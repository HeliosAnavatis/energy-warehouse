# tests/unit/weather/test_weather_client.py

from unittest.mock import Mock
from unittest.mock import patch

from sources.weather.client import WeatherClient

def test_client_initialises():

    client = WeatherClient(
        latitude=51.7,
        longitude=-0.4,
    )

    assert client.latitude == 51.7
    assert client.longitude == -0.4
    assert client.timeout == 30

@patch(
    "sources.weather.client.requests.get"
)
def test_get_history_calls_api(mock_get):

    response = Mock()

    response.json.return_value = {
        "hourly": {}
    }

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = WeatherClient(
        latitude=51.7,
        longitude=-0.4,
        timeout=60,
    )

    client.get_history(
        start_date="2026-11-22",
        end_date="2026-11-22",
    )

    mock_get.assert_called_once()


@patch(
    "sources.weather.client.requests.get"
)
def test_get_history_sends_correct_parameters(
    mock_get
):

    response = Mock()

    response.json.return_value = {}

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = WeatherClient(
        latitude=51.7,
        longitude=-0.4,
    )

    client.get_history(
        "2026-11-22",
        "2026-11-22",
    )

    _, kwargs = mock_get.call_args

    assert kwargs["params"]["latitude"] == 51.7
    assert kwargs["params"]["longitude"] == -0.4

    assert (
        kwargs["params"]["start_date"]
        == "2026-11-22"
    )

    assert (
        kwargs["params"]["end_date"]
        == "2026-11-22"
    )

    assert (
        kwargs["params"]["timezone"]
        == "GMT"
    )

@patch(
    "sources.weather.client.requests.get"
)
def test_get_history_returns_json(
    mock_get
):

    expected = {
        "hourly": {
            "time": [
                "2026-11-22T00:00"
            ]
        }
    }

    response = Mock()

    response.json.return_value = expected

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = WeatherClient(
        latitude=51.7,
        longitude=-0.4,
    )

    result = client.get_history(
        "2026-11-22",
        "2026-11-22",
    )

    assert result == expected