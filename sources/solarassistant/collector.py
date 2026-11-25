import datetime

class SolarAssistantCollector:

    def __init__(self, client):
        self.client = client

    def get_readings(
        self,
        meter_id: str,
        start: datetime,
        end: datetime,
    ):

        response = self.client.get_readings(
            meter_id=meter_id,
            start=start,
            end=end,
        )

        readings = []

        for timestamp, power in response["points"]:

            #
            # Convert mean W over 30m to kWh
            #
            energy = (
                power
                * 0.5
                / 1000.0
            )

            readings.append(
                {
                    "interval_start": timestamp,
                    "reading": energy,
                }
            )

        return readings

    # ------------------------------------------------------------------
    def get_soc(
        self,
        start: datetime,
        end: datetime,
    ):

        response = self.client.get_soc(
            start=start,
            end=end,
        )

        results = []

        for timestamp, soc in response["points"]:

            results.append(
                {
                    "timestamp": timestamp,
                    "soc": float(soc),
                }
            )

        return results