# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


from typing import Tuple

from db import get_db
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def fetch_geojson_for_wind_driven_rain(
    db: AsyncSession = Depends(get_db),
) -> Tuple:
    """Query the database to fetch wind-driven rain data in GeoJSON format.

    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(
        text(
            "SELECT geojson::text AS geojson FROM iris.wind_driven_rain_projections_geojson;"
        )
    )
    row = result.fetchone()
    return row[0]


async def fetch_geojson_for_icing_days(
    db: AsyncSession = Depends(get_db),
) -> Tuple:
    """Query the database to fetch icing days data in GeoJSON format.

    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(
        text("SELECT geojson::text AS geojson FROM iris.icing_days_geojson;")
    )
    row = result.fetchone()
    return row[0]


async def fetch_geojson_for_hot_summer_days(
    db: AsyncSession = Depends(get_db),
) -> Tuple:
    """Query the database to fetch hot summer days data in GeoJSON format.

    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(
        text("SELECT geojson::text AS geojson FROM iris.hot_summer_days_geojson;")
    )
    row = result.fetchone()
    return row[0]

async def fetch_geojson_for_sunlight_hours(
    db: AsyncSession = Depends(get_db),
) -> Tuple: 
    """Query the database to fetch sunlight hours data in GeoJSON format. 

    Keyword arguments: 
    db -- an AsyncSession for sql alchemy 
    """
    result = await db.execute(
        text("SELECT geojson::text AS geojson FROM iris.annual_average_sunlight_hours_geojson;")
    )
    row = result.fetchone()
    return row[0]