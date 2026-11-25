from utils.config import Config

class Database:

    #--------------------------------------------------------------------------
    def __init__(self, config: Config):
        self.config = config
        self.backend = self._get_database(config)

    #--------------------------------------------------------------------------
    def close(self):
        self.backend.close()

    #--------------------------------------------------------------------------
    def load_supplier(
        self,
        supplier_name: str,
    ):
        return self.backend.load_supplier(
            supplier_name,
        )

    #--------------------------------------------------------------------------
    def load_account(
        self,
        account_number: str,
        supplier_id: int,
        active_from: str,
        active_to: str | None,
    ):
        return self.backend.load_account(
            account_number,
            supplier_id,
            active_from,
            active_to,
        )

    #--------------------------------------------------------------------------
    def load_meter(
        self,
        account_id: int,
        identifier: str,
        serial_number: str,
        is_export: bool,
        fuel: str,
    ):
        return self.backend.load_meter(
            account_id,
            identifier,
            serial_number,
            is_export,
            fuel,
        )

    #--------------------------------------------------------------------------
    def load_tariff(
        self,
        meter_id: int,
        tariff_code: str,
        product_code: str,
        tariff_name: str | None,
        tariff_type: str | None,
        applies_from: str,
        applies_to: str | None,
    ):
        return self.backend.load_tariff(
            meter_id,
            tariff_code,
            product_code,
            tariff_name,
            tariff_type,
            applies_from,
            applies_to,
        )

    #--------------------------------------------------------------------------
    def load_tank_temperature(self, sensor_entity_id: str, history: list):
        self.backend.load_tank_temperature(sensor_entity_id, history)

    def load_meter_readings(self, meter_id: int, history: list):
        self.backend.load_meter_readings(meter_id, history)

    def load_energy_rate(self, tariff_code: str, history: list):
        self.backend.load_energy_rate(tariff_code, history)

    #--------------------------------------------------------------------------
    def load_weather(self, history: list):
        self.backend.load_weather(self.config.weather,  history)

    def load_pv_generation(self, history: list):
        self.backend.load_pv_generation(history)

    def load_battery_state(self, history: list):
        self.backend.load_battery_state(history)

    def get_account_id(self, account_number: str):
        return self.backend.get_account_id(account_number)

    # ------------------------------------------------------------------
    def load_battery_soc(
        self,
        history,
    ):
        self.backend.load_battery_soc(
            history
        )

    def get_meter (self, meter_identifier: str, meter_serial: str):
        # returns the meter record for the given meter_identifier and meter_serial:
        # meter_id, supplier_id, fuel, identifier (mpan/mprn), serial, export flag
        return self.backend.get_meter(meter_identifier, meter_serial)

    def get_active_meters(self, account_id: int, ):
        return self.backend.get_active_meters(account_id, )

    def get_active_tariff(self, meter_id: int, day: str, ):
        return self.backend.get_active_tariff(meter_id, day, )

    #--------------------------------------------------------------------------
    def _get_database(self, config):
        if config.database.engine == "sqlite":
            from database.sqlite import (SQLiteBackend,)
            self.backend = SQLiteBackend(
                config.sqlite.path
            )

        elif config.database.engine == "postgres":
            from database.postgres import (PostgreSQLBackend,)
            self.backend = PostgreSQLBackend(
                host=config.postgres.host,
                port=config.postgres.port,
                database=config.postgres.database,
                username=config.postgres.user,
                password=config.postgres.password,
                schema=config.postgres.schema,
            )
        else:
            raise ValueError(
                f"Unsupported database engine: "
                f"{config.database.engine}"
            )
        return self.backend