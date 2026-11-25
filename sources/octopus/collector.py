from datetime import datetime, timedelta

class OctopusCollector:
    def __init__(self, client):
        self.client = client

    def get_reading_history(
        self,
        meter_point: str,
        meter_serial: str,
        meter_fuel: str,
        start: str,
        end: str,
    ):

        response = self.client.get_readings(
            meter_point,
            meter_serial,
            meter_fuel,
            start,
            end,
        )
        results = list(reversed(response["results"]))
        return [
            {
                "interval_start": r["interval_start"],
                "reading": r["consumption"],
            }
            for r in results
            if r["consumption"] is not None
        ]

    def get_rates(
        self,
        tariff_code: str,
        start: str,
        end: str,
    ):
        product = self.client.get_standard_unit_rates(
            tariff_code=tariff_code,
            active_at=start,
        )

        if tariff_code.startswith("G-"):
            return self._get_gas_rates(
                product,
                tariff_code,
                start,
                end,
            )

        if product.get("four_rate_ev_electricity_tariffs"):
            return self._get_four_rate_rates(
                product,
                tariff_code,
                start,
                end,
            )

        return self._get_single_register_rates(
            product,
            tariff_code,
            start,
            end,
        )

    def _get_region_code(self,tariff_code: str,) -> str:

        return "_" + tariff_code.split("-")[-1]

    def _get_single_register_rates(
        self,
        product,
        tariff_code: str,
        start: str,
        end: str,
    ):

        region = self._get_region_code(tariff_code)

        tariffs = product.get("single_register_electricity_tariffs", {})

        tariff = tariffs.get(region)

        if tariff is None:
            raise ValueError(f"No tariff found for region {region}")

        if "direct_debit_monthly" in tariff:
            tariff_details = tariff["direct_debit_monthly"]
        elif "varying" in tariff:
            tariff_details = tariff["varying"]
        else:
            raise ValueError(f"Unsupported tariff structure: " f"{tariff_code}")

        links = tariff_details.get(
            "links",
            [],
        )

        rate_url = None

        for link in links:

            if link.get("rel") == "standard_unit_rates":
                rate_url = link["href"]
                break

        #
        # Fixed tariff?
        #
        standard_rate = tariff_details.get("standard_unit_rate_inc_vat")

        #
        # If there is no rates endpoint then this must
        # be a fixed tariff.
        #
        if rate_url is None:

            if standard_rate is None:
                raise ValueError(
                    f"Tariff {tariff_code} "
                    f"has neither a fixed rate "
                    f"nor a standard_unit_rates link"
                )

            return self._expand_single_rate(
                tariff,
                start,
                end,
            )

        #
        # Variable tariff with historical rates.
        #
        response = self.client.get_flexible_unit_rates(
            tariff_code,
            start,
            end,
        )

        #
        # If Octopus returned actual rate periods,
        # use them.
        #
        if len(response["results"]) > 0:

            return self._expand_flexible_rates(
                response,
                end,
            )

        #
        # No historical rates returned.
        # Fall back to fixed-rate expansion if
        # one exists.
        #
        if standard_rate is not None:

            return self._expand_single_rate(
                tariff,
                start,
                end,
            )

        raise ValueError(
            f"Tariff {tariff_code} "
            f"returned no historical rates "
            f"and has no standard rate"
        )

    def _get_gas_rates(
        self,
        product,
        tariff_code: str,
        start: str,
        end: str,
    ):
        region = self._get_region_code(tariff_code)

        tariffs = product.get("single_register_gas_tariffs", {})

        region_tariff = tariffs.get(region)

        if region_tariff is None:
            raise ValueError(f"No gas tariff found for region {region_tariff}")

        if "direct_debit_monthly" in region_tariff:
            tariff_details = region_tariff["direct_debit_monthly"]
        elif "varying" in region_tariff:
            tariff_details = region_tariff["varying"]
        else:
            raise ValueError(f"Unsupported tariff structure: " f"{tariff_code}")

        links = tariff_details.get(
            "links",
            [],
        )

        rate_url = None

        for link in links:

            if link.get("rel") == "standard_unit_rates":
                rate_url = link["href"]
                break

        if rate_url is None:
            raise ValueError(f"No gas rate URL found in: " f"{tariff_code}")

        response = self.client.get_gas_unit_rates(
            link["href"],
            start,
            end,
        )

        gas_rate = next(
            (r for r in response["results"] if r["payment_method"] == "DIRECT_DEBIT"),
            None,
        )

        if gas_rate is None:
            gas_rate = next(
                (r for r in response["results"] if r["payment_method"] is None),
                None,
            )

        if gas_rate is None:

            raise ValueError(f"No suitable gas rate found for " f"{tariff_code}")

        return self._expand_gas_rate(
            gas_rate,
            start,
            end,
        )

    def _get_four_rate_rates(
        self,
        product,
        tariff_code: str,
        start: str,
        end: str,
    ):

        region = self._get_region_code(tariff_code)
        tariff = product["four_rate_ev_electricity_tariffs"][region]["direct_debit_monthly"]
        off_peak_rate = tariff["night_unit_rate_inc_vat"] / 100.0
        day_rate = tariff["day_unit_rate_inc_vat"] / 100.0
        start_dt = datetime.fromisoformat(
            start.replace(
                "Z",
                "+00:00",
            )
        )

        end_dt = datetime.fromisoformat(
            end.replace(
                "Z",
                "+00:00",
            )
        )

        current = start_dt
        results = []
        while current <= end_dt:
            minutes = current.hour * 60 + current.minute
            off_peak_start = 23 * 60 + 30
            off_peak_end = 5 * 60 + 30
            if minutes >= off_peak_start or minutes < off_peak_end:
                rate = off_peak_rate
            else:
                rate = day_rate

            results.append(
                {
                    "interval_start": current.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "rate": rate,
                }
            )

            current += timedelta(minutes=30)

        return results

    def _expand_single_rate(
        self,
        tariff,
        start: str,
        end: str,
    ):

        rate = tariff["direct_debit_monthly"]["standard_unit_rate_inc_vat"] / 100.0

        start_dt = datetime.fromisoformat(
            start.replace(
                "Z",
                "+00:00",
            )
        )

        end_dt = datetime.fromisoformat(
            end.replace(
                "Z",
                "+00:00",
            )
        )

        current = start_dt

        results = []

        while current <= end_dt:

            results.append(
                {
                    "interval_start": current.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "rate": rate,
                }
            )

            current += timedelta(minutes=30)

        return results

    def _expand_flexible_rates(
        self,
        response,
        end: str,
    ):

        raw_rates = list(reversed(response["results"]))

        results = []

        end_dt = datetime.fromisoformat(
            end.replace(
                "Z",
                "+00:00",
            )
        )

        for rate in raw_rates:

            valid_from = datetime.fromisoformat(
                rate["valid_from"].replace(
                    "Z",
                    "+00:00",
                )
            )

            if rate["valid_to"] is None:
                valid_to = end_dt
            else:
                valid_to = datetime.fromisoformat(
                    rate["valid_to"].replace(
                        "Z",
                        "+00:00",
                    )
                )

            value = rate["value_inc_vat"] / 100.0

            current = valid_from

            while current < valid_to and current < end_dt:

                results.append(
                    {
                        "interval_start": current.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "rate": value,
                    }
                )

                current += timedelta(minutes=30)

        return results

    def _expand_gas_rate(
        self,
        tariff,
        start: str,
        end: str,
    ):

        rate = tariff["value_inc_vat"] / 100.0

        start_dt = datetime.fromisoformat(
            start.replace(
                "Z",
                "+00:00",
            )
        )

        end_dt = datetime.fromisoformat(
            end.replace(
                "Z",
                "+00:00",
            )
        )

        current = start_dt

        results = []

        while current <= end_dt:

            results.append(
                {
                    "interval_start": current.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "rate": rate,
                }
            )

            current += timedelta(minutes=30)

        return results