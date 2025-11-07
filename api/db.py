# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


from typing import Optional

from config import get_settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()
db_connection_string = settings.get_db_connection_string()

if db_connection_string and db_connection_string.startswith("postgres"):
    statement_timeout_ms = str(settings.DB_QUERY_TIMEOUT * 1000)
    engine: Optional[AsyncEngine] = create_async_engine(
        db_connection_string,
        connect_args={"server_settings": {"statement_timeout": statement_timeout_ms}},
        pool_pre_ping=True,
    )
elif db_connection_string and db_connection_string.startswith("sqlite"):
    engine: Optional[AsyncEngine] = create_async_engine(
        db_connection_string, connect_args={"check_same_thread": False}
    )
else:
    engine = None

if engine:
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    async_session_maker = None


async def get_db():
    if async_session_maker is None:
        raise RuntimeError("Database not configured")
    async with async_session_maker() as session:
        yield session


async def execute_with_timeout(
    session: AsyncSession,
    query: text,
    timeout_seconds: int,
    params: Optional[dict] = None,
):
    timeout_ms = str(timeout_seconds * 1000)
    await session.execute(text(f"SET statement_timeout = '{timeout_ms}'"))
    try:
        result = await session.execute(query, params)
        return result
    finally:
        await session.execute(
            text(f"SET statement_timeout = '{settings.DB_QUERY_TIMEOUT * 1000}'")
        )
