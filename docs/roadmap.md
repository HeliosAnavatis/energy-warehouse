# Roadmap

## Overview

The Energy Data Warehouse began as a simple collection utility for storing Octopus Energy consumption data.

Over time the project has evolved into a modular energy data warehouse capable of combining data from multiple energy, monitoring and weather systems into a single database.

The long-term goal is to provide a unified platform for analysing domestic energy generation, consumption, storage and cost.

---

# Current Status

The project is actively developed and used to monitor a real domestic energy installation.

Current capabilities include:

## Data Sources

### Octopus Energy

Collects:

- Electricity import consumption
- Electricity export consumption
- Gas consumption
- Tariff information
- Historical pricing

---

### Solar Assistant

Collects:

- Solar generation
- House load
- Battery power flow
- Grid power flow
- Battery state of charge

---

### Home Assistant

Collects:

- Hot water tank temperatures
- Additional sensor telemetry

---

### Open Meteo

Collects:

- Air temperature
- Cloud cover
- Solar radiation

---

## Database Support

The system supports:

- SQLite
- PostgreSQL

Data can be migrated between both databases using the built-in migration utility.

---

## Test Coverage

The project currently includes:

### Unit Tests

- Logger
- Configuration
- Weather modules
- Home Assistant modules
- Solar Assistant modules
- Octopus modules
- Database abstraction layer
- SQLite backend

### Integration Tests

- Weather ingestion pipeline
- Home Assistant ingestion pipeline
- Octopus ingestion pipeline

---

## Operational Features

- Configuration-driven source selection
- Include / exclude module control
- Historical backfill tooling
- Database migration tooling
- Idempotent ingestion
- Automated testing

---

# Current Focus Areas

The following areas are currently receiving the most attention.

---

## Tariff Processing Improvements

The tariff subsystem is the most complex area of the codebase.

Planned improvements include:

- Simplification of tariff processing logic
- Improved support for non-standard tariff structures
- Reduced code duplication
- Expanded test coverage
- Improved handling of tariff transitions
- Better separation between API integration and tariff business logic

---

## Containerisation

Container support is planned to simplify deployment.

Goals include:

- Docker-based deployment
- Persistent volumes for configuration and data
- Simplified upgrades
- Improved reproducibility
- Easier deployment to Linux servers

Target architecture:

```text
+-------------------+
| Energy Container  |
+-------------------+
         |
         ▼
+-------------------+
| PostgreSQL        |
+-------------------+
```

---

## Grafana Dashboards

Future releases are expected to include example dashboards.

Potential dashboards include:

- Daily energy flow
- Solar generation performance
- Battery utilisation
- Import vs export analysis
- Cost tracking
- Historical temperature data
- Tariff analysis

The warehouse is already suitable as a Grafana data source via PostgreSQL.

---

## Additional Data Sources

The modular architecture makes it straightforward to add new sources.

Potential future integrations include:

### Energy Platforms

- Tesla Powerwall
- GivEnergy
- MyEnergi
- Victron
- OpenEnergyMonitor

### Weather Providers

- Met Office
- OpenWeatherMap
- Visual Crossing

### Home Automation

- Additional Home Assistant sensors
- MQTT sources
- Local device APIs

---

# Future Plans

## Enhanced Reporting

Potential future reporting capabilities include:

- Daily energy summaries
- Weekly and monthly reporting
- Self-consumption analysis
- Battery efficiency calculations
- Import/export forecasting

---

## Analytics Views

Possible database enhancements:

- Pre-built reporting views
- Materialised summary tables
- Optimised analytical queries

These would simplify integration with:

- Excel
- Grafana
- Power BI

---

## Improved Historical Processing

Future work may include:

- Faster backfilling
- Parallel ingestion
- Bulk loading optimisation
- Incremental update strategies

---

## Installation Improvements

Potential enhancements:

- Container-first deployments
- Automated installation scripts
- Sample configuration generation
- Improved diagnostics

---

## PostgreSQL Enhancements

Potential improvements include:

- Performance tuning
- Additional indexes
- Query optimisation
- Automated maintenance tasks

---

# Known Limitations

## Single-Day Ingestion Model

The main ingestion process currently operates on a single day at a time.

Historical backfills therefore require repeated execution across a date range.

The included historical ingestion tool automates this process.

---

## PostgreSQL Test Coverage

Most automated testing currently focuses on SQLite.

PostgreSQL functionality has been validated extensively through migration and ingestion testing, but dedicated automated PostgreSQL integration tests remain limited.

---

## Tariff Complexity

Octopus tariff processing supports current requirements but remains one of the most complex parts of the application.

Additional refactoring and testing are planned.

---

## Limited Dashboarding

The project currently focuses on data collection and storage.

Visualisation and reporting are expected to be provided through external tools such as:

- Excel
- Grafana
- Power BI

---

## Source-Specific Logic

Some ingestion logic is necessarily tied to the behaviour of specific upstream APIs.

Breaking changes in third-party services may require source module updates.

---

## No Automatic Schema Upgrades

Database schema changes currently require manual migration.

Future releases may include a formal schema versioning and migration framework.

---

# Long-Term Vision

The long-term goal is to provide a modular, self-hosted energy warehouse capable of combining:

```text
Energy
Weather
Heating
Battery Storage
Solar Generation
Home Automation
```

into a single historical dataset.

The project aims to remain:

- Open
- Self-hosted
- Database-driven
- Vendor-neutral
- Easy to extend

while maintaining support for both lightweight SQLite deployments and larger PostgreSQL installations.