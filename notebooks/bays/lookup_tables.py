"""Bays lookup tables."""

import pandas as pd

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
