CREATE TABLE supplier (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL UNIQUE
            );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE account (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL UNIQUE,
                supplier_id INTEGER NOT NULL,
                active_from TEXT,
                active_to TEXT,
                FOREIGN KEY (supplier_id)
                    REFERENCES supplier(supplier_id)
            );
CREATE TABLE meter (
                meter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                identifier TEXT NOT NULL,
                serial_number TEXT NOT NULL,
                is_export INTEGER NOT NULL,
                fuel TEXT NOT NULL,
                FOREIGN KEY (account_id)
                    REFERENCES account(account_id),
                UNIQUE(identifier, serial_number)
            );
CREATE TABLE tariff (
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
            );
CREATE TABLE reading (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                interval_start TEXT NOT NULL,
                energy REAL NOT NULL,
                meter_id INTEGER NOT NULL,
                FOREIGN KEY (meter_id)
                    REFERENCES meter(meter_id),
                UNIQUE(interval_start, meter_id)
            );
CREATE TABLE rate_period (
                period_id INTEGER PRIMARY KEY AUTOINCREMENT,
                interval_start TEXT NOT NULL,
                meter_id INTEGER NOT NULL,
                cost REAL NOT NULL,
                FOREIGN KEY (meter_id)
                    REFERENCES meter(meter_id),
                UNIQUE(interval_start, meter_id)
            );
CREATE TABLE sensor (
                sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_name TEXT NOT NULL,
                sensor_entity_id TEXT NOT NULL UNIQUE
            );
CREATE TABLE tank_temps (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                sensor_id INTEGER NOT NULL,
                FOREIGN KEY (sensor_id)
                    REFERENCES sensor(sensor_id),
                UNIQUE(timestamp, sensor_id)
            );
CREATE TABLE location (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                UNIQUE(latitude, longitude)
            );
CREATE TABLE weather (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL,
                cloud_cover INTEGER,
                solar_radiation REAL,
                FOREIGN KEY (location_id)
                    REFERENCES location(location_id),
                UNIQUE(timestamp, location_id)
            );
CREATE TABLE battery_soc (
                soc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL UNIQUE,
                soc REAL NOT NULL
            );