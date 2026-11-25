# Database

## Overview

The Energy Data Warehouse supports both SQLite and PostgreSQL through a common database abstraction layer.

Application code never interacts directly with a specific database engine. Instead, all database operations are performed through the `Database` class, which delegates work to the active backend.

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

The active backend is selected in `config.toml`:

```toml
[database]
engine = "sqlite"
```

or:

```toml
[database]
engine = "postgres"
```

This allows the application to operate against either database engine without changes to the ingestion or source modules. It is possible to specify the connection parameters to both databases simultaneously in the config and secrets; the system will only use the engine specified by the `engine` setting, thus making it very easy to switch modes during development.

---

# Database Schema

The same logical schema is implemented in both SQLite and PostgreSQL.

## Supplier

Stores energy suppliers.

| Column | Description |
|----------|----------|
| supplier_id | Primary key |
| supplier_name | Supplier name |

---

## Account

Stores supplier account information.

| Column | Description |
|----------|----------|
| account_id | Primary key |
| account_number | Supplier account number |
| supplier_id | Related supplier |
| active_from | Account start date |
| active_to | Account end date |

Relationships:

```text
supplier
    └── account
```

---

## Meter

Represents physical and virtual meters.

| Column | Description |
|----------|----------|
| meter_id | Primary key |
| account_id | Owning account |
| identifier | MPAN, MPRN or virtual meter identifier |
| serial_number | Meter serial number |
| is_export | Import/export flag |
| fuel | Meter type |

Relationships:

```text
account
    └── meter
```

---

## Tariff

Stores tariff metadata and tariff history.

| Column | Description |
|----------|----------|
| tariff_id | Primary key |
| tariff_code | Octopus tariff code |
| product_code | Octopus product code |
| tariff_name | Display name |
| tariff_type | Tariff type |
| applies_from | Effective start |
| applies_to | Effective end |
| meter_id | Related meter |

A meter may have multiple tariffs over time.

---

## Reading

Stores half-hourly consumption and generation data.

| Column | Description |
|----------|----------|
| reading_id | Primary key |
| interval_start | Interval start timestamp |
| energy | Energy value (kWh) |
| meter_id | Related meter |

Unique constraint:

```text
(interval_start, meter_id)
```

---

## Rate Period

Stores historical tariff rates for each half-hourly period. This allows historical pricing to be preserved even when changing suppliers or tariffs.

| Column | Description |
|----------|----------|
| period_id | Primary key |
| interval_start | Interval start timestamp |
| cost | Energy cost |
| meter_id | Related meter |

Unique constraint:

```text
(interval_start, meter_id)
```

---

## Sensor

Stores Home Assistant sensor metadata.

| Column | Description |
|----------|----------|
| sensor_id | Primary key |
| sensor_name | Display name |
| sensor_entity_id | Home Assistant entity |

---

## Tank Temperatures

Stores hot water tank temperature readings.

| Column | Description |
|----------|----------|
| reading_id | Primary key |
| timestamp | Reading timestamp |
| value | Temperature |
| sensor_id | Related sensor |

Unique constraint:

```text
(timestamp, sensor_id)
```

---

## Location

Stores weather observation locations.

| Column | Description |
|----------|----------|
| location_id | Primary key |
| latitude | Latitude |
| longitude | Longitude |

Unique constraint:

```text
(latitude, longitude)
```

---

## Weather

Stores weather observations.

| Column | Description |
|----------|----------|
| reading_id | Primary key |
| location_id | Related location |
| timestamp | Observation time |
| temperature | Air temperature |
| cloud_cover | Cloud cover percentage |
| solar_radiation | Solar radiation |

Unique constraint:

```text
(timestamp, location_id)
```

---

## Battery State of Charge

Stores battery SoC history.

| Column | Description |
|----------|----------|
| soc_id | Primary key |
| timestamp | Reading time |
| soc | State of charge percentage |

Unique constraint:

```text
timestamp
```

---

# Schema Relationships

```text
supplier
    │
    ▼
account
    │
    ▼
meter
    │
    ├── tariff
    │
    ├── reading
    │
    └── rate_period


sensor
    │
    ▼
tank_temps


location
    │
    ▼
weather


battery_soc
```

---

# SQLite vs PostgreSQL

Both implementations provide the same logical schema and application behaviour.

The underlying implementations differ where required by the database engine.

## Primary Keys

SQLite uses:

```sql
INTEGER PRIMARY KEY AUTOINCREMENT
```

PostgreSQL uses:

```sql
BIGSERIAL PRIMARY KEY
```

PostgreSQL therefore supports significantly larger row counts.

---

## UPSERT Behaviour

The application is designed to be idempotent.

Running an ingestion multiple times must not create duplicate rows.

SQLite implements this using:

```sql
INSERT OR REPLACE
```

PostgreSQL implements the same behaviour using:

```sql
INSERT ...
ON CONFLICT (...)
DO UPDATE
```

Although the SQL differs, the behaviour seen by the application is identical.

---

## Data Types

SQLite uses flexible typing.

Examples:

```sql
TEXT
REAL
INTEGER
```

PostgreSQL uses strongly typed columns.

Examples:

```sql
TEXT
DOUBLE PRECISION
BOOLEAN
TIMESTAMP
TIMESTAMPTZ
BIGINT
```

PostgreSQL therefore provides stronger validation and will often detect data-quality issues which SQLite may silently accept.

---

## Timestamp Handling

Several tables intentionally use different timestamp types.

### TIMESTAMP

Used for local observation timestamps where timezone information is not significant:

```text
weather.timestamp
tank_temps.timestamp
battery_soc.timestamp
```

### TIMESTAMPTZ

Used for tariff and energy data where timezone information must be preserved:

```text
tariff.applies_from
tariff.applies_to
reading.interval_start
rate_period.interval_start
```

This distinction is particularly important around daylight saving time transitions.

---

## Schemas

SQLite stores everything within a single database file.

PostgreSQL supports named schemas.

The application creates and uses a configurable schema:

```toml
[postgres]
schema = "utility"
```

Allowing multiple independent Energy databases to coexist inside the same PostgreSQL instance.

---

# Database Migration

The Energy Data Warehouse includes a migration tool allowing data transfer between SQLite and PostgreSQL.  Migrations can be made in either direction; PostgreSQL to SQLite, or vice versa.

The migration tool:

- Creates destination tables when required
- Copies all supported tables
- Preserves primary keys
- Preserves foreign key relationships
- Preserves timestamps
- Preserves historical tariff data
- Verifies row counts after migration

---

## Example

Migrate SQLite to PostgreSQL:

```bash
python3 tools/migrate_db.py \
    --source sqlite \
    --target postgres
```

Replace data in the destination:

```bash
python3 tools/migrate_db.py \
    --source sqlite \
    --target postgres \
    --replace
```

---

## Verification

After migration, the tool performs a table-by-table row count comparison.

Example:

```text
supplier                 2 -> 2 OK
account                  2 -> 2 OK
weather             16,296 -> 16,296 OK
reading            124,264 -> 124,264 OK
```

A migration is only considered successful when all table counts match.

---

# Recommended Database Engine

## SQLite

Recommended for:

- Development
- Testing
- Small installations
- Single-user usage

Advantages:

- No server installation
- Simple backup strategy
- Very low administration overhead

---

## PostgreSQL

Recommended for:

- Long-term deployments
- Large historical datasets
- Multi-user access
- Reporting and analytics workloads
- Containerised installations

Advantages:

- Strong type system
- Better data integrity enforcement
- Better scalability
- Native schema support
- More advanced querying capabilities

---

# Future Development

Potential future enhancements include:

- Database views for reporting
- Materialised summary tables
- Automated database health checks
- Migration regression testing
- Performance benchmarking
- Additional database backends