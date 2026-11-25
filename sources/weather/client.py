import requests


class WeatherClient:

    def __init__(
        self,
        latitude: float,
        longitude: float,
        timeout: int = 30,
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.timeout = timeout

    def get_history(
        self,
        start_date: str,
        end_date: str,
    ):

        response = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": self.latitude,
                "longitude": self.longitude,
                "start_date": start_date,
                "end_date": end_date,
                "hourly": ",".join(
                    [
                        "temperature_2m",
                        "cloud_cover",
                        "shortwave_radiation",
                    ]
                ),
                "timezone": "GMT",
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()