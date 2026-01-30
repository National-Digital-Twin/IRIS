# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.


import pytest
import requests

from api.access import AccessClient


@pytest.fixture
def connection_string():
    return "dummy_connection_string"


@pytest.fixture
def headers():
    return {
        "Authorization": "Bearer dummy_token",
        "X-Auth-Request-Access-Token": "dummy_jwt_token",
    }


def test_dev_mode_returns_dummy_data(connection_string, headers):
    client = AccessClient(connection_string, dev_mode=True)
    result = client.get_user_details(headers)
    expected = {
        "username": "Test User1",
        "user_id": "1234-5678-99ab-cdef",
        "email": "test.user@example.com",
    }
    assert result == expected


def test_api_successful_response(mocker, connection_string, headers):
    # Create a fake successful response.
    fake_response = mocker.MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "content": {
            "displayName": "Test User",
            "username": "069292e4-3081-704c-68cd-b5e621f48b62",
            "email": "test.user@example.com",
        }
    }
    # Patch requests.get in the access module.
    get_mock = mocker.patch("access.requests.get", return_value=fake_response)

    client = AccessClient(connection_string, dev_mode=False)
    result = client.get_user_details(headers)
    expected = {
        "username": "Test User",
        "user_id": "069292e4-3081-704c-68cd-b5e621f48b62",
        "email": "test.user@example.com",
    }
    assert result == expected

    # Ensure the API was called with the correct URL and headers.
    expected_url = "https://test.com/api/v1/user-details"
    get_mock.assert_called_with(expected_url, headers=headers)


def test_api_error_response(mocker, connection_string, headers):
    # Create a fake error response from the API.
    fake_response = mocker.MagicMock()
    fake_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "400 Bad Request"
    )
    mocker.patch("access.requests.get", return_value=fake_response)

    client = AccessClient(connection_string, dev_mode=False)
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_user_details(headers)
