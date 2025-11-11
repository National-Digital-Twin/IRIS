# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

"""
Run from dbt:
    dbt run --select mart_address_profiling --threads 8

Run from CLI using Typer:
    # `SELECT * FROM int_epc_certificates` -> `int_epc_certificates.csv`
    cd ./c477_data_cleansing/
    python ./models/mart_address_profiling.py \
        ../data/raw/int_epc_certificates.csv \
        ../data/interim/mart_address_profiling.csv
"""

import re

import numpy as np
import pandas as pd
import typer


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


def split_columns(df):
    """Split roof, wall and floor information into separate columns."""
    for col in ["roof_description", "walls_description", "floor_description"]:
        split_cols = df[col].str.split(",", expand=True)
        df[f"{col}_1"] = split_cols.get(0)
        df[f"{col}_2"] = split_cols.get(1)
        if 2 in split_cols:
            df[f"{col}_3"] = split_cols[2]
    return df


def replace_invalid_values(value):
    """Replace invalid values with np.nan."""
    invalid_values = ["unknown", "no data!", "nodata!", "nan", "n/a"]
    if str(value).lower() in invalid_values:
        return np.nan
    return value


def cleanse_data(df):
    """Perform default cleansing on raw data."""
    for col in [
        "address",
        "property_type",
        "roof_description_1",
        "mechanical_ventilation",
    ]:
        df[col] = df[col].str.title()
    df["address"] = df["address"].apply(format_address)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    for col in df.columns:
        df[col] = df[col].apply(replace_invalid_values)

    df["uprn"] = df["uprn"].astype(str).str.strip().replace("nan", "")

    return df


def to_pascal_case(value):
    """Transform a string to PascalCase."""
    if pd.isna(value):
        return np.nan
    return "".join(word.capitalize() for word in value.split())


def transform_roof_construction(value):
    """Transform the RoofConstruction values."""
    # List of accepted roof constructions
    accepted_roof_constructions = [
        "Pitched",
        "(Another Dwelling Above)",
        "Flat",
        "Roof Room(S)",
        "(Other Premises Above)",
        "Thatched",
    ]

    if value in accepted_roof_constructions:
        clean_value = "".join(e for e in value if e.isalnum() or e.isspace())
        return to_pascal_case(clean_value)
    return np.nan


def transform_roof_insulation_location(value):
    """Transform RoofInsulationLocation values."""
    # Handle None values and float values
    if value is None or isinstance(value, float):
        return np.nan

    # List of values to set to "Other"
    values_to_replace_with_other = [
        "",
        "*** INVALID INPUT Code : 57 *** loft insulation",
        "insulated  (assumed)",
        "Unknown loft insulation",
    ]

    if value in values_to_replace_with_other:
        return "Other"

    # Cast the value to string
    value_str = str(value)

    # Remove any non-alphanumeric characters and then convert to PascalCase
    clean_value = "".join(e for e in value_str if e.isalnum() or e.isspace())
    pascal_case_value = to_pascal_case(clean_value)

    # Specific replacements as per your request
    if pascal_case_value == "MmLoftInsulation":
        return "LoftInsulation"
    if pascal_case_value in ["Insulation", "WithAdditionalInsulation"]:
        return "Insulated"

    return pascal_case_value


def clean_roof_insulation_thickness(value):
    """Clean roof insulation thickness values."""
    # Convert to string in case there are any non-string entries
    value_str = str(value)

    # Remove any non-numeric characters except the '+' sign
    cleaned_value = "".join(e for e in value_str if e.isnumeric() or e in ["+", " "])

    # Replace double "mm" with a single "mm" and "mm mm" with "0mm"
    if "mm mm" in cleaned_value:
        cleaned_value = "0mm"
    else:
        cleaned_value = cleaned_value.replace(" mm", "mm").replace("mm mm", "mm")

    # Handle other cases like removing trailing spaces
    cleaned_value = cleaned_value.strip()

    # Append "mm" if the cleaned value is numeric
    if cleaned_value.isdigit():
        cleaned_value += "mm"

    # Append "mm" if cleaned value ends with "+"
    if cleaned_value.endswith("+"):
        cleaned_value += "mm"

    return cleaned_value


def transform_wall_construction(value):
    """Clean wall construction values."""
    if pd.isna(value):
        return "Other"

    # Remove leading and trailing whitespace and trailing commas
    value = value.strip().rstrip(",")

    # Convert to lowercase for case-insensitive matching
    value = str(value).lower()

    # Define mappings for specific cases
    wall_construction_mappings = {
        "cavity wall": "CavityWall",
        "timber frame": "TimberFrame",
        "solid brick": "SolidBrick",
        "sandstone": "Sandstone",
        "sandstone or limestone": "SandstoneOrLimestone",
        "granite or whin": "GraniteOrWhinstone",
        "park home wall": "ParkHomeWall",
        "cob": "Cob",
        "system built": "SystemBuilt",
    }

    # Check if the lowercase value contains any of the keys in the mappings,
    # otherwise set to 'Other'
    for key, mapped_value in wall_construction_mappings.items():
        if key in value:
            return mapped_value

    return "Other"


def transform_wall_insulation_type(input_string):
    """Clean wall insulation type value."""
    if input_string is None:
        return np.nan
    input_string = str(input_string).lower()

    # Mapping of terms to their corresponding values
    term_mapping = {
        "as built": "AsBuilt",
        "filled cavity and internal insulation": "FilledCavityAndInternalInsulation",
        "filled cavity and external insulation": "FilledCavityAndExternalInsulation",
        "filled cavity": "FilledCavity",
        "internal insulation": "WithInternalInsulation",
        "external insulation": "WithExternalInsulation",
        "additional insulation": "WithAdditionalInsulation",
    }

    for substring, mapped_value in term_mapping.items():
        if substring in input_string:
            return mapped_value

    return np.nan


def transform_wall_insulation_thickness(value):
    """Clean WallInsulationThickness values."""
    return np.nan


def transform_floor_construction(value):
    """Clean floor construction values."""
    if pd.isna(value):
        return np.nan

    valid_values = [
        "Solid",
        "Suspended",
        "(other premises below)",
        "(another dwelling below)",
    ]
    replacements = {
        "(another dwelling below)": "AnotherDwellingBelow",
        "(other premises below)": "OtherPremisesBelow",
    }

    # Replace specific cases
    if value in replacements:
        return replacements[value]

    # Convert non-valid values to 'Other'
    if value not in valid_values:
        return "Other"

    # Convert to PascalCase
    return to_pascal_case(value)


def transform_floor_insulation(value):
    """Clean FloorInsulation values."""
    if pd.isna(value):
        return np.nan

    # Remove (assumed) from the string
    value = value.replace("(assumed)", "").strip()

    # Convert to PascalCase
    value = to_pascal_case(value)

    # Change Uninsulated to NoInsulation
    if value == "Uninsulated":
        return "NoInsulation"

    return value


def transform_floor_insulation_thickness(value):
    """Clean FloorInsulationThickness values."""
    if not value:
        return np.nan
    return value


def map_heating_category(value):
    """Enumerate heating category values."""
    if pd.isna(value):
        return np.nan

    result = "Other"  # default value

    # Mapping categories to values
    category_map = {
        ("Boiler and radiators, mains gas",): "BoilerRadiatorsMainsGas",
        ("Electric storage heaters", "Portable electric heaters"): "ElectricHeaters",
        (
            "Boiler and radiators, LPG",
            "Boiler and underfloor heating, LPG",
        ): "BoilerRadiatorsLPG",
        (
            "Boiler and radiators, oil",
            "Boiler and underfloor heating, oil",
        ): "BoilerRadiatorsOil",
        ("Electric underfloor heating",): "ElectricUnderfloor",
        ("Community scheme",): "CommunityScheme",
        ("Warm air, mains gas",): "WarmAirMainsGas",
        (
            "Boiler & underfloor, mains gas",
            "Boiler and underfloor heating, mains gas",
        ): "BoilerUnderfloorMainsGas",
        ("Air source heat pump",): "AirSourceHeatPump",
        (
            "Boiler and radiators, electric",
            "Boiler and underfloor heating, electric",
        ): "BoilerRadiatorsElectric",
        ("Ground source heat pump",): "GroundSourceHeatPump",
        ("Boiler and radiators, dual fuel",): "BoilerRadiatorsDualFuel",
        ("Boiler and radiators, wood",): "BoilerRadiatorsWood",
        ("Room heaters, mains gas",): "RoomHeatersMainsGas",
        ("No system present",): "NoSystemPresent",
        ("Water source heat pump",): "WaterSourceHeatPump",
    }

    for categories, mapped_value in category_map.items():
        if any(category in value for category in categories):
            result = mapped_value
            break

    return result


def map_fuel_category(value):
    """Enumerate fuel categories."""
    if pd.isna(value) or not isinstance(value, str):
        return np.nan

    value = str(value).lower()

    # Mapping keywords to categories
    keyword_map = {
        "mains gas": "MainsGas",
        "electricity": "Electricity",
        "oil": "Oil",
        "lpg": "LPG",
        "no heating/hot-water system": "NoSystem",
        "dual fuel": "DualFuel",
        "wood logs": "WoodLogs",
        "house coal": "Coal",
        "biomass": "Biomass",
        "invalid": "Invalid",
        "anthracite": "Anthracite",
        "smokeless coal": "SmokelessCoal",
        "wood pellets": "WoodPellets",
        "wood chips": "WoodChips",
        "biogas": "Biogas",
    }

    for keyword, mapped_value in keyword_map.items():
        if keyword in value:
            return mapped_value

    return np.nan


def map_glazing_type(value):
    """Enumerate glazing type."""
    mapping = {
        "double glazing installed before 2002": "DoubleGlazingBefore2002",
        "double glazing installed during or after 2002": "DoubleGlazingAfter2002",
        "double glazing, unknown install date": "DoubleGlazing",
        "not defined": np.nan,
        "secondary glazing": "SecondaryGlazing",
        "single glazing": "SingleGlazing",
        "INVALID!": np.nan,
        "triple glazing": "TripleGlazing",
        "double, known data": "DoubleGlazing",
        "triple, known data": "TripleGlazing",
    }
    return mapping.get(value, np.nan)


def transform_property_type(value):
    """Transform Property Type."""
    if pd.isna(value) or value == "":
        return np.nan

    mappings = {
        "A1/A2RetailAndFinancial/ProfessionalServices": "Other",
        (
            "A3/A4/A5RestaurantAndCafes/"  # pragma: allowlist secret
            "DrinkingEstablishmentsAndHotFoodTakeaways"
        ): "Other",
        "B1OfficesAndWorkshopBusinesses": "Other",
        "B2ToB7GeneralIndustrialAndSpecialIndustrialGroups": "Other",
        "B8StorageOrDistribution": "Other",
        "Bungalow": "Bungalow",
        "C1Hotels": "Other",
        "C2ASecureResidentialInstitutions": "Other",
        "C2ResidentialInstitutions-HospitalsAndCareHomes": "Other",
        "C2ResidentialInstitutions-ResidentialSchools": "Other",
        "C2ResidentialInstitutions-UniversitiesAndColleges": "Other",
        "Community/DayCentre": "Other",
        "D1Non-ResidentialInstitutions-Community/DayCentre": "Other",
        "D1Non-ResidentialInstitutions-Education": "Other",
        "D1Non-ResidentialInstitutions-LibrariesMuseumsAndGalleries": "Other",
        "D1Non-ResidentialInstitutions-PrimaryHealthCareBuilding": "Other",
        "D2GeneralAssemblyAndLeisurePlusNightClubsAndTheatres": "Other",
        "Dwelling": "Other",
        "Flat": "Flat",
        "GeneralAssemblyAndLeisureNightClubsAndTheatres": "Other",
        "Hotel": "Other",
        "Hotels": "Other",
        "House": "House",
        "IndustrialProcessBuilding": "Other",
        "Maisonette": "Maisonette",
        "Non-ResidentialInstitutions:Education": "Other",
        "Non-ResidentialInstitutions:LibrariesMuseumsAndGalleries": "Other",
        "Non-ResidentialInstitutions:PrimaryHealthCareBuilding": "Other",
        "NursingResidentialHomesAndHostels": "Other",
        "Office": "Other",
        "OfficesAndWorkshopBusinesses": "Other",
        "Others-StandAloneUtilityBlock": "Other",
        "Others:EmergencyServices": "Other",
        "ParkHome": "ParkHome",
        "PrimaryHealthCareBuildings": "Other",
        "PrimarySchool": "Other",
        "Prisons": "Other",
        "ResidentialInstitutions:HospitalsAndCareHomes": "Other",
        "ResidentialInstitutions:ResidentialSchools": "Other",
        "ResidentialSpaces": "Other",
        "Restaurant/PublicHouse": "Other",
        "RestaurantsAndCafes/DrinkingEstablishments/Takeaways": "Other",
        "Retail": "Other",
        "Retail/FinancialAndProfessionalServices": "Other",
        "RetailWarehouses": "Other",
        "SocialClubs": "Other",
        "SportsCentre/LeisureCentre": "Other",
        "StorageOrDistribution": "Other",
        "WarehouseAndStorage": "Other",
        "Workshops/MaintenanceDepot": "Other",
    }

    # Return the mapped value if it's in the mapping, else return 'Other'
    return mappings.get(value, np.nan)


def transform_built_form(value):
    """Transform BuiltForm."""
    if pd.isna(value):
        return np.nan
    return "".join(word.capitalize() for word in value.replace("-", " ").split()).replace("-", "")


def map_age_band(value):
    """Enumerate age bands."""
    if pd.isna(value):
        return np.nan

    value_str = str(value)

    # Extracting years directly
    if "England and Wales:" in value_str:
        years = value_str.replace("England and Wales:", "").strip()

        if "-" in years or "onwards" in years:
            # Either return the range or the "onwards" format
            return years if "-" in years else years.split(" ", maxsplit=1)[0] + " Onwards"

    # If the value is a single year, or "INVALID!", "Unknown", or starts with "Year"
    if value_str.isdigit():
        return value_str
    if value_str in ("INVALID!", "Unknown"):
        return np.nan
    if value_str.startswith("Year"):
        return value_str.replace("Year", "")

    return np.nan


def pipeline(df):
    """Cleanse and prepare raw data for address profiling dataset."""
    # Filter out the required columns with uppercase names
    columns_to_keep = [
        "lmk_key",
        "uprn",
        "address",
        "postcode",
        "property_type",
        "built_form",
        "current_energy_rating",
        "current_energy_efficiency",
        "roof_description",
        "walls_description",
        "floor_description",
        "windows_description",
        "glazed_type",
        "total_floor_area",
        "environment_impact_current",
        "lodgement_date",
        "co2_emissions_current",
        "floor_level",
        "heating_cost_current",
        "construction_age_band",
        "main_heating_controls",
        "mainheat_description",
        "main_fuel",
        "number_open_fireplaces",
        "wind_turbine_count",
        "mechanical_ventilation",
        # "heating_cost_current",  # Un-commented as it was commented in your original list
        "hot_water_cost_current",
        "lighting_cost_current",
        "inspection_date",
        "flat_storey_count",
        "certificate_type",
    ]

    df = (
        df[columns_to_keep]
        .copy()
        .drop_duplicates()
        # Split the columns into multiple columns
        .pipe(split_columns)
        # Data cleansing
        .pipe(cleanse_data)
    )
    # Split the roof description based on whether it has the thickness of the insulation
    df["roof_description_3"] = df["roof_description_2"].apply(
        lambda x: x.split(" ")[0] + " mm" if isinstance(x, str) and "mm" in x else np.nan,
    )

    df["roof_description_4"] = df["roof_description_2"].apply(
        lambda x: " ".join(x.split(" ")[2:]) if isinstance(x, str) and "mm" in x else x,
    )

    df = df.rename(
        columns={
            "lmk_key": "LMK_KEY",
            "uprn": "UPRN",
            "current_energy_efficiency": "SAPRating",
            "current_energy_rating": "SAPBand",
            "roof_description_1": "RoofConstruction",
            "roof_description_3": "RoofInsulationThickness",
            "roof_description_4": "RoofInsulationLocation",
            "walls_description": "WallConstruction",
            "walls_description_2": "WallInsulationType",
            "walls_description_3": "WallInsulationThickness",
            "floor_description_1": "FloorConstruction",
            "floor_description_2": "FloorInsulation",
            "glazed_type": "MultipleGlazingType",
            "environmental_impact_current": "EnvironmentalImpactRating",
            "co2_emissions_current": "tCO2",
            "heating_cost_current": "HeatingCost(£/yr)",
            "main_heating_controls": "MainHeatingControl",
            "mainheat_description": "MainHeatingCategory",
            "main_fuel": "MainFuelType",
            "number_open_fireplaces": "OpenFireplacesCount",
            "wind_turbine_count": "Renewables",
            "mechanical_ventilation": "Ventilation",
            "hot_water_cost_current": "WaterHeatingCost(£/yr)",
            "lighting_cost_current": "LightingCost(£/yr)",
            "flat_storey_count": "StoreysCount",
            "floor_level": "FlatLevel",
            "address": "Address",
            "postcode": "Postcode",
            "environment_impact_current": "EnvironmentalImpactRating",
            "lodgement_date": "LodgementDate",
            "property_type": "PropertyType",
            "construction_age_band": "ConstructionAgeBand",
            "built_form": "BuiltForm",
            "total_floor_area": "TotalFloorArea",
            # "fuzzy_matched": "FuzzyMatched",
            "certificate_type": "CertificateType",
        },
    )

    # Add new blank columns
    blank_cols = [
        "UDPRN",
        "ParityAddressId",
        "EnvironmentalImpactRatingBand",
        "FuelBills(£/yr)",
        "FloorInsulationThickness",
        "RealisticFuelBill(Regional)",
        "SAPVersion",
        # "HeatingCost(£/yr)",  # noqa: ERA001
        "FlatLocation",
        "LowestFloorArea",
        "DerivedSAPMainHeatingCode",
        "HeatEmitterType",
        "WaterHeatingFuel",
    ]

    for col in blank_cols:
        df[col] = np.nan

    df = df[
        [
            "LMK_KEY",
            "UPRN",
            "UDPRN",
            "ParityAddressId",
            "Address",
            "Postcode",
            "EnvironmentalImpactRating",
            "EnvironmentalImpactRatingBand",
            "FuelBills(£/yr)",
            "RealisticFuelBill(Regional)",
            "tCO2",
            "HeatingCost(£/yr)",
            "SAPRating",
            "SAPBand",
            "LodgementDate",
            "SAPVersion",
            "PropertyType",
            "ConstructionAgeBand",
            "BuiltForm",
            "StoreysCount",
            "FlatLocation",
            "FlatLevel",
            "LowestFloorArea",
            "MainHeatingCategory",
            "MainFuelType",
            "MainHeatingControl",
            "DerivedSAPMainHeatingCode",
            "HeatEmitterType",
            "WaterHeatingFuel",
            "RoofConstruction",
            "RoofInsulationLocation",
            "RoofInsulationThickness",
            "WallConstruction",
            "WallInsulationType",
            "WallInsulationThickness",
            "FloorConstruction",
            "FloorInsulation",
            "FloorInsulationThickness",
            "MultipleGlazingType",
            "OpenFireplacesCount",
            "Renewables",
            "Ventilation",
            "WaterHeatingCost(£/yr)",
            "LightingCost(£/yr)",
            "TotalFloorArea",
            # "FuzzyMatched",
            "CertificateType",
        ]
    ].copy()

    df["RoofConstruction"] = df["RoofConstruction"].apply(transform_roof_construction)
    df["RoofInsulationLocation"] = df["RoofInsulationLocation"].apply(
        transform_roof_insulation_location,
    )
    df["RoofInsulationThickness"] = df["RoofInsulationThickness"].apply(
        clean_roof_insulation_thickness,
    )

    df["WallInsulationType"] = df["WallConstruction"].apply(transform_wall_insulation_type)
    df["WallConstruction"] = df["WallConstruction"].apply(transform_wall_construction)
    df["WallInsulationThickness"] = df["WallInsulationThickness"].apply(
        transform_wall_insulation_thickness,
    )

    df["FloorConstruction"] = df["FloorConstruction"].apply(transform_floor_construction)
    df["FloorInsulation"] = df["FloorInsulation"].apply(transform_floor_insulation)
    df["FloorInsulationThickness"] = df["FloorInsulationThickness"].apply(
        transform_floor_insulation_thickness,
    )

    df["MainHeatingCategory"] = df["MainHeatingCategory"].apply(map_heating_category)
    df["MainFuelType"] = df["MainFuelType"].apply(map_fuel_category)

    df["MultipleGlazingType"] = df["MultipleGlazingType"].apply(map_glazing_type)
    df["ConstructionAgeBand"] = df["ConstructionAgeBand"].apply(map_age_band)
    df["ConstructionAgeBand"] = df["ConstructionAgeBand"].apply(to_pascal_case)
    df["PropertyType"] = df["PropertyType"].apply(transform_property_type)
    df["BuiltForm"] = df["BuiltForm"].apply(transform_built_form)

    # Mapping dictionary
    floor_mapping = {
        "Basement": -1,
        "-1.0": -1,
        "-1": -1,
        "Ground": 0,
        "ground floor": 0,
        "00": 0,
        "0.0": 0,
        "1st": 1,
        "01": 1,
        "1.0": 1,
        "1": 1,
        "2nd": 2,
        "02": 2,
        "2.0": 2,
        "2": 2,
        "3rd": 3,
        "03": 3,
        "3.0": 3,
        "3": 3,
        "4th": 4,
        "04": 4,
        "5th": 5,
        "05": 5,
        "5.0": 5,
        "6th": 6,
        "7th": 7,
        "07": 7,
        "8th": 8,
        "12th": 12,
    }

    # Let's find the max floor for 'top floor'
    max_floor = max(list(floor_mapping.values()))
    floor_mapping["TopFloor"] = max_floor + 1

    # For 'mid floor', we'll average the min and max values
    min_floor = min(list(floor_mapping.values()))
    floor_mapping["MidFloor"] = (max_floor + min_floor) // 2

    # Replace values in dataframe
    df["FlatLevel"] = df["FlatLevel"].map(floor_mapping).fillna(np.nan)
    df["LMK_KEY"] = df["LMK_KEY"].astype(str)

    # Drop rows where UPRN is null
    df = df.dropna(subset=["UPRN"])
    df = df[df["UPRN"] != ""]
    df = df.sort_values("LodgementDate", ascending=False).drop_duplicates(
        subset="UPRN",
        keep="first",
    )

    return df


def model(dbt, fal):
    """dbt-fal model."""
    return dbt.ref("epc_with_uprn").pipe(pipeline)


def main(input_csv: str, output_csv: str, to_excel: bool):
    """Process input CSV and save cleansed CSV file."""
    df = pd.read_csv(input_csv, low_memory=False, dtype={"uprn": str, "lmk_key": str}).pipe(
        pipeline,
    )
    if to_excel:
        # Save to XLSX
        df = df.dropna(subset=["uprn"])
        df["uprn"] = df["uprn"].astype(float).astype("int64")
        df.to_excel(output_csv.replace(".csv", ".xlsx"), index=False, engine="openpyxl")
    else:
        # Save to CSV
        df.to_csv(output_csv, index=False)
    typer.echo(f"File saved to {output_csv}")


if __name__ == "__main__":
    typer.run(main)
