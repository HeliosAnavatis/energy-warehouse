from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from sources.solarassistant.client import (
    SolarAssistantClient,
)

def create_client():

    return SolarAssistantClient(
        base_url="http://solarassistant.local",
        username="admin",
        password="secret",
        topics={
            "pv-generation": "total/pv_power",
            "battery-soc": "battery/soc",
        },
    )

def test_client_initialises():

    client = create_client()

    assert (
        client.base_url
        == "http://solarassistant.local"
    )

    assert client.auth == (
        "admin",
        "secret",
    )

@patch(
    "sources.solarassistant.client.requests.get"
)
def test_get_readings_returns_json(
    mock_get
):

    payload = {
        "points": []
    }

    response = Mock()

    response.json.return_value = payload
    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = create_client()

    result = client.get_readings(
        meter_id="pv-generation",
        start=datetime.now(),
        end=datetime.now(),
    )

    assert result == payload

def test_get_readings_unknown_meter():

    client = create_client()

    with pytest.raises(
        ValueError
    ):

        client.get_readings(
            meter_id="does-not-exist",
            start=datetime.now(),
            end=datetime.now(),
        )

@patch(
    "sources.solarassistant.client.requests.get"
)
def test_get_readings_sends_correct_parameters(
    mock_get
):

    response = Mock()

    response.json.return_value = {
        "points": []
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    start = datetime(
        2026,
        11,
        22,
        0,
        0,
    )

    end = datetime(
        2026,
        11,
        23,
        0,
        0,
    )

    client = create_client()

    client.get_readings(
        meter_id="pv-generation",
        start=start,
        end=end,
    )

    _, kwargs = mock_get.call_args

    assert (
        kwargs["params"]["topic"]
        == "total/pv_power"
    )

    assert (
        kwargs["params"]["group_by"]
        == "30m"
    )

    assert (
        kwargs["params"]["agg"]
        == "mean"
    )

@patch(
    "sources.solarassistant.client.requests.get"
)
def test_get_soc_returns_json(
    mock_get
):

    payload = {
        "points": []
    }

    response = Mock()

    response.json.return_value = payload
    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = create_client()

    result = client.get_soc(
        start=datetime.now(),
        end=datetime.now(),
    )

    assert result == payload

@patch(
    "sources.solarassistant.client.requests.get"
)
def test_get_soc_uses_last_aggregation(
    mock_get
):

    response = Mock()

    response.json.return_value = {
        "points": []
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = create_client()

    client.get_soc(
        start=datetime.now(),
        end=datetime.now(),
    )

    _, kwargs = mock_get.call_args

    assert (
        kwargs["params"]["agg"]
        == "last"
    )

def test_get_soc_requires_topic():

    client = SolarAssistantClient(
        base_url="http://solarassistant.local",
        username="admin",
        password="secret",
        topics={},
    )

    with pytest.raises(
        ValueError
    ):

        client.get_soc(
            start=datetime.now(),
            end=datetime.now(),
        )