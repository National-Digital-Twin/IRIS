# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

from typing import Tuple

from db import get_db
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_geojson_for_deprivation(
    db: AsyncSession = Depends(get_db),
) -> Tuple:
    """Query the database to fetch deprivation data in GeoJSON format.

    Keyword arguments:
    db -- an AsyncSession for sql alchemy
    """
    result = await db.execute(
        text("SELECT geojson::text AS geojson FROM iris.msoa_deprivation_geojson;")
    )
    row = result.fetchone()
    return row[0]