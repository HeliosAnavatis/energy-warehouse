# Testing

## Overview

The Energy Data Warehouse includes both unit tests and integration tests.

The test suite is designed to verify:

- Configuration validation
- Data source clients
- Data collectors
- Database interfaces
- Database backends
- End-to-end data ingestion pipelines

Testing is performed using:

```text
pytest
```

---

# Test Types

## Unit Tests

Unit tests verify individual classes and functions in isolation.

External dependencies such as:

- HTTP APIs
- Databases
- Third-party services

are replaced with mocks.

Examples:

```text
WeatherClient
WeatherCollector

HomeAssistantClient
HomeAssistantCollector

SolarAssistantClient
SolarAssistantCollector

OctopusClient
OctopusCollector
```

Unit tests are:

- Fast
- Deterministic
- Suitable for frequent execution

---

## Integration Tests

Integration tests verify multiple components working together.

Typically these tests combine:

```text
Mock Data Source
        │
        ▼
Collector
        │
        ▼
Database Layer
        │
        ▼
SQLite Database
```

Unlike unit tests, integration tests use a real database backend.

Integration tests validate:

- Data transformation
- Data persistence
- Uniqueness constraints
- Idempotent ingestion behaviour

---

# Test Structure

The test suite is organised as:

```text
tests/
├── unit/
│   ├── test_logger.py
│   ├── test_config.py
│   │
│   ├── weather/
│   ├── homeassistant/
│   ├── solarassistant/
│   ├── octopus/
│   └── database/
│
└── integration/
    ├── test_weather_pipeline.py
    ├── test_homeassistant_pipeline.py
    └── test_octopus_pipeline.py
```

The exact structure may evolve as additional modules are added.

---

# Running Tests

## Run Entire Test Suite

```bash
pytest
```

---

## Verbose Output

```bash
pytest -v
```

---

## Stop On First Failure

```bash
pytest -x
```

Useful during development.

---

## Run Only Unit Tests

```bash
pytest tests/unit
```

---

## Run Only Integration Tests

```bash
pytest tests/integration
```

---

## Run A Single Test File

Example:

```bash
pytest tests/unit/test_config.py
```

---

## Run A Single Test

Example:

```bash
pytest \
    tests/unit/test_config.py::test_valid_sqlite_config
```

---

# Current Test Coverage

## Logger

Tests:

- Logger creation
- Log level configuration
- Handler creation
- Duplicate handler prevention

---

## Configuration

Tests:

- Valid configuration values
- Database configuration validation
- URL validation
- Timeout validation
- Tank configuration validation
- Weather configuration validation

---

## Weather

### Client

Tests:

- API request construction
- Parameter handling
- Response handling

### Collector

Tests:

- Weather history processing
- Data transformation

---

## Home Assistant

### Client

Tests:

- State retrieval
- History retrieval
- Bucket aggregation
- Time grouping

### Collector

Tests:

- Tank temperature collection
- Type conversion

---

## Solar Assistant

### Client

Tests:

- Topic mapping
- API requests
- Battery SoC retrieval
- Error handling

### Collector

Tests:

- Energy conversion
- Timestamp mapping
- SoC processing

---

## Octopus

### Client

Tests:

- Product code extraction
- Consumption URL generation
- Fuel validation
- API interaction

### Collector

Tests:

- Meter reading processing
- Tariff region extraction
- Single-rate expansion
- Flexible tariff expansion
- Missing data handling

---

## Database Frontend

Tests:

- Backend abstraction layer
- Method delegation
- Database selection

---

## SQLite Backend

Tests:

- Supplier creation
- Account creation
- Meter creation
- Tariff creation
- Reading storage
- Weather storage
- Battery SoC storage
- Idempotent updates

---

# Integration Tests

## Weather Pipeline

Tests:

```text
WeatherClient (mock)
        │
        ▼
WeatherCollector
        │
        ▼
SQLiteBackend
```

Validates:

- Data collection
- Data transformation
- Database persistence

---

## Home Assistant Pipeline

Tests:

```text
HomeAssistantClient (mock)
        │
        ▼
HomeAssistantCollector
        │
        ▼
SQLiteBackend
```

Validates:

- Tank temperature collection
- Sensor persistence
- Idempotency behaviour

---

## Octopus Pipeline

Tests:

```text
OctopusClient (mock)
        │
        ▼
OctopusCollector
        │
        ▼
SQLiteBackend
```

Validates:

- Reading ingestion
- Database storage
- Idempotent updates

---

# Temporary Database Handling

Integration tests create temporary SQLite databases using pytest's:

```python
tmp_path
```

fixture.

Advantages:

- No cleanup required
- No modification of production databases
- Repeatable test execution
- Parallel test support

Example:

```python
db_file = tmp_path / "test.db"
```

The temporary database is automatically deleted when the test completes.

---

# PostgreSQL Testing

Most development testing is performed against SQLite.

PostgreSQL functionality is validated through:

- Migration testing
- End-to-end ingestion
- Manual verification
- Data parity checks

Where automated PostgreSQL testing is required, a dedicated test schema should be used.

Example:

```text
utility_test
```

rather than the production schema:

```text
utility
```

This prevents test execution from affecting production data.

---

# Idempotency Testing

A core design principle of Energy is that ingestion operations are idempotent.

This means:

```text
Running the same ingest twice
must not create duplicate data.
```

Many tests intentionally execute the same load operation multiple times and verify that row counts remain unchanged.

This behaviour is particularly important for:

- Scheduled jobs
- Historical backfills
- Recovery after failures

---

# Adding New Tests

When adding a new source module:

1. Create unit tests for the client.
2. Create unit tests for the collector.
3. Add an integration test covering the full collection pipeline.
4. Verify idempotent behaviour.
5. Run the complete test suite.

The preferred testing order is:

```text
Client
    ↓
Collector
    ↓
Database
    ↓
Integration Pipeline
```

This mirrors the structure of the application and makes debugging significantly easier.

---

# Continuous Testing

Recommended development workflow:

```bash
pytest
```

before every commit.

For larger changes:

```bash
pytest -v
```

and perform a full ingestion run against a test database before merging changes.

A change should only be considered complete when:

- Unit tests pass
- Integration tests pass
- Ingestion succeeds
- No duplicate data is created