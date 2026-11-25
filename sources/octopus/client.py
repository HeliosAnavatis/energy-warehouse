import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

class OctopusClient:

    def __init__(
        self,
        base_url: str,
        account_number: str,
        api_key: str,
        timeout: int = 30,
    ):

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.account_number = account_number
        self.api_key = api_key

        self.headers = {
            "Content-Type": "application/json",
        }

    #--------------------------------------------------------------------------
    def get_account(self):

        response = requests.get(
            f"{self.base_url}/accounts/{self.account_number}",
            headers=self.headers,
            timeout=self.timeout,
            auth=(self.api_key, ""),
        )

        response.raise_for_status()

        return response.json()

    #--------------------------------------------------------------------------
    def get_product(self, product_name: str):
        response = requests.get(
            f"{self.base_url}/products/{product_name}",
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    #--------------------------------------------------------------------------
    # TODO: Move this to a utils helper module as it is only contains business logic and not API calls """
    def tariff_to_product_code(self, tariff_code: str) -> str:

        """ Strip off the first 2 fields of the tariff code  """
        product_code = "-".join(tariff_code.split("-")[2:])

        """ Now strip off the last field of the product code """
        return "-".join(product_code.split("-")[:-1])

    #--------------------------------------------------------------------------
    def get_readings(self, meter_point: str, meter_serial: str, meter_fuel: str, start: str,end: str):
        meter_fuel = meter_fuel.upper()

        if meter_fuel not in ("E", "G"):

            raise ValueError(
                f"Unsupported fuel type "
                f"'{meter_fuel}'."
            )
        
        if meter_fuel == "E":
            url = (
                f"{self.base_url}/electricity-meter-points/{meter_point}/meters/{meter_serial}/consumption"
            )
        elif meter_fuel == "G":
            url = (
                f"{self.base_url}/gas-meter-points/{meter_point}/meters/{meter_serial}/consumption"
            )

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
            auth=(self.api_key, ""),
            params={
                "period_from": start,
                "period_to": end,
            }
        )
        # TODO: Handle pagination if we ever request a large amount of data. The Octopus API will return a maximum of 100 records per request.
        response.raise_for_status()
        return response.json()

    #--------------------------------------------------------------------------
    def get_flexible_unit_rates(
        self,
        tariff_code: str,
        start: str,
        end: str,
    ):

        response = requests.get(
            f"{self.base_url}/products/"
            f"{self.tariff_to_product_code(tariff_code)}"
            f"/electricity-tariffs/"
            f"{tariff_code}"
            f"/standard-unit-rates",
            headers=self.headers,
            timeout=self.timeout,
            auth=(self.api_key, ""),
            params={
                "period_from": start,
                "period_to": end,
            },
        )

        response.raise_for_status()

        # TODO: Handle pagination if we ever request
        # more than a day's data.

        return response.json()

    #--------------------------------------------------------------------------
    def get_standard_unit_rates(
        self,
        tariff_code: str,
        active_at: str,
    ):

        response = requests.get(
            f"{self.base_url}/products/"
            f"{self.tariff_to_product_code(tariff_code)}",
            headers=self.headers,
            timeout=self.timeout,
            params={
                "active_at": active_at,
            },
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------------------------------
    def get_gas_unit_rates(
        self,
        link: str,
        active_from: str,
        active_to: str
    ):

        response = requests.get(
            link,
            headers=self.headers,
            timeout=self.timeout,
            params={
                "period_from": active_from,
                "period_to": active_to,
            },
        )

        response.raise_for_status()

        return response.json()