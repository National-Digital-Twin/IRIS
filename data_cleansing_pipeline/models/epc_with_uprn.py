import os
import re

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from logging_config import setup_logger

# load credentials from .env
load_dotenv(".env", verbose=True)

DEBUG = os.environ.get("DEBUG", False)

logger = setup_logger(DEBUG)


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

    # Merge in OS (DPA) data for epc_ok
    epc = epc.merge(
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
    epc["fuzzy_matched"] = 0
    epc["address_source"] = "os_dpa"

    # Merge in OS (LPI) data for epc_ok as fallback
    epc = epc.merge(
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
    epc["address_os"] = epc.apply(
        lambda row: (
            row["address_os_dpa"]
            if pd.notna(row["udprn_os_dpa"])
            else row["address_os_lpi"]
        ),
        axis=1,
    )
    epc["postcode_os"] = epc.apply(
        lambda row: (
            row["postcode_os_dpa"]
            if pd.notna(row["udprn_os_dpa"])
            else row["postcode_os_lpi"]
        ),
        axis=1,
    )
    epc["address_source"] = epc.apply(
        lambda row: "os_dpa" if pd.notna(row["udprn_os_dpa"]) else "os_lpi",
        axis=1,
    )
    epc["fuzzy_matched"] = 0

    # Use Ordnance Survey address & postcode going forwards
    epc["address_os"] = epc["address_os"].apply(format_address)
    epc["address_epc"] = epc["address_epc"].apply(format_address)

    epc["address"] = epc.address_os.combine_first(epc.address_epc)
    epc["postcode"] = epc.postcode_os.combine_first(epc.postcode_epc)

    return epc


def model(dbt, fal):
    """dbt-fal model."""

    # get validated EPC data
    epc = dbt.ref("stg_epc_certificates")

    # reduce to rows with a UPRN
    epc["uprn"] = epc["uprn"].apply(lambda x: np.nan if x == "" else x)
    epc_ok = epc[epc["uprn"].notna()].copy()

    logger.info("-" * 50, "EPC (with UPRN) columns and shape", "-" * 50)
    logger.info(epc.columns)
    logger.info(epc.shape)

    # Filter to IoW postcodes only
    epc_ok["district"] = epc_ok.postcode.str.split(" ").str[0]
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
    epc_ok = (
        epc_ok[
            epc_ok.district.isin(isle_of_wight_districts)
            | epc_ok.district.isin(east_riding_districts)
        ]
        .copy()
        .drop(columns=["district"])
    )

    # get OS data
    os = dbt.ref("stg_os_places")
    logger.info("-" * 50, "OS COLUMNS", "-" * 50)
    logger.info(os.columns)
    logger.info(os.shape)
    os["address"] = os["address"].str.lower()
    os["udprn"] = os["udprn"].apply(lambda x: np.nan if x in ["", "N/A"] else x)

    return pipeline(epc=epc_ok, os=os)
