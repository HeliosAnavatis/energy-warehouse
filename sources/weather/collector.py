from datetime import date, UTC, datetime, timedelta

class WeatherCollector:

    def __init__(self, client,):
        self.client = client

    def get_day_hourly(self, day: date):

        #start_date = datetime.combine(day, datetime.min.time(),)
        #end_date = start_date + timedelta(days=1)

        history = self.client.get_history(
            start_date=day.isoformat(),
            end_date=day.isoformat(),
        )

        hourly = history["hourly"]

        results = []

        for i in range(len(hourly["time"])):

            results.append(
                {
                    "timestamp": hourly["time"][i],
                    "temperature": hourly["temperature_2m"][i],
                    "cloud_cover": hourly["cloud_cover"][i],
                    "solar_radiation": hourly["shortwave_radiation"][i],
                }
            )

        return results