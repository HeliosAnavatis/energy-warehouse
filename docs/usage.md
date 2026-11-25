# Usage

## Overview

This guide covers installation, configuration, scheduling, containerisation and common operational tasks.

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/<your-user>/energy.git
cd energy
```

---

## Install Dependencies

```bash
pip install .
```

For development:

```bash
pip install -e .
```

---

# Configuration

Copy and customise:

```text
config.toml
secrets/secrets.toml
```

See:

```text
docs/config.md
```

for a full description of every configuration option.

---

# Database Setup

## SQLite

SQLite requires no additional setup.

The database file will be created automatically.

Example:

```toml
[database]
engine = "sqlite"

[sqlite]
path = "data/energy.db"
```

---

## PostgreSQL

PostgreSQL must be installed and configured separately.

Recommended:

- PostgreSQL 16+
- Dedicated database
- Dedicated user account

Official PostgreSQL installation guide:

https://www.postgresql.org/docs/current/tutorial-install.html

Typical configuration:

```toml
[database]
engine = "postgres"

[postgres]
host = "localhost"
port = 5432
database = "energy"
schema = "utility"
```

The application will automatically create tables within the configured schema.

---

# Initial Setup

## Load Account Information

Before collecting Octopus data, account information must be loaded.

Run:

```bash
python3 tools/load_account.py
```

This will:

- Retrieve account information from Octopus
- Create supplier records
- Create account records
- Create meter records
- Create tariff records

This only needs to be performed when initially configuring the system or when significant account changes occur.

---

## Load Historical Data

The primary ingestion script collects a single day at a time.

To backfill historical data use:

```bash
python3 tools/ingest_history.py \
    2025-01-01 \
    2025-12-31
```

The script repeatedly invokes the daily ingestion process and is intended for initial population of the warehouse.

This may take a considerable amount of time depending on the size of the date range.

---

# Daily Ingestion

## Collect a Single Day

Example:

```bash
python3 ingest_day.py 2026-11-22
```

This collects:

- Weather
- Tank temperatures
- Octopus readings
- Octopus tariffs
- Solar Assistant readings
- Battery SoC

for the specified day.

---

# Including and Excluding Modules

The collector supports selective execution.

---

## Include Specific Modules

Example:

```bash
python3 ingest_day.py \
    2026-11-22 \
    -i weather,octopus
```

Only the specified modules will run.

Useful for:

- Testing
- Troubleshooting
- Partial backfills

---

## Exclude Specific Modules

Example:

```bash
python3 ingest_day.py \
    2026-11-22 \
    -x solarassistant
```

All modules except Solar Assistant will run.

Useful when:

- A source system is unavailable
- A module is being upgraded
- Troubleshooting is in progress

---

# Scheduling

### Linux Cron

The ingestion script expects a specific date to collect.

A common pattern is to calculate yesterday's date within the cron job and pass it to the script.

Example:

```cron
15 00 * * * cd /srv/energy && \
python3 ingest_day.py $(date -d "yesterday" +\%F) \
>> logs/ingest.log 2>&1
```

This runs every day at 00:15 and collects data for the previous day.

The expanded command will look similar to:

```bash
python3 ingest_day.py 2026-11-23
```

which avoids collecting a day that is still in progress.

### Cron Notes

The `%` character has special meaning in cron and must be escaped:

```cron
+\%F
```

rather than:

```cron
+%F
```

### Logging

The example commands append output to:

```text
logs/ingest.log
```

You may prefer to rotate logs using:

```text
logrotate
```

or manage execution using a systemd service and timer instead.

---

## Systemd Timer

You will need to work out how to do this for yourself, because it isn't what I'm using but it is a more modern approach than cron.

Advantages:

- Better logging
- Failure detection
- Automatic restart behaviour

---

# Containerisation

Container support is planned.

A typical deployment will consist of:

```text
+-------------------+
| Energy Container  |
+-------------------+
         |
         +----------------+
                          |
                          ▼
                PostgreSQL Database
```

Benefits:

- Simplified deployment
- Environment isolation
- Easier upgrades
- Reproducible installations

---

# Database Migration

The project includes a database migration utility.

SQLite to PostgreSQL:

```bash
python3 tools/migrate_db.py \
    --source sqlite \
    --target postgres
```

Replace destination data:

```bash
python3 tools/migrate_db.py \
    --source sqlite \
    --target postgres \
    --replace
```

See:

```text
docs/database.md
```

for full migration details.

---

# Accessing Data From Excel

The warehouse has been designed to support analysis within Excel.

---

## SQLite

Install an SQLite ODBC driver.

Create an ODBC data source pointing to:

```text
data/energy.db
```

Within Excel:

```text
Data
    →
Get Data
    →
From Database
    →
From ODBC
```

---

## PostgreSQL

Install the PostgreSQL ODBC driver.

Create an ODBC connection using:

```text
Host
Port
Database
User
Password
```

Then in Excel:

```text
Data
    →
Get Data
    →
From Database
    →
From PostgreSQL Database
```

or

```text
From ODBC
```

depending on your installation.

---

# Useful SQL Queries

## Daily Electricity Cost

Example import meter:

```sql
SELECT
    DATE(r.interval_start) AS day,
    ROUND(
        SUM(
            r.energy * rp.cost
        ),
        2
    ) AS daily_cost
FROM reading r
JOIN rate_period rp
    ON r.interval_start = rp.interval_start
   AND r.meter_id = rp.meter_id
WHERE r.meter_id = 1
GROUP BY DATE(r.interval_start)
ORDER BY day;
```

---

## Daily Electricity Consumption

```sql
SELECT
    DATE(interval_start) AS day,
    ROUND(
        SUM(energy),
        2
    ) AS kwh
FROM reading
WHERE meter_id = 1
GROUP BY DATE(interval_start)
ORDER BY day;
```

---

## Daily Solar Generation

```sql
SELECT
    DATE(interval_start) AS day,
    ROUND(
        SUM(energy),
        2
    ) AS solar_kwh
FROM reading
WHERE meter_id = 4
GROUP BY DATE(interval_start)
ORDER BY day;
```

---

## Daily Battery Throughput

```sql
SELECT
    DATE(interval_start) AS day,
    ROUND(
        SUM(ABS(energy)),
        2
    ) AS battery_kwh
FROM reading
WHERE meter_id = 6
GROUP BY DATE(interval_start)
ORDER BY day;
```

---

## Daily Grid Import / Export

```sql
SELECT
    DATE(interval_start) AS day,
    ROUND(
        SUM(
            CASE
                WHEN energy > 0
                THEN energy
                ELSE 0
            END
        ),
        2
    ) AS import_kwh,
    ROUND(
        SUM(
            CASE
                WHEN energy < 0
                THEN ABS(energy)
                ELSE 0
            END
        ),
        2
    ) AS export_kwh
FROM reading
WHERE meter_id = 7
GROUP BY DATE(interval_start)
ORDER BY day;
```

---

## Average Daily Temperature

```sql
SELECT
    DATE(timestamp) AS day,
    ROUND(
        AVG(temperature),
        1
    ) AS avg_temperature
FROM weather
GROUP BY DATE(timestamp)
ORDER BY day;
```

---

## Battery State of Charge

```sql
SELECT
    timestamp,
    soc
FROM battery_soc
ORDER BY timestamp;
```

---

## Tank Temperature Profile

```sql
SELECT
    tt.timestamp,
    s.sensor_name,
    tt.value
FROM tank_temps tt
JOIN sensor s
    ON s.sensor_id = tt.sensor_id
ORDER BY tt.timestamp;
```

---

# Troubleshooting

## Module Fails

Run the module independently:

```bash
python3 ingest_day.py 2026-11-22 -i weather
```

or:

```bash
python3 ingest_day.py 2026-11-22 -i octopus
```

to isolate the source of the error.

---

## Verify Database Connectivity

SQLite:

```bash
sqlite3 data/energy.db
```

PostgreSQL:

```bash
psql -h HOST -d DATABASE -U USER
```

---

## Verify Data Collection

Check the latest readings:

```sql
SELECT MAX(interval_start)
FROM reading;
```

```sql
SELECT MAX(timestamp)
FROM weather;
```

These values should advance after successful ingestion.

---

# Further Reading

- docs/config.md
- docs/database.md
- docs/tools.md
- docs/tests.md
- docs/architecture.md