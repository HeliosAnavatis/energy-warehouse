# Configuration

## Overview

The Energy Data Warehouse uses two configuration files. Configuration is intentionally split into:

- Non-sensitive settings in `config.toml`
- Credentials and secrets in `secrets.toml`

This allows configuration to be committed to source control while keeping passwords, API tokens and account details separate.

---

# Configuration Files

## config.toml

Contains:

- Database configuration
- Service URLs
- Timeouts
- Weather location
- Sensor mappings
- Solar Assistant topic mappings
- Collector settings

This file is safe to customise and share.

---

## secrets/secrets.toml

Contains:

- Octopus API credentials
- Home Assistant access token
- Solar Assistant credentials
- PostgreSQL username and password

This file should never be shared or committed to source control.

---

# Database Configuration

The active database backend is selected using:

```toml
[database]
engine = "sqlite"
```

or:

```toml
[database]
engine = "postgres"
```

Only one backend is active at a time.

---

# SQLite Configuration

```toml
[sqlite]
type = "sqlite"
path = "data/energy.db"
```

## path

Location of the SQLite database file.

Examples:

```toml
path = "data/energy.db"
```

```toml
path = "/srv/energy/energy.db"
```

SQLite is recommended for:

- Development
- Testing
- Small installations

No database server is required.

---

# PostgreSQL Configuration

```toml
[postgres]
type = "postgres"
host = "192.168.1.100"
port = 5432
database = "energy"
schema = "utility"
```

Credentials are stored separately in `secrets.toml`.

## host

PostgreSQL server address.

Examples:

```toml
host = "localhost"
```

```toml
host = "postgres"
```

```toml
host = "postgres.local"
```

---

## port

Database port.

Default:

```toml
port = 5432
```

---

## database

Database name:

```toml
database = "energy"
```

---

## schema

Schema used by the application:

```toml
schema = "utility"
```

Multiple Energy installations can coexist within the same PostgreSQL database by using different schema names.

Examples:

```toml
schema = "utility-house"
```

```toml
schema = "utility-workshop"
```

---

# Home Assistant Configuration

```toml
[homeassistant]
url = "http://homeassistant.local:8123"
timeout = 30
```

## url

Base URL of the Home Assistant instance.

Examples:

```toml
url = "http://homeassistant.local:8123"
```

```toml
url = "https://ha.example.com"
```

---

## timeout

HTTP request timeout in seconds.

Example:

```toml
timeout = 30
```

---

# Solar Assistant Configuration

```toml
[solarassistant]
url = "http://solarassistant.local"
timeout = 30

pv-generation = "pv_power"
house-load = "load_power"
battery-flow = "battery_power"
grid-flow = "grid_power"
battery-soc = "battery_soc"
```

## url

Solar Assistant web interface URL.

Example:

```toml
url = "http://solarassistant.local"
```

---

## timeout

Request timeout.

Example:

```toml
timeout = 30
```

---

## Topic Mapping

The remaining entries map Energy meter identifiers to Solar Assistant topics.  These should not need to be changed.

Example:

```toml
pv-generation = "pv_power"
```

This tells Energy which Solar Assistant metric should be used for the meter named:

```text
pv-generation
```

The exact values depend on the Solar Assistant installation.

You should verify these topics against your own Solar Assistant API.

---

# Octopus Configuration

```toml
[octopus]
url = "https://api.octopus.energy/v1"
timeout = 30
```

## url

Base URL for the Octopus API.

Unless using a proxy or test environment, this should normally remain unchanged.

---

## timeout

Request timeout.

Example:

```toml
timeout = 30
```

---

# Weather Configuration

```toml
[weather]
provider = "openmeteo"
latitude = 57.5962226
longitude = -13.6875217
```

Currently `"openmeteo"` is the only supported weather provider.

The `latitude` and `longitude` settings relate to the site being monitored.  These are used when retrieving weather observations.

---

## latitude

Site latitude.

Example:

```toml
latitude = 57.5962226
```

---

## longitude

Site longitude.

Example:

```toml
longitude = -13.6875217
```

---

# Tank Configuration

```toml
[tank]
volume = 250

tank_top = "sensor.tank_top"
tank_bottom = "sensor.tank_bottom"
```

## volume

Tank volume in litres.

Example:

```toml
volume = 250
```

**Note**: This value is not currently used and exists for future functionality.

---

## tank_top

Home Assistant entity representing the upper tank temperature sensor.

Example:

```toml
tank_top = "sensor.tank_top"
```

---

## tank_bottom

Home Assistant entity representing the lower tank temperature sensor.

Example:

```toml
tank_bottom = "sensor.tank_bottom"
```

---

# Collector Configuration

```toml
[collector]
name = "energycollector"
timezone = "Europe/London"
```

## name

Friendly name for the collector instance.

Example:

```toml
name = "energycollector"
```

---

## timezone

Local timezone.

Example:

```toml
timezone = "Europe/London"
```

Future reporting and scheduling features may use this value.

---

# Secrets Configuration

All credentials are stored in:

```text
secrets/secrets.toml
```

---

## PostgreSQL Credentials

```toml
[postgres]
user = "energy"
password = "secret"
```

Required only when PostgreSQL is used.

---

## Octopus Credentials

```toml
[octopus]
account_number = "X-nnnnnn"
api_key = "sk_live_xxxxx"
```

### account_number

Your Octopus account number.

### api_key

API key generated from the Octopus developer portal.

---

## Home Assistant Token

```toml
[homeassistant]
token = "long-lived-access-token"
```

Generate a Long-Lived Access Token within Home Assistant.

---

## Solar Assistant Credentials

```toml
[solarassistant]
username = "admin"
password = "password"
```

Credentials used to access the Solar Assistant API.

---

# Example SQLite Installation

```toml
[database]
engine = "sqlite"

[sqlite]
type = "sqlite"
path = "data/energy.db"
```

Suitable for:

- Testing
- Development
- Small deployments

---

# Example PostgreSQL Installation

```toml
[database]
engine = "postgres"

[postgres]
type = "postgres"
host = "postgres"
port = 5432
database = "energy"
schema = "utility"
```

Suitable for:

- Container deployments
- Large datasets
- Multi-user access
- Long-term production use

---

# Migrating Between Databases

The active backend can be changed simply by modifying:

```toml
[database]
engine = "sqlite"
```

or:

```toml
[database]
engine = "postgres"
```

Existing data can be migrated using:

```bash
python3 tools/migrate_db.py \
    --source sqlite \
    --target postgres
```

See:

```text
docs/database.md
```

for details of the migration process.

---

# Configuration Validation

Configuration files are validated when the application starts.

Validation includes:

- Database configuration
- URLs
- Network ports
- Timeouts
- Weather coordinates
- Credentials
- Sensor mappings

Invalid configuration values will cause startup to fail with a descriptive error message.

This helps detect configuration problems before data collection begins.