from datetime import datetime
import requests

class SolarAssistantClient:

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        topics: dict[str, str],
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = (username, password)
        self.topics = topics

    def get_readings(
        self,
        meter_id: str,
        start: datetime,
        end: datetime,
    ):
        group_by = "30m"
        agg = "mean"
        topic = self.topics.get(meter_id)

        if topic is None:
            raise ValueError(
                f"No Solar Assistant topic configured "
                f"for meter '{meter_id}'"
            )

        response = requests.get(
            f"{self.base_url}/api/v1/history",
            params={
                "topic": topic,
                "from": start.isoformat(),
                "to": end.isoformat(),
                "group_by": group_by,
                "agg": agg,
            },
            auth=self.auth,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    # ------------------------------------------------------------------
    def get_soc(
        self,
        start: datetime,
        end: datetime,
    ):

        topic = self.topics.get("battery-soc")

        if topic is None:
            raise ValueError(
                f"No Solar Assistant topic configured for battery SoC"
            )
        
        response = requests.get(
            f"{self.base_url}/api/v1/history",
            params={
                "topic": topic,
                "from": start.isoformat(),
                "to": end.isoformat(),
                "group_by": "30m",
                "agg": "last",
            },
            auth=self.auth,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()