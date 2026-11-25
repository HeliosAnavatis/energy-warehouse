# tests/unit/weather/test_weather_collector.py

from datetime import date

from sources.weather.collector import WeatherCollector


class MockWeatherClient:

    def get_history(
        self,
        start_date,
        end_date,
    ):

        return {
            "hourly": {
                "time": [
                    "2026-11-22T00:00",
                    "2026-11-22T01:00",
                ],
                "temperature_2m": [
                    10.5,
                    11.0,
                ],
                "cloud_cover": [
                    50,
                    75,
                ],
                "shortwave_radiation": [
                    0.0,
                    12.5,
                ],
            }
        }


def test_get_day_hourly_returns_list():

    collector = WeatherCollector(
        MockWeatherClient()
    )

    results = collector.get_day_hourly(
        date(2026, 11, 22)
    )

    assert isinstance(
        results,
        list,
    )


def test_get_day_hourly_returns_expected_count():

    collector = WeatherCollector(
        MockWeatherClient()
    )

    results = collector.get_day_hourly(
        date(2026, 11, 22)
    )

    assert len(results) == 2


def test_get_day_hourly_maps_fields_correctly():

    collector = WeatherCollector(
        MockWeatherClient()
    )

    results = collector.get_day_hourly(
        date(2026, 11, 22)
    )

    assert results[0] == {
        "timestamp": "2026-11-22T00:00",
        "temperature": 10.5,
        "cloud_cover": 50,
        "solar_radiation": 0.0,
    }


def test_get_day_hourly_calls_client_with_same_day():

    class TrackingClient:

        def __init__(self):

            self.start_date = None
            self.end_date = None

        def get_history(
            self,
            start_date,
            end_date,
        ):

            self.start_date = start_date
            self.end_date = end_date

            return {
                "hourly": {
                    "time": [],
                    "temperature_2m": [],
                    "cloud_cover": [],
                    "shortwave_radiation": [],
                }
            }

    client = TrackingClient()

    collector = WeatherCollector(
        client
    )

    collector.get_day_hourly(
        date(2026, 11, 22)
    )

    assert client.start_date == "2026-11-22"
    assert client.end_date == "2026-11-22"