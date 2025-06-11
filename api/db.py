# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


from typing import Annotated

from config import Settings, get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


async def get_db(settings: Annotated[Settings, Depends(get_settings)]):
    db_connection_string = settings.get_db_connection_string()

    if db_connection_string.startswith("postgres"):
        engine = create_async_engine(
            db_connection_string, connect_args={}, pool_pre_ping=True
        )
    elif db_connection_string.startswith("sqlite"):
        engine = create_async_engine(
            db_connection_string, connect_args={"check_same_thread": False}
        )
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
