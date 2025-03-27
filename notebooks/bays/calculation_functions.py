"""Bays calculation functions."""

import math

import pandas as pd


def calculate_energy_used(
    s: pd.Series,
    avg_kwh_per_m2_per_annum: float = 133,
):
    """Calculate the heating energy used by using the average heating energy
    per square meter per annum.

    Source: https://www.ovoenergy.com/guides/energy-guides/how-much-heating-energy-do-you-use
    """
    return s.total_floor_area * avg_kwh_per_m2_per_annum


def calculate_heating_cost(
    s: pd.Series,
    fuel_prices_df: pd.DataFrame,
):
    """Calculates the Heating cost per annum.

    Source for prices: https://files.bregroup.com/SAP/SAP-2012_9-92.pdf (page 225)
    """
    heating_energy_used = calculate_energy_used(s)
    heating_fuel = s.MainFuelType
    fuel_prices = fuel_prices_df.loc[heating_fuel]
    heating_cost = fuel_prices["standing_cost"] + fuel_prices["unit_price"] * heating_energy_used
    return heating_cost


def calculate_total_energy_cost(
    s: pd.Series,
) -> float:
    """Calculate the total energy cost of the dwelling."""
    total_water_heating_cost = s["WaterHeatingCost(£/yr)"]
    total_lighting_cost = s["LightingCost(£/yr)"]
    total_heating_cost = s["HeatingCost(£/yr)"]
    return total_water_heating_cost + total_lighting_cost + 0.5 * total_heating_cost


def calculate_energy_cost_factor(s: pd.Series, energy_cost_deflator: float = 0.42) -> float:
    """Calculate the energy cost factor to be used in the SAP calculation."""
    total_energy_cost = calculate_total_energy_cost(s)
    total_floor_area = s.total_floor_area
    return (total_energy_cost * energy_cost_deflator) / (total_floor_area + 45.0)


def calculate_sap_score(s: pd.Series) -> int:
    """Calculate the SAP score."""
    energy_cost_factor = calculate_energy_cost_factor(s)
    if energy_cost_factor > 3.4:
        return int(111 - (110 * math.log10(energy_cost_factor)))
    return int(110 - 13.96 * energy_cost_factor)
