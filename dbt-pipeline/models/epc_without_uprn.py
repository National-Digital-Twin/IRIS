import os

import fuzzymatcher
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pandarallel import pandarallel
from rapidfuzz import fuzz, process
from tqdm import tqdm

from data_cleansing_pipeline.logging_config import setup_logger

# load credentials from .env
load_dotenv(".env", verbose=True)

DEBUG = os.environ.get("DEBUG", False)

logger = setup_logger(DEBUG)
pandarallel.initialize(progress_bar=True)
tqdm.pandas()


def pipeline(epc: pd.DataFrame, os: pd.DataFrame) -> pd.DataFrame:
    """Cleanse and prepare raw data for address base plus dataset."""

    # Fuzzy match where epc is missing UPRN
    epc["address_postcode"] = epc.apply(
        lambda row: f"{row.address}, {row.posttown.title()}, {row.postcode}".lower(),
        axis=1,
    )
    epc["partial_postcode"] = epc.postcode.apply(
        lambda s: f"{s.split(' ')[0]} {s.split(' ')[1][:2]}",
    )

    def match_address(address, partial_postcode):
        """Function to get the closest match and its UPRN based on the address and postcode."""
        addresses_in_district = os[os.postcode.str.contains(partial_postcode)].address.str.lower()
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
    epc["matched_address"] = epc.progress_apply(
        lambda row: match_address(
            address=row["address_postcode"],
            partial_postcode=row["partial_postcode"],
        ),
        axis=1,
    )

    epc = (
        epc.merge(
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
    epc["fuzzy_matched"] = 1
    epc["address_source"] = "os_fuzzy"

    return epc


def model(dbt, fal):
    """dbt-fal model."""

    # get validated EPC data
    epc = dbt.ref("stg_epc_certificates")

    # reduce to rows without a UPRN
    epc["uprn"] = epc["uprn"].apply(lambda x: np.nan if x == "" else x)
    epc_na = epc[epc["uprn"].isna()].copy()

    logger.info("-" * 50, "EPC (without UPRN) columns and shape", "-" * 50)
    logger.info(epc_na.columns)
    logger.info(epc_na.shape)

    # Filter to IoW postcodes only
    epc_na["district"] = epc_na.postcode.str.split(" ").str[0]
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
    epc_na = (
        epc_na[
            epc_na.district.isin(isle_of_wight_districts)
            | epc_na.district.isin(east_riding_districts)
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

    return pipeline(epc=epc_na, os=os)
