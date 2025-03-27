# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Run from dbt:
    dbt run --select mart_reduced_co2_measures --threads 8

Run from CLI using Typer:
    # `SELECT * FROM int_os_epc` -> `int_os_epc.csv`
    cd ./c477_data_cleansing/
    python ./models/mart_reduced_co2_measures.py \
        ../data/raw/int_os_epc.csv \
        ../data/interim/mart_reduced_co2_measures.csv
"""

import re

import numpy as np
import pandas as pd
import typer


def replace_invalid_values(value):
    """Remove invalid values."""
    invalid_values = ["unknown", "no data!", "nodata!", "nan", "n/a"]
    if str(value).lower() in invalid_values:
        return np.nan
    return value


def format_address(input_str: str) -> str:
    """Format address like
        123 main street, cowes, po33 1ab
    into
        123 Main Street, Cowes, PO33 1AB
    """
    # Check if null
    if pd.isna(input_str):
        return np.nan

    # Convert rest of the string to title case
    input_str = input_str.title()

    # This regex matches many UK postcodes
    postcode_pattern = r"(?:[a-zA-Z]{1,2}[0-9][a-zA-Z0-9]? ?[0-9][a-zA-Z]{2}|GIR ?0AA)"

    # Function to uppercase the matched postcode
    def to_upper(match):
        return match.group(0).upper()

    # Replace the postcode with its uppercase version
    formatted_str = re.sub(postcode_pattern, to_upper, input_str, flags=re.IGNORECASE)

    return formatted_str


def cleanse_data(df):
    """Perform default cleansing on raw data."""
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    for col in df.columns:
        df[col] = df[col].map(replace_invalid_values)

    df["uprn"] = df["uprn"].astype(str)
    df["uprn"] = df["uprn"].str.strip().replace("nan", np.nan)

    df["udprn"] = df["udprn"].astype(str)
    df["udprn"] = df["udprn"].str.strip().replace("nan", np.nan)

    df = df.rename(columns={"uprn": "UPRN", "udprn": "UDPRN"})

    return df


def pipeline(df):
    """Cleanse and prepare staging data for C02 measures dataset."""
    df = (
        df.pipe(cleanse_data)
        .sort_values(["UPRN", "ImprovementIndex"], ascending=[False, True])
        .drop_duplicates()
    )
    df["Address"] = df["Address"].apply(format_address)

    return df


def model(dbt, fal):
    """dbt-fal model."""
    return dbt.ref("int_os_epc").pipe(pipeline)


def main(input_csv: str, output_csv: str, to_excel: bool):
    """Process input CSV and save cleansed CSV file.

    Run from dbt:
        dbt run --select mart_reduced_co2_measures --threads 8

    Run from CLI using Typer:
        # `SELECT * FROM int_os_epc` -> `int_os_epc.csv`
        cd ./c477_data_cleansing/
        python ./models/mart_reduced_co2_measures.py \
            ../data/raw/int_os_epc.csv \
            ../data/interim/mart_reduced_co2_measures.csv

    """
    if to_excel:
        col_types = {"UPRN": str, "ParentUPRN": str}
        df = pd.read_csv(input_csv, dtype=col_types).pipe(pipeline)
        df["UPRN"] = df["UPRN"].astype(float).astype("int64")
        df["ParentUPRN"] = df["ParentUPRN"].astype(float).astype("int64")
        with pd.ExcelWriter(output_csv) as writer:  # pylint: disable=abstract-class-instantiated
            df.to_excel(writer, index=False)
    else:
        pd.read_csv(input_csv, low_memory=False).pipe(pipeline).to_csv(output_csv, index=False)
        typer.echo(f"File saved to {output_csv}")


if __name__ == "__main__":
    typer.run(main)
