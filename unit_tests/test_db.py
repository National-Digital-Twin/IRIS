# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from db import execute_with_timeout


@pytest.mark.asyncio
async def test_execute_with_timeout_sets_and_resets_timeout():
    """Test that execute_with_timeout sets timeout before query and resets after"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_session.execute.return_value = mock_result

    query = text("SELECT * FROM buildings")
    timeout_seconds = 60
    params = {"uprn": "12345"}

    result = await execute_with_timeout(mock_session, query, timeout_seconds, params)

    # Verify timeout was set before query execution
    assert mock_session.execute.call_count == 3  # SET timeout, query, SET timeout back

    # First call: SET statement_timeout
    first_call = mock_session.execute.call_args_list[0]
    set_timeout_query = first_call[0][0]
    assert "SET statement_timeout" in str(set_timeout_query)
    assert "60000" in str(set_timeout_query)  # 60 seconds * 1000

    # Second call: the actual query with params
    second_call = mock_session.execute.call_args_list[1]
    assert second_call[0][0] == query
    assert second_call[0][1] == params

    # Third call: reset timeout - should reset to query_timeout value
    # This verifies it uses the config default (29) not the fallback (30)
    third_call = mock_session.execute.call_args_list[2]
    reset_timeout_query = third_call[0][0]
    assert "SET statement_timeout" in str(reset_timeout_query)
    assert "29000" in str(reset_timeout_query)  # Config default DB_QUERY_TIMEOUT (29) * 1000, not fallback (30)

    assert result == mock_result


@pytest.mark.asyncio
async def test_execute_with_timeout_resets_on_error():
    """Test that execute_with_timeout resets timeout even when query fails"""
    mock_session = AsyncMock(spec=AsyncSession)

    # Make the second execute call (the actual query) raise an exception
    mock_session.execute.side_effect = [
        AsyncMock(),  # First call (SET timeout) succeeds
        Exception("Query failed"),  # Second call (query) fails
        AsyncMock(),  # Third call (reset timeout) succeeds
    ]

    query = text("SELECT * FROM buildings")
    timeout_seconds = 30

    with pytest.raises(Exception, match="Query failed"):
        await execute_with_timeout(mock_session, query, timeout_seconds)

    # Verify timeout was still reset after error
    assert mock_session.execute.call_count == 3

    # Check that reset was called
    third_call = mock_session.execute.call_args_list[2]
    reset_timeout_query = third_call[0][0]
    assert "SET statement_timeout" in str(reset_timeout_query)


@pytest.mark.asyncio
async def test_execute_with_timeout_uses_config_default_for_reset():
    """Test that execute_with_timeout uses query_timeout for reset"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = AsyncMock()

    query = text("SELECT * FROM buildings")
    timeout_seconds = 60

    with patch("db.query_timeout", 45):
        await execute_with_timeout(mock_session, query, timeout_seconds)

        # Check third call resets to query_timeout value
        third_call = mock_session.execute.call_args_list[2]
        reset_timeout_query = str(third_call[0][0])
        assert "45000" in reset_timeout_query  # 45 * 1000


@pytest.mark.asyncio
async def test_execute_with_timeout_uses_fallback_when_config_is_zero():
    """Test that execute_with_timeout uses fallback (30) when DB_QUERY_TIMEOUT is 0"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.return_value = AsyncMock()

    query = text("SELECT * FROM buildings")
    timeout_seconds = 60

    # Patch settings to return 0, which should trigger fallback to DEFAULT_QUERY_TIMEOUT (30)
    with patch("db.settings") as mock_settings:
        mock_settings.DB_QUERY_TIMEOUT = 0
        # Also need to patch query_timeout since it's calculated at module level
        with patch("db.query_timeout", 30):  # Fallback value
            await execute_with_timeout(mock_session, query, timeout_seconds)

            # Check third call resets to fallback value (30)
            third_call = mock_session.execute.call_args_list[2]
            reset_timeout_query = str(third_call[0][0])
            assert "30000" in reset_timeout_query  # Fallback DEFAULT_QUERY_TIMEOUT (30) * 1000
