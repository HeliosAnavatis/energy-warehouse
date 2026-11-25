# Tools

## Overview

The `tools/` directory contains administrative and maintenance utilities that are not part of the normal daily ingestion workflow.

These scripts are typically used for:

- Initial system setup
- Historical backfills
- Database migration
- Maintenance operations
- Development activities

Most users will only need to run these tools occasionally.

---

# Available Tools

```text
tools/
├── ingest_history.sh
├── load_account.py
├── migrate_db.py
└── preamble.py
```

---

# load_account.py

## Purpose

Initialises the database with account, meter and tariff information.

This is normally the first tool that should be run after configuring the system.

---

## What It Does

The script:

1. Connects to the Octopus API
2. Retrieves account information
3. Creates supplier records
4. Creates account records
5. Creates electricity meter records
6. Creates gas meter records
7. Creates tariff records
8. Creates Solar Assistant synthetic meters

The following synthetic meters are automatically created: 【1-9a0c72】

```text
pv-generation
house-load
battery-flow
grid-flow
```

These meters are subsequently populated using Solar Assistant data. 【1-9a0c72】

---

## Usage

```bash
python3 tools/load_account.py
```

---

## When To Run

### First Installation

Always run after:

```text
1. Installing the application
2. Creating config.toml
3. Creating secrets.toml
```

---

### Account Changes

Run again if:

- Electricity meters change
- Gas meters change
- Tariffs change significantly
- Supplier account details change

The script is idempotent and can safely be rerun.

---

## Typical Workflow

```bash
python3 tools/load_account.py

python3 ingest_day.py 2026-11-22
```

---

# ingest_history.sh

## Purpose

Populates the warehouse with historical data.

The normal ingestion process loads a single day at a time.

This utility repeatedly invokes:

```text
ingest_day.py
```

over a specified date range.

---

## Usage

```bash
./tools/ingest_history.sh \
    2025-01-01 \
    2025-12-31
```

Optionally specify a delay between days:

```bash
./tools/ingest_history.sh \
    2025-01-01 \
    2025-12-31 \
    5
```

where:

```text
5
```

is the delay in seconds between ingestion runs.

---

## Example

```bash
./tools/ingest_history.sh \
    2026-01-01 \
    2026-01-31
```

This will execute:

```bash
python3 ingest_day.py 2026-01-01
python3 ingest_day.py 2026-01-02
python3 ingest_day.py 2026-01-03
...
python3 ingest_day.py 2026-01-31
```

until the requested range has been processed.

---

## Typical Usage

A common setup workflow is:

```bash
python3 tools/load_account.py

./tools/ingest_history.sh \
    2025-01-01 \
    2026-11-30
```

followed by normal scheduled daily ingestion.

---

# migrate_db.py

## Purpose

Transfers data between SQLite and PostgreSQL.

This is primarily intended for:

- Migration to PostgreSQL
- Database upgrades
- Testing
- Development

The tool supports migration in both directions.

---

## Supported Migrations

```text
SQLite → PostgreSQL
PostgreSQL → SQLite
```

---

## Usage

SQLite to PostgreSQL:

```bash
python3 tools/migrate_db.py \
    --source sqlite \
    --target postgres \
    --replace
```

PostgreSQL to SQLite:

```bash
python3 tools/migrate_db.py \
    --source postgres \
    --target sqlite \
    --replace
```

---

## Safety Features

The migration tool intentionally refuses to overwrite data unless:

```bash
--replace
```

is specified.

This helps prevent accidental data loss.

---

## What Gets Migrated

The following tables are copied:

```text
supplier
account
meter
tariff
sensor
location
tank_temps
weather
battery_soc
reading
rate_period
```

---

## Verification

After migration the tool verifies row counts between source and destination databases and reports any discrepancies.

Example:

```text
supplier                 2 -> 2 OK
account                  2 -> 2 OK
weather             16,296 -> 16,296 OK
reading            124,264 -> 124,264 OK
```

---

## Typical Migration Workflow

1. Stop ingestion.
2. Backup both databases.
3. Perform migration.
4. Verify row counts.
5. Switch the active backend in `config.toml`.
6. Run a test ingestion.

See:

```text
docs/database.md
```

for detailed migration information.

---

# preamble.py

## Purpose

Development helper used by standalone tools.

The file ensures that scripts executed from within the `tools/` directory can import modules from the project root.

---

## Typical Usage

Import at the top of a tool:

```python
from tools.preamble import *
```

This adjusts `sys.path` so that imports such as:

```python
from database.database import Database
from utils.config import load_config
```

work correctly regardless of where the script is executed from.

---

# Creating New Tools

Administrative utilities should generally be placed in:

```text
tools/
```

rather than the main application code.

Examples include:

```text
backup_db.py
check_data.py
export_csv.py
repair_readings.py
```

Recommended pattern:

```python
from tools.preamble import *

from database.database import Database
from utils.config import load_config

def main():

    config = load_config()

    db = Database(config)

    try:
        ...
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

This keeps maintenance scripts separate from ingestion and source modules while still allowing access to the project's shared database and configuration functionality.

---

# Recommended Setup Workflow

For a new installation:

```bash
# Configure the application

edit config.toml
edit secrets/secrets.toml

# Load account and meter metadata

python3 tools/load_account.py

# Backfill historical data

./tools/ingest_history.sh \
    2025-01-01 \
    2026-11-30

# Begin normal operation

python3 ingest_day.py 2026-12-01
```

For most users, `load_account.py` and `ingest_history.sh` will be the only tools that need to be run on a regular basis.