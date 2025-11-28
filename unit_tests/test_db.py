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
    """Test that execute_with_timeout sets LOCAL timeout before query and resets after success"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_session.execute.return_value = mock_result

    query = text("SELECT * FROM buildings")
    timeout_seconds = 60
    params = {"uprn": "12345"}

    with patch("db.settings.DB_QUERY_TIMEOUT", 10):
        result = await execute_with_timeout(mock_session, query, timeout_seconds, params)

    # Verify timeout was set before query execution
    assert mock_session.execute.call_count == 3

    # First call: SET LOCAL statement_timeout
    first_call = mock_session.execute.call_args_list[0]
    set_timeout_query = first_call[0][0]
    assert set_timeout_query.text == "SET LOCAL statement_timeout = '60000'"

    # Second call: the actual query with params
    second_call = mock_session.execute.call_args_list[1]
    assert second_call[0][0] == query
    assert second_call[0][1] == params

    # Third call: reset timeout - should reset to query_timeout value
    third_call = mock_session.execute.call_args_list[2]
    reset_timeout_query = third_call[0][0]
    assert reset_timeout_query.text == "SET LOCAL statement_timeout = '10000'"

    assert result == mock_result


@pytest.mark.asyncio
async def test_execute_with_timeout_does_not_reset_on_error():
    """Test that execute_with_timeout does NOT try to reset timeout when query fails.

    This is important because when a query times out, the transaction is in a failed state
    and cannot execute any more SQL (including the reset). By not attempting the reset,
    we avoid InFailedSQLTransactionError.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    # Make the second execute call (the actual query) raise an exception
    mock_session.execute.side_effect = [
        AsyncMock(),  # First call (SET LOCAL timeout) succeeds
        Exception("Query failed"),  # Second call (query) fails
    ]

    query = text("SELECT * FROM buildings")
    timeout_seconds = 30

    with pytest.raises(Exception, match="Query failed"):
        await execute_with_timeout(mock_session, query, timeout_seconds)

    # Verify reset was NOT attempted after error (only 2 calls, not 3)
    assert mock_session.execute.call_count == 2
