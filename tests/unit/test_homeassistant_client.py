# tests/unit/homeassistant/test_homeassistant_client.py

from unittest.mock import Mock
from unittest.mock import patch
from datetime import timedelta

from sources.homeassistant.client import (
    HomeAssistantClient,
)

def test_client_initialises():

    client = HomeAssistantClient(
        base_url="http://ha.local",
        token="secret",
        timeout=60,
    )

    assert client.base_url == (
        "http://ha.local"
    )

    assert client.timeout == 60

    assert (
        client.headers["Authorization"]
        == "Bearer secret"
    )

@patch(
    "sources.homeassistant.client.requests.get"
)
def test_get_state_calls_api(
    mock_get
):

    response = Mock()

    response.json.return_value = {
        "state": "55"
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    client.get_state(
        "sensor.test"
    )

    mock_get.assert_called_once()

@patch(
    "sources.homeassistant.client.requests.get"
)
def test_get_state_returns_json(
    mock_get
):

    payload = {
        "state": "55"
    }

    response = Mock()

    response.json.return_value = payload

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    result = client.get_state(
        "sensor.test"
    )

    assert result == payload
@patch(
    "sources.homeassistant.client.requests.get"
)
def test_get_history_passes_parameters(
    mock_get
):

    response = Mock()

    response.json.return_value = []

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    client.get_history(
        entity_id="sensor.test",
        start="2026-11-22T00:00:00",
        end="2026-11-23T00:00:00",
    )

    _, kwargs = mock_get.call_args

    assert (
        kwargs["params"]["filter_entity_id"]
        == "sensor.test"
    )

    assert (
        kwargs["params"]["end_time"]
        == "2026-11-23T00:00:00"
    )

def test_parse_group_by_minutes():

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    assert (
        client._parse_group_by("30m")
        == timedelta(minutes=30)
    )


def test_parse_group_by_hours():

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    assert (
        client._parse_group_by("1h")
        == timedelta(hours=1)
    )


def test_parse_group_by_seconds():

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    assert (
        client._parse_group_by("15s")
        == timedelta(seconds=15)
    )

import pytest


def test_parse_group_by_invalid():

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    with pytest.raises(
        ValueError
    ):

        client._parse_group_by(
            "2d"
        )

@patch(
    "sources.homeassistant.client.requests.get"
)
def test_get_history_buckets_mean(
    mock_get
):

    payload = [[
        {
            "last_changed":
                "2026-11-22T00:05:00",
            "state": "10",
        },
        {
            "last_changed":
                "2026-11-22T00:15:00",
            "state": "20",
        },
    ]]

    response = Mock()

    response.json.return_value = payload

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = HomeAssistantClient(
        "http://ha.local",
        "secret",
    )

    result = client.get_history_buckets(
        entity_id="sensor.test",
        start="2026-11-22T00:00:00",
        end="2026-11-23T00:00:00",
        group_by="30m",
        agg="mean",
    )

    assert len(result) == 1

    assert result[0]["value"] == 15.0

