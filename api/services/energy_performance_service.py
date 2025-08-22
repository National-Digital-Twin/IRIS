# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


from sqlalchemy import text
from db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_geojson_for_energy_performance_by_wards(
    db: AsyncSession = Depends(get_db),):
    """ Query the database to fetch wind-driven rain data in GeoJSON format.
    
    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(text("SELECT geojson::text AS geojson FROM iris.uk_ward_epc;"))
    row = result.fetchone()
    return row[0]
    