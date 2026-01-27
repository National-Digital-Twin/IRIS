# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import asyncio
import json

import asyncpg.exceptions
import pytest
import sqlalchemy.exc
from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

import db as db_module
from main import app, query_timeout_handler


class MockRequest:
    pass


def test_query_timeout_handler_returns_504_for_query_canceled():
    original_db_error = MagicMock()
    original_db_error.sqlstate = asyncpg.exceptions.QueryCanceledError.sqlstate

    ex = sqlalchemy.exc.DBAPIError("statement", {}, original_db_error, None)
    request = MockRequest()

    response = asyncio.run(query_timeout_handler(request, ex))

    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert response.body == b'{"detail":"The request took too long to complete.","error":"QueryCanceledError"}'


def test_query_timeout_handler_returns_json_error_response():
    original_db_error = MagicMock()
    original_db_error.sqlstate = asyncpg.exceptions.QueryCanceledError.sqlstate

    ex = sqlalchemy.exc.DBAPIError("statement", {}, original_db_error, None)
    request = MockRequest()

    response = asyncio.run(query_timeout_handler(request, ex))

    body = json.loads(response.body)

    assert "detail" in body
    assert "error" in body
    assert body["detail"] == "The request took too long to complete."
    assert body["error"] == "QueryCanceledError"


def test_query_timeout_handler_reraises_other_dbapi_errors():
    original_db_error = MagicMock()
    original_db_error.sqlstate = "23505"

    ex = sqlalchemy.exc.DBAPIError("statement", {}, original_db_error, None)
    request = MockRequest()

    with pytest.raises(sqlalchemy.exc.DBAPIError):
        asyncio.run(query_timeout_handler(request, ex))


def test_query_timeout_handler_reraises_when_no_sqlstate():
    original_db_error = MagicMock(spec=[])
    delattr(original_db_error, "sqlstate") if hasattr(original_db_error, "sqlstate") else None

    ex = sqlalchemy.exc.DBAPIError("statement", {}, original_db_error, None)
    request = MockRequest()

    with pytest.raises(sqlalchemy.exc.DBAPIError):
        asyncio.run(query_timeout_handler(request, ex))


def test_query_timeout_handler_reraises_when_sqlstate_is_none():
    original_db_error = MagicMock()
    original_db_error.sqlstate = None

    ex = sqlalchemy.exc.DBAPIError("statement", {}, original_db_error, None)
    request = MockRequest()

    with pytest.raises(sqlalchemy.exc.DBAPIError):
        asyncio.run(query_timeout_handler(request, ex))


def test_exception_handler_is_registered():
    assert sqlalchemy.exc.DBAPIError in app.exception_handlers
    assert app.exception_handlers[sqlalchemy.exc.DBAPIError] == query_timeout_handler


def test_query_timeout_integration():
    async def mock_get_db_that_fails():
        mock_session = AsyncMock()

        original_db_error = MagicMock()
        original_db_error.sqlstate = asyncpg.exceptions.QueryCanceledError.sqlstate
        ex = sqlalchemy.exc.DBAPIError("statement", {}, original_db_error, None)

        mock_session.execute.side_effect = ex
        yield mock_session

    test_router = APIRouter()

    @test_router.get("/test-timeout")
    async def test_timeout_endpoint(db: AsyncSession = Depends(db_module.get_db)):
        await db.execute(text("SELECT * FROM buildings"))
        return {"status": "ok"}

    test_app = FastAPI()
    test_app.include_router(test_router)
    test_app.add_exception_handler(sqlalchemy.exc.DBAPIError, query_timeout_handler)
    test_app.dependency_overrides[db_module.get_db] = mock_get_db_that_fails

    client = TestClient(test_app)

    response = client.get("/test-timeout")

    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    data = response.json()
    assert data["error"] == "QueryCanceledError"
    assert "took too long" in data["detail"]
