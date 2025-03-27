"""Bays main.py"""

import warnings

import numpy as np
import pandas as pd

from .calculation_functions import (
    calculate_heating_cost,
    calculate_sap_score,
    calculate_total_energy_cost,
)
from .cleaning_functions import clean_address_profiling_df
from .lookup_tables import fuel_prices_df

warnings.filterwarnings("ignore")

seed = 290923
np.random.seed(seed)  # noqa: NPY002


def calculate_sap_scores(df):
    """Entrypoint."""
    df = df.pipe(clean_address_profiling_df)

    df["HeatingCost(£/yr)"] = df.apply(
        calculate_heating_cost,
        fuel_prices_df=fuel_prices_df,
        axis=1,
    )
    df["totalEnergyCost"] = df.apply(calculate_total_energy_cost, axis=1)
    df["SAP Score"] = df.apply(calculate_sap_score, axis=1)


if __name__ == "__main__":
    df = pd.read_csv(
        "s3://bays-rdsap-data/raw_data/address_profiling_2023_09_15_1430.csv",
        low_memory=False,
    )
    calculate_sap_scores(df)
