import requests
from collections import defaultdict
from datetime import datetime, timedelta

class HomeAssistantClient:

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: int = 30,
    ):

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_state(self, entity_id: str):

        response = requests.get(
            f"{self.base_url}/api/states/{entity_id}",
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def get_history(self, entity_id: str, start: str, end: str):

        response = requests.get(
            f"{self.base_url}/api/history/period/{start}",
            headers=self.headers,
            params={
                "filter_entity_id": entity_id,
                "end_time": end,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def get_history_buckets (self, entity_id: str, start: str, end: str, group_by: str = "h", agg: str = "mean"):
        
        response = requests.get(
            f"{self.base_url}/api/history/period/{start}",
            headers=self.headers,
            params={
                "filter_entity_id": entity_id,
                "end_time": end,
                "group_by": group_by,
                "agg": agg,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        records = response.json()
        if not records:
            return []
        records = records[0]
        bucket_size = self._parse_group_by(group_by)
        start_dt = datetime.fromisoformat(start)
        buckets = defaultdict(list)

        for record in records:
            timestamp = datetime.fromisoformat(
                record["last_changed"]
            )
            try:
                value = float(record["state"])
            except (TypeError, ValueError):
                continue
            bucket_number = int(
                (timestamp - start_dt).total_seconds()
                // bucket_size.total_seconds()
            )
            bucket_start = (
                start_dt
                + bucket_size * bucket_number
            )
            buckets[bucket_start].append(value)
            results = []

        for bucket_start in sorted(buckets):
            values = buckets[bucket_start]
            if agg == "mean":
                value = sum(values) / len(values)
            elif agg == "max":
                value = max(values)
            elif agg == "min":
                value = min(values)
            elif agg == "last":
                value = values[-1]
            elif agg == "sum":
                value = sum(values)
            else:
                raise ValueError(
                    f"Unsupported aggregation: {agg}"
                )

            results.append(
                {
                    "timestamp": bucket_start.isoformat(),
                    "value": value,
                }
            )

        return results

    def _parse_group_by(self, group_by: str):

        unit = group_by[-1]
        amount = int(group_by[:-1])

        if unit == "s":
            return timedelta(seconds=amount)

        if unit == "m":
            return timedelta(minutes=amount)

        if unit == "h":
            return timedelta(hours=amount)

        raise ValueError(
            f"Unsupported group_by value: {group_by}"
        )      