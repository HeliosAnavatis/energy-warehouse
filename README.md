# Energy Warehouse

This is a modular home energy data warehouse for collecting, storing and analysing energy, weather and telemetry data from multiple sources. I wrote it because I have a home battery, EV charger, and PV and thermal solar panels and I wanted to understand how they are working together, what environmental factors influence performance, optimise my grid imports and exports, and generally tweak the system to get the most value out of it.

The project ingests data from:

- Octopus Energy
- Solar Assistant
- Home Assistant
- Open-Meteo

and stores it in a unified schema that can be queried using SQLite or PostgreSQL.

The goal is to create a single source of truth for analysing:

- Electricity import (and export!)
- Gas consumption
- Solar PV generation
- Battery charging and discharging
- Battery state of charge
- Tank temperatures (proxying solar thermal generation)
- Weather conditions
- Tariffs and energy costs

The warehouse is designed to support both simple reporting and more advanced analysis using tools such as Excel, Grafana, Power BI and SQL.

This project was developed with the assistance of AI tools to speed up the code authoring process but the concept, logical and physical architecture, and module structure were all human-designed. All the code has been reviewed and tested manually.  If you don't like the use of AI and refuse to use this project, that's fine.  I get the arguments but please don't argue with me that I shouldn't work this way; my objective is functionality at speed, not passing some kind of purity test.

## Recognitions & Thanks

- [Octopus Energy](octopus.energy) for being such a forward-thinking energy supplier and providing a fantastic API.  USe my [referral link](https://share.octopus.energy/mauve-otter-194) to get a £50 sign-up bonus!
- [Home Assistant](https://www.home-assistant.io) for the best home automation and control platform. It is a brilliant piece of work
- [ESPHome](https://esphome.io) for the tools needed to create the tank temperature sensors
- [Solar Assistant](https://solar-assistant.io) for a really useful local controller for many brands of inverters (including mine!). **Note**: You need to be on version 2021-11-11 or later for the solar assistant collection to work.
- [Open Meteo](https://open-meteo.com) for providing a free weather API
- [BottlecapDave's Home Assistant Octopus Integration](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy) for the insights into the Octopus API (and just generally being an incredibly good Home Assistant integration)

And all the millions of people throughout history who have developed all the things that we stand on today to make these things possible.

---

## Features

- Modular ingestion architecture
- SQLite and PostgreSQL support
- Historical tariff storage
- Half-hourly energy modelling
- Solar, battery and household energy flow tracking
- Weather and environmental data collection
- Battery state-of-charge history
- Database migration tooling
- Selective module execution
- Container-friendly design

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/your-account/energy-warehouse.git
cd energy-warehouse
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create and customise:

```text
config.toml
secrets.toml
```

There are example files in the repository to give you a head start but you'll need to provide logins, API keys, hostnames, etc.

See:

- [Config](docs/config.md)
- [Usage](docs/usage.md)

Initialise account metadata:

```bash
python tools/load_account.py
```

Run an ingestion:

```bash
python ingest_day.py 2026-11-21
```

There's a tool called `ingest_history.sh` in the `tools` folder that will help to ingest historical data when you're setting up for the first time.

Run only specific modules:

```bash
python ingest_day.py 2026-11-21 -i weather,tank
```

Exclude specific modules:

```bash
python ingest_day.py 2026-11-21 -x solarassistant
```

---

## Documentation

### [Architecture](docs/architecture.md)

Describes the overall architecture of the system.

Includes:

- Module structure
- Client / collector pattern
- Database abstraction layer
- Ingestion workflow
- Adding new data sources
- Writing new modules

---

### [Database](docs/database.md)

Describes the warehouse schema in detail.

Includes:

- Table descriptions
- Entity relationships
- SQLite implementation
- PostgreSQL implementation
- Differences between both database engines
- Database migration tooling
- Backup and migration procedures

---

### [Config](docs/config.md)

Documents all configuration files.

Includes:

- `config.toml`
- `secrets.toml`
- Example configurations
- Required and optional settings
- Source-specific configuration sections

---

### [Usage](docs/usage.md)

Installation and operational guide.

Includes:

- Installation
- Creating databases
- PostgreSQL setup
- Running ingestion
- Scheduling
- Container deployment
- Using include and exclude module options
- Accessing warehouse data from Excel

---

### [Tests](docs/tests.md)

Describes the testing strategy.

Includes:

- Unit tests
- Integration tests
- End-to-end validation
- Adding tests for new modules

---

### [Tools](docs/tools.md)

Documents the utility scripts in the tools directory.

Includes:

- load_account.py
- ingest_history.py
- migrate_db.py
- Other administrative utilities

---

## Supported Data Sources

If you don't want or need these specific data sources, you can exclude them from an ingest without needing to modify the code (see the [usage](doc/usage.md) doc).  I've deliberately architected this system to be modular, so it should be fairly simple to write modules for whatever data sources you want to use.  If you write new modules, I'd encourage you to submit them here so that I can include them and make this project more usable to everyone.

### Octopus Energy

Collects:

- Electricity consumption
- Electricity export
- Gas consumption
- Tariff data

### Solar Assistant

Collects:

- Solar generation
- House load
- Battery energy flow
- Grid energy flow
- Battery state of charge

### Home Assistant

Collects:

- Tank temperatures
- Additional sensor telemetry

### Open-Meteo

Collects:

- Temperature
- Solar radiation
- Environmental conditions

---

## Typical Analysis

The warehouse can be used to answer questions such as:

- What is my average electricity cost per kWh?
- What is my solar self-consumption ratio?
- How much energy has passed through the battery?
- Has the battery paid for itself?
- What is the relationship between solar generation and hot water production?
- What are my monthly energy costs?
- How much electricity is imported during peak periods?

---

## Database Support

The warehouse supports:

- SQLite
- PostgreSQL

Data can be migrated between both systems using the migration tools documented in `docs/database.md`.

---

## Project Status

This project is in active development. See the [roadmap](docs/roadmap.md) for more details.

---

## Contributing

Contributions, bug reports and suggestions are welcome.

Please read:

- [Architecture](docs/architecture.md)
- [Tests](docs/tests.md)

before submitting changes.

---

## Licence

This software is published under the MIT license.  See [LICENSE](LICENSE) for full details.