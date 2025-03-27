# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Run from dbt:
    dbt run --select mart_address_profiling_with_sap --threads 8

Run from CLI using Typer:
    # `SELECT * FROM mart_address_profiling` -> `mart_address_profiling.csv`
    cd ./c477_data_cleansing/
    python ./models/mart_address_profiling_with_sap.py \
        ../data/interim/mart_address_profiling.csv \
        ../data/interim/mart_address_profiling_with_sap.csv
"""

import math

import numpy as np
import pandas as pd
import typer

seed = 290923
np.random.seed(seed)  # noqa: NPY002

###############
# LOOKUP TABLES
###############

fuel_prices_df = pd.DataFrame(
    {
        "standing_cost": {
            "MainsGas": 120.0,
            "Electricity": 54.0,
            "Oil": 0.0,
            "LPG": 70.0,
            "DualFuel": 0.0,
            "WoodLogs": 0.0,
            "Coal": 0.0,
            "Biomass": 0.0,
            "Anthracite": 0.0,
            "SmokelessCoal": 0.0,
            "WoodPellets": 0.0,
            "WoodChips": 0.0,
            "Biogas": 70.0,
            "Other": 0.0,
        },
        "unit_price": {
            "MainsGas": 0.0348,
            "Electricity": 0.1319,
            "Oil": 0.0544,
            "LPG": 0.076,
            "DualFuel": 0.0399,
            "WoodLogs": 0.0423,
            "Coal": 0.0367,
            "Biomass": 0.47,
            "Anthracite": 0.0364,
            "SmokelessCoal": 0.0367,
            "WoodPellets": 0.0526,
            "WoodChips": 0.0307,
            "Biogas": 0.076,
            "Other": 0.025,
        },
    },
)

#######################
# CALCULATION FUNCTIONS
#######################


def calculate_energy_used(
    row: pd.Series,
    avg_kwh_per_m2_per_annum: float = 133,
):
    """Calculate the heating energy used by using the average heating energy
    per square meter per annum.

    Source: https://www.ovoenergy.com/guides/energy-guides/how-much-heating-energy-do-you-use
    """
    return row.TotalFloorArea * avg_kwh_per_m2_per_annum


def calculate_heating_cost(
    row: pd.Series,
    fuel_prices_df: pd.DataFrame,
):
    """Calculates the Heating cost per annum.

    Source for prices: https://files.bregroup.com/SAP/SAP-2012_9-92.pdf (page 225)
    """
    heating_energy_used = calculate_energy_used(row)
    heating_fuel = row.MainFuelType
    fuel_prices = fuel_prices_df.loc[heating_fuel]
    heating_cost = fuel_prices["standing_cost"] + fuel_prices["unit_price"] * heating_energy_used
    return heating_cost


def calculate_total_energy_cost(
    row: pd.Series,
) -> float:
    """Calculate the total energy cost of the dwelling."""
    total_water_heating_cost = row["WaterHeatingCost(£/yr)"]
    total_lighting_cost = row["LightingCost(£/yr)"]
    total_heating_cost = row["HeatingCost(£/yr)"]
    return total_water_heating_cost + total_lighting_cost + 0.5 * total_heating_cost


def calculate_energy_cost_factor(row: pd.Series, energy_cost_deflator: float = 0.42) -> float:
    """Calculate the energy cost factor to be used in the SAP calculation."""
    total_energy_cost = calculate_total_energy_cost(row)
    total_floor_area = row.TotalFloorArea
    return (total_energy_cost * energy_cost_deflator) / (total_floor_area + 45.0)


def sap_score(row: pd.Series) -> int:
    """Calculate the SAP score."""
    for col in ["TotalFloorArea", "WaterHeatingCost(£/yr)", "LightingCost(£/yr)"]:
        if pd.isna(row[col]):
            return np.nan

    energy_cost_factor = calculate_energy_cost_factor(row)
    if energy_cost_factor > 3.4:
        return int(111 - (110 * math.log10(energy_cost_factor)))
    return int(110 - 13.96 * energy_cost_factor)


####################
# CLEANING FUNCTIONS
####################


def clean_address_profiling_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean address profiling df."""
    df = df.drop(columns="HeatingCost(£/yr)")

    # Clean 'MainFuelType'
    df.loc[df.MainFuelType.isna(), "MainFuelType"] = "Other"
    for fuel_type in ["NoSystem", "Invalid"]:
        fuel_filter = df.MainFuelType == fuel_type
        df.loc[fuel_filter, "MainFuelType"] = "Other"

    return df


######
# MAIN
######


def calculate_sap_scores(df):
    """Bays' SAP score calculations."""

    df = df.pipe(clean_address_profiling_df)

    df["HeatingCost(£/yr)"] = df.apply(
        calculate_heating_cost,
        fuel_prices_df=fuel_prices_df,
        axis=1,
    )
    df["totalEnergyCost"] = df.apply(calculate_total_energy_cost, axis=1)
    df["SAPScore"] = df.apply(sap_score, axis=1)

    return df


def model(dbt, fal):
    """dbt-fal model."""
    return dbt.ref("mart_address_profiling").pipe(calculate_sap_scores)


def main(input_csv: str, output_csv: str, to_excel: bool = False):
    """Process input CSV and save cleansed CSV file."""
    df = pd.read_csv(input_csv, low_memory=False, dtype={"uprn": str, "lmk_key": str}).pipe(
        calculate_sap_scores,
    )
    if to_excel:
        # Save to XLSX
        df = df.dropna(subset=["UPRN"])
        df["UPRN"] = df["UPRN"].astype(float).astype("int64")
        df.to_excel(output_csv.replace(".csv", ".xlsx"), index=False, engine="openpyxl")
    else:
        # Save to CSV
        df.to_csv(output_csv, index=False)
    typer.echo(f"File saved to {output_csv}")


if __name__ == "__main__":
    typer.run(main)
