# tests/integration/test_weather_pipeline.py

from datetime import date

from database.sqlite import SQLiteBackend
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
                    "2026-01-01T00:00",
                    "2026-01-01T01:00",
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
                    25.0,
                ],
            }
        }


class WeatherConfig:

    latitude = 51.7
    longitude = -0.4


def test_weather_pipeline(
    tmp_path,
):

    #
    # Create database
    #

    db_file = tmp_path / "weather.db"

    db = SQLiteBackend(
        str(db_file)
    )

    #
    # Collect weather
    #

    collector = WeatherCollector(
        MockWeatherClient()
    )

    history = collector.get_day_hourly(
        date(
            2026,
            1,
            1,
        )
    )

    #
    # Store weather
    #

    db.load_weather(
        WeatherConfig(),
        history,
    )

    #
    # Verify row count
    #

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM weather
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 2

    #
    # Verify data
    #

    db.cursor.execute(
        """
        SELECT
            timestamp,
            temperature,
            cloud_cover,
            solar_radiation
        FROM weather
        ORDER BY timestamp
        """
    )

    rows = db.cursor.fetchall()

    assert rows[0] == (
        "2026-01-01T00:00",
        10.5,
        50,
        0.0,
    )

    assert rows[1] == (
        "2026-01-01T01:00",
        11.0,
        75,
        25.0,
    )

    db.close()

def test_weather_pipeline_is_idempotent(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "weather.db"
        )
    )

    collector = WeatherCollector(
        MockWeatherClient()
    )

    history = collector.get_day_hourly(
        date(
            2026,
            1,
            1,
        )
    )

    db.load_weather(
        WeatherConfig(),
        history,
    )

    db.load_weather(
        WeatherConfig(),
        history,
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM weather
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 2

    db.close()