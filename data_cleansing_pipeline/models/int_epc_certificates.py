# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Run from dbt:
    dbt run --select int_epc_certificates --threads 8

Run from CLI using Typer:
    # `SELECT * FROM stg_epc_certificates` -> `stg_epc_certificates.csv`
    # `SELECT * FROM stg_os_places` -> `stg_os_places.csv`
    cd ./c477_data_cleansing/
    python ./models/int_epc_certificates.py \
        ../data/raw/stg_epc_certificates.csv \
        ../data/raw/stg_os_places.csv \
        ../data/interim/int_epc_certificates.csv
"""

# logger
import os
import re

import fuzzymatcher
import numpy as np
import pandas as pd
import typer
from dotenv import load_dotenv
from logging_config import setup_logger
from pandarallel import pandarallel
from rapidfuzz import fuzz, process
from tqdm import tqdm

# load credentials from .env
load_dotenv(".env", verbose=True)

DEBUG = os.environ.get("DEBUG", False)


logger = setup_logger(DEBUG)
pandarallel.initialize(progress_bar=True)
tqdm.pandas()


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


def pipeline(epc: pd.DataFrame, os: pd.DataFrame) -> pd.DataFrame:
    """Cleanse and prepare raw data for address base plus dataset."""
    epc_ok = epc[epc["uprn"].notna()].copy()
    epc_na = epc[epc["uprn"].isna()].copy()

    # Fuzzy match where epc is missing UPRN
    epc_na["address_postcode"] = epc_na.apply(
        lambda row: f"{row.address}, {row.posttown.title()}, {row.postcode}".lower(),
        axis=1,
    )
    epc_na["partial_postcode"] = epc_na.postcode.apply(
        lambda s: f"{s.split(' ')[0]} {s.split(' ')[1][:2]}",
    )

    def match_address(address, partial_postcode):
        """Function to get the closest match and its UPRN based on the address and postcode."""
        addresses_in_district = os[
            os.postcode.str.contains(partial_postcode)
        ].address.str.lower()
        if len(addresses_in_district) < 10:
            addresses_in_district = os[
                os.postcode.str.contains(partial_postcode.split(" ")[0])
            ].address.str.lower()

        choices = [
            c[0]
            for c in process.extract(
                address,
                addresses_in_district.tolist(),
                scorer=fuzz.WRatio,
                limit=500,
            )
        ]

        df_left = pd.DataFrame({"address": [address]})
        df_right = pd.DataFrame({"address": choices})

        df_both = fuzzymatcher.fuzzy_left_join(
            df_left,
            df_right,
            left_on="address",
            right_on="address",
        )
        matched_address = df_both.address_right[0]

        return matched_address

    # Change to .parallel_apply() for speed
    epc_na["matched_address"] = epc_na.progress_apply(
        lambda row: match_address(
            address=row["address_postcode"],
            partial_postcode=row["partial_postcode"],
        ),
        axis=1,
    )

    epc_na = (
        epc_na.merge(
            os[["address", "uprn", "udprn", "postcode"]],
            left_on="matched_address",
            right_on="address",
            how="left",
        )
        .drop(columns=["uprn_x", "address_y", "address_x", "partial_postcode"])
        .rename(
            columns={
                "uprn_y": "uprn",
                "matched_address": "address_os",
                "address_postcode": "address_epc",
                "postcode_x": "postcode_epc",
                "postcode_y": "postcode_os",
            },
        )
    )
    epc_na["fuzzy_matched"] = 1
    epc_na["address_source"] = "os_fuzzy"

    # Merge in OS (DPA) data for epc_ok
    epc_ok = epc_ok.merge(
        os.query('os_api_source == "DPA"')[["uprn", "udprn", "address", "postcode"]],
        on="uprn",
        how="left",
    ).rename(
        columns={
            "address_x": "address_epc",
            "address_y": "address_os_dpa",
            "postcode_x": "postcode_epc",
            "postcode_y": "postcode_os_dpa",
            "udprn": "udprn_os_dpa",
        },
    )
    epc_ok["fuzzy_matched"] = 0
    epc_ok["address_source"] = "os_dpa"

    # Merge in OS (LPI) data for epc_ok as fallback
    epc_ok = epc_ok.merge(
        os.query('os_api_source == "LPI"')[
            ["uprn", "udprn", "address", "postcode"]
        ].rename(
            columns={
                "udprn": "udprn_os_lpi",
                "address": "address_os_lpi",
                "postcode": "postcode_os_lpi",
            },
        ),
        on="uprn",
        how="left",
    )

    # If udprn_os_dpa is not null, use DPA data for udprn/address/postcode
    epc_ok["address_os"] = epc_ok.apply(
        lambda row: (
            row["address_os_dpa"]
            if pd.notna(row["udprn_os_dpa"])
            else row["address_os_lpi"]
        ),
        axis=1,
    )
    epc_ok["postcode_os"] = epc_ok.apply(
        lambda row: (
            row["postcode_os_dpa"]
            if pd.notna(row["udprn_os_dpa"])
            else row["postcode_os_lpi"]
        ),
        axis=1,
    )
    epc_ok["address_source"] = epc_ok.apply(
        lambda row: "os_dpa" if pd.notna(row["udprn_os_dpa"]) else "os_lpi",
        axis=1,
    )
    epc_ok["fuzzy_matched"] = 0

    # Combine back together again
    epc_df = pd.concat([epc_ok, epc_na], axis=0).sort_values("uprn")

    # Use Ordnance Survey address & postcode going forwards
    epc_df["address_os"] = epc_df["address_os"].apply(format_address)
    epc_df["address_epc"] = epc_df["address_epc"].apply(format_address)

    epc_df["address"] = epc_df.address_os.combine_first(epc_df.address_epc)
    epc_df["postcode"] = epc_df.postcode_os.combine_first(epc_df.postcode_epc)

    return epc_df


def model(dbt, fal):
    """dbt-fal model."""

    # get validated EPC data
    epc = dbt.ref("stg_epc_certificates")
    logger.info("-" * 50, "EPC COLUMNS", "-" * 50)
    logger.info(epc.columns)
    logger.info(epc.shape)
    epc["uprn"] = epc["uprn"].apply(lambda x: np.nan if x == "" else x)

    # Filter to IoW postcodes only
    epc["district"] = epc.postcode.str.split(" ").str[0]
    isle_of_wight_districts = [
        "PO30",
        "PO31",
        "PO32",
        "PO33",
        "PO34",
        "PO35",
        "PO36",
        "PO37",
        "PO38",
        "PO39",
        "PO40",
        "PO41",
    ]
    east_riding_districts = [
        "DN8",
        "DN14",
        "HU2",
        "HU4",
        "HU5",
        "HU6",
        "HU7",
        "HU8",
        "HU10",
        "HU11",
        "HU12",
        "HU13",
        "HU14",
        "HU15",
        "HU16",
        "HU17",
        "HU18",
        "HU19",
        "HU20",
        "YO4",
        "YO8",
        "YO11",
        "YO15",
        "YO16",
        "YO25",
        "YO41",
        "YO42",
        "YO43",
        "YO95",
    ]
    epc = (
        epc[
            epc.district.isin(isle_of_wight_districts)
            | epc.district.isin(east_riding_districts)
        ]
        .copy()
        .drop(columns=["district"])
    )

    os = dbt.ref("stg_os_places")
    logger.info("-" * 50, "OS COLUMNS", "-" * 50)
    logger.info(os.columns)
    logger.info(os.shape)
    os["address"] = os["address"].str.lower()
    os["udprn"] = os["udprn"].apply(lambda x: np.nan if x in ["", "N/A"] else x)

    return pipeline(epc=epc, os=os)


def main(epc_file: str, os_file: str, output_csv: str):
    """Process input CSV and save cleansed CSV file."""
    epc = pd.read_csv(
        epc_file,
        low_memory=False,
        dtype={"UPRN": str, "ParentUPRN": str},
    )
    os = pd.read_csv(os_file, low_memory=False, dtype={"UPRN": str, "ParentUPRN": str})
    os["address"] = os["address"].str.lower()
    os["udprn"] = os["udprn"].apply(lambda x: np.nan if x in ["", "N/A"] else x)

    df = pipeline(epc=epc, os=os)
    df.to_csv(output_csv, index=False)
    typer.echo(f"File saved to {output_csv}")


if __name__ == "__main__":
    typer.run(main)
