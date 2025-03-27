"""
Run from CLI using Typer:
    python utils.py --help
    python utils.py
"""

import logging
from io import BytesIO
from time import sleep
from zipfile import ZipFile

import pandas as pd
import requests
import typer
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://epc.opendatacommunities.org/api/v1/domestic/search"
DESTINATION_TABLE = "recommendations"

MAX_PAGE_SIZE = 1000  # Reduced page size
REQUEST_TIMEOUT = 500
REQUEST_SLEEP = 0.5
LOCAL_AUTHORITY_LIST = [
    "E06000046",  # Isle of Wight
    "E06000011",  # East Riding of Yorkshire
]
START_YEAR = 2008
END_YEAR = 2024
CACHE_DIR = ".cache"


def requests_cached(params, logger, auth_key=None):
    """Wrapper for caching requests."""
    if not auth_key:
        auth_key = (
            # pragma: allowlist nextline secret
            "Basic INSERT_YOUR_EPC_API_KEY_HERE"
        )

    headers = {
        "Accept": "application/zip",
        "Authorization": auth_key,
    }

    s = requests.Session()
    retries = Retry(
        total=10,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))

    response = s.get(BASE_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    sleep(REQUEST_SLEEP)

    if response.status_code == 500:
        message = f"Encountered error 500 for {params=}"
        logger.error(message)
        raise RuntimeError(message)

    elif response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zf:
            if "recommendations.csv" in zf.namelist():
                with zf.open("recommendations.csv") as myfile:
                    df = pd.read_csv(myfile)
                    return df
            else:
                return None

    else:
        message = f"Encountered error {response.status_code} for {params=}"
        logger.error(message)
        raise RuntimeError(message)


def fetch_recommendations_for_segment(
    local_authority,
    year,
    month,
    energy_band,
    logger,
    auth_key=None,
):
    """Fetch recs."""
    from_param = 0
    df_list = [pd.DataFrame()]
    while True:
        params = {
            "local-authority": local_authority,
            "size": MAX_PAGE_SIZE,
            "from": from_param,
            "from-year": year,
            "to-year": year,
            "from-month": month,
            "to-month": month,
            "energy-band": energy_band,
        }
        df = requests_cached(params=params, logger=logger, auth_key=auth_key)

        if df is None:
            break
        else:
            df_list.append(df)

        # If we fetched less than the maximum page size, we've reached the end.
        if df.shape[0] < MAX_PAGE_SIZE:
            break
        else:
            from_param += MAX_PAGE_SIZE
            if from_param >= 10000:
                logger.warning(
                    f"Reached 10000 records for {year}-{month} band {energy_band}",
                )

    return pd.concat(df_list, axis=0, ignore_index=True)


def main(
    local_authority_list: list[str] = LOCAL_AUTHORITY_LIST,
    start_year: int = START_YEAR,
    end_year: int = END_YEAR,
    auth_key: str = None,
    logger=None,
) -> pd.DataFrame:
    """Main recommendations pipeline runner."""
    if not logger:
        logger = logging.getLogger("airbyte")

    df_list = []
    for local_authority in local_authority_list:
        for year in list(range(start_year, end_year + 1)):
            for month in list(range(1, 13)):
                logger.info(
                    f"Getting data for {year}-{month} for local authority {local_authority}",
                )
                for energy_band in "abcdefg":
                    segment_df = fetch_recommendations_for_segment(
                        local_authority,
                        year,
                        month,
                        energy_band,
                        logger,
                        auth_key,
                    )
                    df_list.append(segment_df)

    recommendations = (
        pd.concat(df_list, axis=0, ignore_index=True)
        .drop_duplicates()
        .reset_index(drop=True)
        .sort_values(["LMK_KEY", "IMPROVEMENT_ITEM"], ascending=True)
    )

    logger.info(f"{len(recommendations)} rows retrieved from the EPC API ✨")

    return recommendations


if __name__ == "__main__":
    typer.run(main)
