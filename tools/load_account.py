#!/usr/bin/env python3

from database.database import Database

from sources.octopus.client import OctopusClient

from utils.config import load_config


def main():

    config = load_config()

    db = Database(config)

    try:

        octopus = OctopusClient(
            base_url=config.octopus.url,
            account_number=config.octopus_secrets.account_number,
            api_key=config.octopus_secrets.api_key,
            timeout=config.octopus.timeout,
        )

        account = octopus.get_account()

        #
        # Supplier
        #

        supplier_id = db.load_supplier(
            "Octopus"
        )

        print(
            f"Supplier ID: {supplier_id}"
        )

        #
        # Accounts / Properties
        #

        for property_ in account["properties"]:

            if property_["moved_out_at"] is not None:
                continue

            account_id = db.load_account(
                account_number=account["number"],
                supplier_id=supplier_id,
                active_from=property_["moved_in_at"],
                active_to=property_["moved_out_at"],
            )

            print(
                f"Account ID: {account_id}"
            )

            #
            # Electricity meters
            #

            for mp in property_.get(
                "electricity_meter_points",
                [],
            ):

                # Electricity uses the LAST meter in the list
                meter = mp["meters"][-1]

                meter_id = db.load_meter(
                    account_id=account_id,
                    identifier=mp["mpan"],
                    serial_number=meter["serial_number"],
                    is_export=mp["is_export"],
                    fuel="E",
                )

                print(
                    f"Electric meter ID: {meter_id}"
                )

                for agreement in mp.get(
                    "agreements",
                    [],
                ):

                    tariff_code = (
                        agreement["tariff_code"]
                    )

                    product_code = (
                        octopus.tariff_to_product_code(
                            tariff_code
                        )
                    )

                    db.load_tariff(
                        meter_id=meter_id,
                        tariff_code=tariff_code,
                        product_code=product_code,
                        tariff_name=None,
                        tariff_type=None,
                        applies_from=agreement[
                            "valid_from"
                        ],
                        applies_to=agreement[
                            "valid_to"
                        ],
                    )

                    print(
                        f"Loaded tariff "
                        f"{tariff_code}"
                    )

            #
            # Gas meters
            #

            for mp in property_.get(
                "gas_meter_points",
                [],
            ):

                # Gas uses the FIRST meter in the list
                meter = mp["meters"][0]

                meter_id = db.load_meter(
                    account_id=account_id,
                    identifier=mp["mprn"],
                    serial_number=meter["serial_number"],
                    is_export=False,
                    fuel="G",
                )

                print(
                    f"Gas meter ID: {meter_id}"
                )

                for agreement in mp.get(
                    "agreements",
                    [],
                ):

                    tariff_code = (
                        agreement["tariff_code"]
                    )

                    product_code = (
                        octopus.tariff_to_product_code(
                            tariff_code
                        )
                    )

                    db.load_tariff(
                        meter_id=meter_id,
                        tariff_code=tariff_code,
                        product_code=product_code,
                        tariff_name=None,
                        tariff_type=None,
                        applies_from=agreement[
                            "valid_from"
                        ],
                        applies_to=agreement[
                            "valid_to"
                        ],
                    )

                    print(
                        f"Loaded tariff "
                        f"{tariff_code}"
                    )


        # --------------------------------------------------------------------
        # Solar Assistant synthetic supplier & account
        # --------------------------------------------------------------------

        supplier_id = db.load_supplier("Home Energy System")
        
        battery_account_id = db.load_account(
            account_number="solar-assistant",
            supplier_id=supplier_id,
            active_from=None,
            active_to=None,
        )

        # --------------------------------------------------------------------
        # Synthetic energy-flow meters
        # --------------------------------------------------------------------

        synthetic_meters = [
            {
                "identifier": "pv-generation",
                "serial_number": "SOLAR",
                "fuel": "S",
                "is_export": False,
            },
            {
                "identifier": "house-load",
                "serial_number": "LOAD",
                "fuel": "L",
                "is_export": False,
            },
            {
                "identifier": "battery-flow",
                "serial_number": "BATTERY",
                "fuel": "B",
                "is_export": False,
            },
            {
                "identifier": "grid-flow",
                "serial_number": "NETWORK",
                "fuel": "N",
                "is_export": False,
            },
        ]

        for meter in synthetic_meters:

            db.load_meter(
                account_id=battery_account_id,
                identifier=meter["identifier"],
                serial_number=meter["serial_number"],
                fuel=meter["fuel"],
                is_export=meter["is_export"],
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()