# Database Architecture

## Overview

The Energy application uses a database abstraction layer that allows the same application code to operate against either SQLite or PostgreSQL.

Application code interacts only with the `Database` class. Database-specific behaviour is implemented by backend classes.

```text
Application
    │
    ▼
Database
    │
    ├── SQLiteBackend
    │
    └── PostgreSQLBackend
```

The active backend is selected through the configuration file.

```toml
[database]
engine = "sqlite"
```

or

```toml
[database]
engine = "postgres"
```

---

## Database Backends

### SQLite

SQLite is intended for:

- development
- testing
- small installations
- single-user deployments

Database data is stored in a local file.

### PostgreSQL

PostgreSQL is intended for:

- larger datasets
- multi-user environments
- production deployments
- future containerised installations

The PostgreSQL backend mirrors the SQLite schema and behaviour as closely as possible.

---

## Schema

### Supplier

Energy suppliers.  There is a placeholder supplier for the solarassistant readings because these are treated as meter readings in the same way as the energy supplier.  This puts all meter readings (half-hourly kWh figures) in the same table, allowing for easier analysis and comparison.

```text
supplier
```

Examples:

- Octopus Energy
- Home Energy System

---

### Account

Supplier accounts.

```text
account
```

An account belongs to a supplier.  As with suppliers, there is a placeholder account for solarassistant readings.

---

### Meter

Physical or virtual energy meters.

```text
meter
```

Examples:

- Electricity import
- Electricity export
- Gas
- PV generation
- House load
- Battery flow
- Grid flow

A meter belongs to an account.

---

### Tariff

Tariff information associated with a meter.

```text
tariff
```

Stores:

- tariff code
- product code
- effective dates
- tariff metadata

---

### Reading

Energy consumption or generation readings.

```text
reading
```

Each reading is uniquely identified by:

```text
(interval_start, meter_id)
```

---

### Rate Period

Energy pricing information.

```text
rate_period
```

Each rate period is uniquely identified by:

```text
(interval_start, meter_id)
```

---

### Sensor

Home Assistant sensors.

```text
sensor
```

Stores sensor entity IDs and metadata.

---

### Tank Temperatures

Historical hot water tank temperature measurements.

```text
tank_temps
```

Each reading is uniquely identified by:

```text
(timestamp, sensor_id)
```

---

### Location

Weather observation locations.

```text
location
```

Provides a reusable latitude/longitude reference.

---

### Weather

Historical weather observations.

```text
weather
```

Stores:

- temperature
- cloud cover
- solar radiation

Each observation is uniquely identified by:

```text
(timestamp, location_id)
```

---

### Battery State of Charge

Battery charge history.

```text
battery_soc
```

Stores timestamped battery state of charge percentages.

---

## Idempotent Ingestion

All ingestion operations are designed to be idempotent.

Running the same ingest operation multiple times should not create duplicate records.

SQLite achieves this through:

```sql
INSERT OR REPLACE
```

PostgreSQL achieves this through:

```sql
INSERT ... ON CONFLICT DO UPDATE
```

This allows historical backfills and re-processing without requiring manual cleanup.

---

## Migration

The project includes a migration utility which can transfer data between SQLite and PostgreSQL.

Supported migrations:

```text
SQLite → PostgreSQL
PostgreSQL → SQLite
```

The migration utility preserves:

- primary keys
- foreign keys
- timestamps
- historical readings
- tariff history

---

## Future Development

Planned areas for improvement include:

- additional reporting views
- analytical queries
- database performance optimisation
- containerised deployment
- automated migration testing
```