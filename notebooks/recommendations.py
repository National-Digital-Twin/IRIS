"""
Run from CLI using Typer:
    python ./notebooks/recommendations.py
"""

import os
from io import BytesIO
from time import sleep
from zipfile import ZipFile

import pandas as pd
import requests
import typer
import yaml
from joblib import Memory
from requests.adapters import HTTPAdapter, Retry
from sqlalchemy import create_engine
from tqdm import tqdm

BASE_URL = "https://epc.opendatacommunities.org/api/v1/domestic/search?local-authority=E06000046"
DESTINATION_TABLE = "recommendations"

HEADERS = {
    "Accept": "application/zip",
    "Authorization": (
        "Basic INSERT_YOUR_EPC_API_KEY_HERE"
    ),
}
MAX_PAGE_SIZE = 1000  # Reduced page size
REQUEST_TIMEOUT = 500
REQUEST_SLEEP = 0.5
START_YEAR = 2008
END_YEAR = 2023
CACHE_DIR = ".cache"
memory = Memory(CACHE_DIR, verbose=0)

# Load config from ~/.dbt/profiles.yml
with open(os.path.expanduser("~/.dbt/profiles.yml"), encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)
DB_CONFIG = CONFIG["c477_data_cleansing"]["outputs"]["dev_postgres"]


@memory.cache
def requests_cached(params):
    """Wrapper for caching requests."""
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))

    response = s.get(BASE_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    sleep(REQUEST_SLEEP)

    if response.status_code == 500:
        raise RuntimeError(f"Encountered error 500 for {params=}")

    elif response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zf:
            if "recommendations.csv" in zf.namelist():
                with zf.open("recommendations.csv") as myfile:
                    df = pd.read_csv(myfile)
                    return df
            else:
                return None

    else:
        raise RuntimeError(f"Encountered error {response.status_code} for {params=}")


@memory.cache
def fetch_recommendations_for_segment(year, month, energy_band):
    """Fetch recs."""
    from_param = 0
    df_list = [pd.DataFrame()]
    while True:
        params = {
            "size": MAX_PAGE_SIZE,
            "from": from_param,
            "from-year": year,
            "to-year": year,
            "from-month": month,
            "to-month": month,
            "energy-band": energy_band,
        }
        df = requests_cached(params=params)

        if df is None:
            break
        else:
            df_list.append(df)

        # If we fetched less than the maximum page size, we've reached the end.
        if df.shape[0] < MAX_PAGE_SIZE:
            break
        else:
            from_param += MAX_PAGE_SIZE

    return pd.concat(df_list, axis=0, ignore_index=True)


def main():
    """Main recommendations pipeline runner."""
    df_list = []
    for year in tqdm(list(range(START_YEAR, END_YEAR + 1))):
        for month in list(range(1, 13)):
            typer.echo(f"Getting data for {year}-{month}")
            for energy_band in "abcdefg":
                segment_df = fetch_recommendations_for_segment(year, month, energy_band)
                df_list.append(segment_df)

    recommendations = (
        pd.concat(df_list, axis=0, ignore_index=True)
        .drop_duplicates()
        .reset_index(drop=True)
        .sort_values(["LMK_KEY", "IMPROVEMENT_ITEM"], ascending=True)
    )

    typer.echo(f"{len(recommendations)} rows API'd ✨")

    # Create an engine instance
    conn_string = (
        "postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}"
        f":{DB_CONFIG['port']}"
        f"/{DB_CONFIG['dbname']}"
    )
    engine = create_engine(conn_string, pool_recycle=3600)
    with engine.begin() as connection:
        recommendations.to_sql(
            name=DESTINATION_TABLE,
            con=connection,
            index=False,
            if_exists="replace",
            chunksize=1000,
        )

    typer.echo(f"{len(recommendations)} rows uploaded to {DESTINATION_TABLE} ✨")


if __name__ == "__main__":
    typer.run(main)
