import sqlite3

# ----------------------------------------------------------------------------
#  SQLiteBackend
#  Provides a technology-specific database backend to the database class
# ----------------------------------------------------------------------------
class SQLiteBackend:

    #-------------------------------------------------------------------------
    # Class Constructor
    #-------------------------------------------------------------------------
    def __init__(self, filename: str, ):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self._create_tables()
        self.connection.commit()

    #-------------------------------------------------------------------------
    # Close the DB
    #-------------------------------------------------------------------------
    def close(self):

        self.cursor.close()
        self.connection.close()

    #-------------------------------------------------------------------------
    # Create a supplier record
    #-------------------------------------------------------------------------
    def load_supplier(
        self,
        supplier_name: str,
    ):

        self.cursor.execute(
            """
            SELECT supplier_id
            FROM supplier
            WHERE supplier_name = ?
            """,
            (
                supplier_name,
            ),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO supplier (
                supplier_name
            )
            VALUES (?)
            """,
            (
                supplier_name,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    #-------------------------------------------------------------------------
    # Create an account record
    #-------------------------------------------------------------------------
    def load_account(
        self,
        account_number: str,
        supplier_id: int,
        active_from: str,
        active_to: str | None,
    ):

        self.cursor.execute(
            """
            SELECT account_id
            FROM account
            WHERE account_number = ?
            """,
            (
                account_number,
            ),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO account (
                account_number,
                supplier_id,
                active_from,
                active_to
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                account_number,
                supplier_id,
                active_from,
                active_to,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    #-------------------------------------------------------------------------
    # Create a meter record
    #-------------------------------------------------------------------------
    def load_meter(
        self,
        account_id: int,
        identifier: str,
        serial_number: str,
        is_export: bool,
        fuel: str,
    ):

        self.cursor.execute(
            """
            SELECT meter_id
            FROM meter
            WHERE identifier = ?
            AND serial_number = ?
            """,
            (
                identifier,
                serial_number,
            ),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO meter (
                account_id,
                identifier,
                serial_number,
                is_export,
                fuel
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                account_id,
                identifier,
                serial_number,
                is_export,
                fuel,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    #-------------------------------------------------------------------------
    # Create a tariff record
    #-------------------------------------------------------------------------
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

        self.cursor.execute(
            """
            SELECT tariff_id
            FROM tariff
            WHERE meter_id = ?
            AND tariff_code = ?
            AND applies_from = ?
            """,
            (
                meter_id,
                tariff_code,
                applies_from,
            ),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO tariff (
                tariff_code,
                product_code,
                tariff_name,
                tariff_type,
                applies_from,
                applies_to,
                meter_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tariff_code,
                product_code,
                tariff_name,
                tariff_type,
                applies_from,
                applies_to,
                meter_id,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    #-------------------------------------------------------------------------
    # Write tank temperatures to the database
    #-------------------------------------------------------------------------
    def load_tank_temperature(
        self,
        sensor_entity_id: str,
        history: list,
    ):

        sensor_pk = self._get_or_create_sensor(
            sensor_entity_id,
        )

        rows = []

        for reading in history:

            rows.append(
                (
                    reading["timestamp"],
                    reading["value"],
                    sensor_pk,
                )
            )

        self.cursor.executemany(
            """
            INSERT OR REPLACE INTO tank_temps (
                timestamp,
                value,
                sensor_id
            )
            VALUES (?, ?, ?)
            """,
            rows,
        )

        self.connection.commit()

    #-------------------------------------------------------------------------
    # Write energy consumption readings to the database
    #-------------------------------------------------------------------------
    def load_meter_readings(
        self,
        meter_id: int,
        history: list,
    ):

        rows = []

        for reading in history:

            rows.append(
                (
                    reading["interval_start"],
                    reading["reading"],
                    meter_id,
                )
            )

        self.cursor.executemany(
            """
            INSERT OR REPLACE INTO reading (
                interval_start,
                energy,
                meter_id
            )
            VALUES (?, ?, ?)
            """,
            rows,
        )

        self.connection.commit()

    #-------------------------------------------------------------------------
    # write energy cost information to the database
    #-------------------------------------------------------------------------
    def load_energy_rate(
        self,
        meter_id: int,
        history: list,
    ):

        rows = []

        for period in history:

            rows.append(
                (
                    period["interval_start"],
                    period["rate"],
                    meter_id,
                )
            )

        self.cursor.executemany(
            """
            INSERT OR REPLACE INTO rate_period (
                interval_start,
                cost,
                meter_id
            )
            VALUES (?, ?, ?)
            """,
            rows,
        )

        self.connection.commit()

    #-------------------------------------------------------------------------
    # Write weather observations to the database
    #-------------------------------------------------------------------------
    def load_weather(self, weather_config, history: list, ):

        location_id = self._get_or_create_location(
            latitude=weather_config.latitude,
            longitude=weather_config.longitude,
        )

        rows = []

        for reading in history:

            rows.append(
                (
                    location_id,
                    reading["timestamp"],
                    reading["temperature"],
                    reading["cloud_cover"],
                    reading["solar_radiation"],
                )
            )

        self.cursor.executemany(
            """
            INSERT OR REPLACE INTO weather (
                location_id,
                timestamp,
                temperature,
                cloud_cover,
                solar_radiation
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )

        self.connection.commit()

    # ------------------------------------------------------------------
    def load_battery_soc(
        self,
        history,
    ):

        rows = [
            (
                reading["timestamp"],
                reading["soc"],
            )
            for reading in history
        ]

        self.cursor.executemany(
            """
            INSERT OR REPLACE
            INTO battery_soc (
                timestamp,
                soc
            )
            VALUES (?, ?)
            """,
            rows,
        )

        self.connection.commit()

    def get_account_id(self, account_number: str):
        self.cursor.execute(
            """
            SELECT account_id FROM account WHERE account_number = ?
            """,
            (account_number,),)
        row = self.cursor.fetchone()
        if row is None:
            raise ValueError (f"Unknown account: {account_number}")
        return row[0]

    def get_active_meters(
        self,
        account_id: int,
    ):

        self.cursor.execute(
            """
            SELECT
                meter_id,
                account_id,
                identifier,
                serial_number,
                is_export,
                fuel
            FROM meter
            WHERE account_id = ?
            ORDER BY meter_id
            """,
            (
                account_id,
            ),
        )

        rows = self.cursor.fetchall()

        return [
            {
                "meter_id": row[0],
                "account_id": row[1],
                "identifier": row[2],
                "serial_number": row[3],
                "is_export": bool(row[4]),
                "fuel": row[5],
            }
            for row in rows
        ]

    def get_active_tariff(
        self,
        meter_id: int,
        day: str,
    ):

        self.cursor.execute(
            """
            SELECT
                tariff_id,
                tariff_code,
                product_code,
                tariff_name,
                tariff_type,
                applies_from,
                applies_to,
                meter_id
            FROM tariff
            WHERE meter_id = ?
            AND applies_from <= ?
            AND (
                    applies_to IS NULL
                    OR applies_to > ?
                )
            ORDER BY applies_from DESC
            LIMIT 1
            """,
            (
                meter_id,
                day,
                day,
            ),
        )

        row = self.cursor.fetchone()

        if row is None:
            return None

        return {
            "tariff_id": row[0],
            "tariff_code": row[1],
            "product_code": row[2],
            "tariff_name": row[3],
            "tariff_type": row[4],
            "applies_from": row[5],
            "applies_to": row[6],
            "meter_id": row[7],
        }

    #-------------------------------------------------------------------------
    # Crete tables if they don't exist
    #-------------------------------------------------------------------------
    def _create_tables(self):

        # --------------------------------------------------------------------
        # Supplier
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL UNIQUE
            )
        """)

        # --------------------------------------------------------------------
        # Account
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS account (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL UNIQUE,
                supplier_id INTEGER NOT NULL,
                active_from TEXT,
                active_to TEXT,
                FOREIGN KEY (supplier_id)
                    REFERENCES supplier(supplier_id)
            )
        """)

        # --------------------------------------------------------------------
        #  Meter
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS meter (
                meter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                identifier TEXT NOT NULL,
                serial_number TEXT NOT NULL,
                is_export INTEGER NOT NULL,
                fuel TEXT NOT NULL,
                FOREIGN KEY (account_id)
                    REFERENCES account(account_id),
                UNIQUE(identifier, serial_number)
            )
        """)

        # --------------------------------------------------------------------
        # Tariff
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tariff (
                tariff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tariff_code TEXT NOT NULL,
                product_code TEXT NOT NULL,
                tariff_name TEXT,
                tariff_type TEXT,
                applies_from TEXT NOT NULL,
                applies_to TEXT,
                meter_id INTEGER NOT NULL,
                FOREIGN KEY (meter_id)
                    REFERENCES meter(meter_id),
                UNIQUE (
                    meter_id,
                    tariff_code,
                    applies_from
                )
            )
        """)

        # --------------------------------------------------------------------
        # Reading (energy meter)
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                interval_start TEXT NOT NULL,
                energy REAL NOT NULL,
                meter_id INTEGER NOT NULL,
                FOREIGN KEY (meter_id)
                    REFERENCES meter(meter_id),
                UNIQUE(interval_start, meter_id)
            )
        """)

        # --------------------------------------------------------------------
        # Rate Period (energy meter)
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_period (
                period_id INTEGER PRIMARY KEY AUTOINCREMENT,
                interval_start TEXT NOT NULL,
                meter_id INTEGER NOT NULL,
                cost REAL NOT NULL,
                FOREIGN KEY (meter_id)
                    REFERENCES meter(meter_id),
                UNIQUE(interval_start, meter_id)
            )
        """)

        # --------------------------------------------------------------------
        # Sensor
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor (
                sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_name TEXT NOT NULL,
                sensor_entity_id TEXT NOT NULL UNIQUE
            )
        """)

        # --------------------------------------------------------------------
        # Tank Temps
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tank_temps (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                sensor_id INTEGER NOT NULL,
                FOREIGN KEY (sensor_id)
                    REFERENCES sensor(sensor_id),
                UNIQUE(timestamp, sensor_id)
            )
        """)

        # --------------------------------------------------------------------
        # Location
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS location (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                UNIQUE(latitude, longitude)
            )
        """)

        # --------------------------------------------------------------------
        # Weather
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL,
                cloud_cover INTEGER,
                solar_radiation REAL,
                FOREIGN KEY (location_id)
                    REFERENCES location(location_id),
                UNIQUE(timestamp, location_id)
            )
        """)

        # --------------------------------------------------------------------
        # Battery SoC
        # --------------------------------------------------------------------
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS battery_soc (
                soc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL UNIQUE,
                soc REAL NOT NULL
            )
        """)
        
        self.connection.commit()

    #-------------------------------------------------------------------------
    # Return a location ID from a lat/long, or create one if it doesn't exist
    #-------------------------------------------------------------------------
    def _get_or_create_location(
        self,
        latitude: float,
        longitude: float,
    ):

        self.cursor.execute(
            """
            SELECT location_id
            FROM location
            WHERE latitude = ?
            AND longitude = ?
            """,
            (
                latitude,
                longitude,
            ),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO location (
                latitude,
                longitude
            )
            VALUES (?, ?)
            """,
            (
                latitude,
                longitude,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    def _get_or_create_sensor(
        self,
        sensor_entity_id: str,
    ):

        self.cursor.execute(
            """
            SELECT sensor_id
            FROM sensor
            WHERE sensor_entity_id = ?
            """,
            (
                sensor_entity_id,
            ),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO sensor (
                sensor_name,
                sensor_entity_id
            )
            VALUES (?, ?)
            """,
            (
                sensor_entity_id,
                sensor_entity_id,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid