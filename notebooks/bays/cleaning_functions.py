"""Bays cleaning functions."""

import pandas as pd


def clean_address_profiling_df(address_profiling_df: pd.DataFrame) -> pd.DataFrame:
    """Clean address profiling df."""
    address_profiling_df = address_profiling_df.drop(columns="HeatingCost(£/yr)")

    # Clean 'MainFuelType'
    address_profiling_df.loc[address_profiling_df.MainFuelType.isna(), "MainFuelType"] = "Other"
    for fuel_type in ["NoSystem", "Invalid"]:
        fuel_filter = address_profiling_df.MainFuelType == fuel_type
        address_profiling_df.loc[fuel_filter, "MainFuelType"] = "Other"

    return address_profiling_df
