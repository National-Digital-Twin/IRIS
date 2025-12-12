# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Run from dbt:
    dbt run --select mart_address_base_plus --threads 8

Run from CLI using Typer:
    # `SELECT * FROM stg_os_places` -> `stg_os_places.csv`
    cd ./c477_data_cleansing/
    python ./models/mart_address_base_plus.py \
        ../data/raw/stg_os_places.csv \
        ../data/interim/mart_address_base_plus.csv
"""

import re

import numpy as np
import pandas as pd
import typer
from pyproj import Transformer


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


def convert_coordinates_to_lat_lon(input_df):
    """Convert BNG reference to WGS84."""
    transformer = Transformer.from_crs("epsg:27700", "epsg:4326")

    def get_lat_lon(row):
        return transformer.transform(row["x_coordinate"], row["y_coordinate"])

    coordinates = input_df.apply(get_lat_lon, axis=1)
    input_df["LATITUDE"], input_df["LONGITUDE"] = zip(*coordinates, strict=False)

    return input_df


def add_shares_toid(input_df):
    """Adds boolean `shares_toid` column if the TOID is duplicated."""
    input_df["SharesTOID"] = input_df["TOID"].duplicated(keep=False)

    return input_df


def rename_columns(input_df):
    """Rename columns using mapping."""
    columns_mapping = {
        "uprn": "UPRN",
        "udprn": "UDPRN",
        "address": "ADDRESS",
        "postcode": "POSTCODE_LOCATOR",
        "x_coordinate": "X_COORDINATE",
        "y_coordinate": "Y_COORDINATE",
        "parent_uprn": "PARENT_UPRN",
        "classification_code": "CLASS",
        "classification_code_description": "CLASS_DESCRIPTION",
        "topography_layer_toid": "TOID",
    }
    return input_df.rename(columns=columns_mapping)


def add_blank_columns(input_df):
    """Add blank columns to DataFrame to produce correct output."""
    blank_cols = [
        "WARD_CODE",
        "LSOA11_CODE",
        "COA11_CODE",
        "PARISH_CODE",
        "CONSERVATION_AREA",
        "NATIONAL_PARK",
        "WORLD_HERITAGE_SITE",
        "AONB",
    ]
    for col in blank_cols:
        input_df[col] = np.nan
    return input_df


def reorder_columns(input_df):
    """Reorder DataFrame to specific output required."""
    specified_order_os = [
        "UPRN",
        "UDPRN",
        "TOID",
        "SharesTOID",
        "ADDRESS",
        "POSTCODE_LOCATOR",
        "X_COORDINATE",
        "Y_COORDINATE",
        "LATITUDE",
        "LONGITUDE",
        "PARENT_UPRN",
        "WARD_CODE",
        "LSOA11_CODE",
        "COA11_CODE",
        "PARISH_CODE",
        "CONSERVATION_AREA",
        "NATIONAL_PARK",
        "WORLD_HERITAGE_SITE",
        "AONB",
        "CLASS",
        "CLASS_DESCRIPTION",
        "os_api_source",
    ]
    return input_df[specified_order_os]


def final_rename_columns(input_df):
    """Rename DataFrame to specific output required."""
    return input_df.rename(
        columns={
            "ADDRESS": "Address",
            "POSTCODE_LOCATOR": "PostcodeLocator",
            "X_COORDINATE": "XCoordinate",
            "Y_COORDINATE": "YCoordinate",
            "LATITUDE": "Latitude",
            "LONGITUDE": "Longitude",
            "PARENT_UPRN": "ParentUPRN",
            "WARD_CODE": "WardCode",
            "LSOA11_CODE": "LSOA11Code",
            "COA11_CODE": "COA11Code",
            "PARISH_CODE": "ParishCode",
            "CONSERVATION_AREA": "ConservationArea",
            "NATIONAL_PARK": "NationalPark",
            "WORLD_HERITAGE_SITE": "WorldHeritageSite",
            "CLASS": "Class",
            "CLASS_DESCRIPTION": "ClassDescription",
            "os_api_source": "OSAPISource",
        },
    )


def pipeline(df):
    """Cleanse and prepare raw data for address base plus dataset."""
    df = (
        df.pipe(convert_coordinates_to_lat_lon)
        .pipe(rename_columns)
        .pipe(add_shares_toid)
        .pipe(add_blank_columns)
        .pipe(reorder_columns)
        .pipe(final_rename_columns)
        .drop_duplicates()
    )
    df["Address"] = df["Address"].apply(format_address)

    # Filter to IoW postcodes only
    df["district"] = df.PostcodeLocator.str.split(" ").str[0]
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
    df = (
        df[df.district.isin(isle_of_wight_districts) | df.district.isin(east_riding_districts)]
        .copy()
        .drop(columns=["district"])
    )

    return df


def model(dbt, fal):
    """dbt-fal model."""
    return dbt.ref("stg_os_places").query("os_api_source == 'DPA'").pipe(pipeline)


def main(input_csv: str, output_csv: str, to_excel: bool):
    """Process input CSV and save cleansed CSV file."""
    df = (
        pd.read_csv(input_csv, low_memory=False, dtype={"UPRN": str, "ParentUPRN": str})
        .query("os_api_source == 'DPA'")
        .pipe(pipeline)
    )
    if to_excel:
        df["UPRN"] = df["UPRN"].astype(float).astype("int64")
        df["ParentUPRN"] = df["ParentUPRN"].astype(float).astype("int64")
        with pd.ExcelWriter(output_csv) as writer:  # pylint: disable=abstract-class-instantiated
            df.to_excel(writer, index=False)
    else:
        df.to_csv(output_csv, index=False)
        typer.echo(f"File saved to {output_csv}")


if __name__ == "__main__":
    typer.run(main)
