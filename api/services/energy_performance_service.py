# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


from sqlalchemy import text
from db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_geojson_for_energy_performance_by_wards(
    db: AsyncSession = Depends(get_db),):
    """ Query the database to fetch EPC data for wards in GeoJSON format.
    
    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(text("SELECT geojson::text AS geojson FROM iris.uk_ward_epc;"))
    row = result.fetchone()
    return row[0]

async def fetch_geojson_for_energy_performance_by_districts(
    db: AsyncSession = Depends(get_db),):
    """ Query the database to fetch EPC data for districts in GeoJSON format.
    
    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(text("SELECT geojson::text AS geojson FROM iris.district_borough_unitary_epc;"))
    row = result.fetchone()
    return row[0]

async def fetch_geojson_for_energy_performance_by_counties(
    db: AsyncSession = Depends(get_db),):
    """ Query the database to fetch EPC data for counties in GeoJSON format.
    
    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(text("SELECT geojson::text AS geojson FROM iris.boundary_line_ceremonial_counties_epc;"))
    row = result.fetchone()
    return row[0]

async def fetch_geojson_for_energy_performance_by_regions(
    db: AsyncSession = Depends(get_db),):
    """ Query the database to fetch EPC data for regions in GeoJSON format.
    
    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(text("SELECT geojson::text AS geojson FROM iris.uk_region_epc;"))
    row = result.fetchone()
    return row[0]
    