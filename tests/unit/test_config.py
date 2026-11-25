# tests/unit/test_config.py

import pytest

from utils.config import (
    ConfigError,
    ActiveDatabaseConfig,
    SQLiteConfig,
    PostgresConfig,
    ServiceConfig,
    WeatherConfig,
    TankConfig,
)


# ============================================================================
# ActiveDatabaseConfig
# ============================================================================

def test_active_database_sqlite():

    config = ActiveDatabaseConfig(
        engine="sqlite"
    )

    assert config.engine == "sqlite"


def test_active_database_postgres():

    config = ActiveDatabaseConfig(
        engine="postgres"
    )

    assert config.engine == "postgres"


def test_invalid_database_engine():

    with pytest.raises(ConfigError):

        ActiveDatabaseConfig(
            engine="mysql"
        )


# ============================================================================
# SQLiteConfig
# ============================================================================

def test_valid_sqlite_config():

    config = SQLiteConfig(
        type="sqlite",
        path="data/test.db",
    )

    assert config.path == "data/test.db"


def test_invalid_sqlite_type():

    with pytest.raises(ConfigError):

        SQLiteConfig(
            type="postgres",
            path="data/test.db",
        )


def test_missing_sqlite_path():

    with pytest.raises(ConfigError):

        SQLiteConfig(
            type="sqlite",
            path="",
        )


# ============================================================================
# PostgresConfig
# ============================================================================

def test_valid_postgres_config():

    config = PostgresConfig(
        type="postgres",
        host="localhost",
        port=5432,
        database="energy",
        schema="utility",
        user="john",
        password="secret",
    )

    assert config.database == "energy"


def test_invalid_postgres_type():

    with pytest.raises(ConfigError):

        PostgresConfig(
            type="sqlite",
            host="localhost",
            port=5432,
            database="energy",
            schema="utility",
            user="john",
            password="secret",
        )


def test_invalid_postgres_port():

    with pytest.raises(ConfigError):

        PostgresConfig(
            type="postgres",
            host="localhost",
            port=70000,
            database="energy",
            schema="utility",
            user="john",
            password="secret",
        )


def test_missing_postgres_host():

    with pytest.raises(ConfigError):

        PostgresConfig(
            type="postgres",
            host="",
            port=5432,
            database="energy",
            schema="utility",
            user="john",
            password="secret",
        )


# ============================================================================
# ServiceConfig
# ============================================================================

def test_valid_service_config():

    config = ServiceConfig(
        url="https://example.com",
        timeout=30,
    )

    assert config.timeout == 30


def test_invalid_service_scheme():

    with pytest.raises(ConfigError):

        ServiceConfig(
            url="ftp://example.com",
            timeout=30,
        )


def test_invalid_service_timeout():

    with pytest.raises(ConfigError):

        ServiceConfig(
            url="https://example.com",
            timeout=999,
        )


# ============================================================================
# WeatherConfig
# ============================================================================

def test_valid_weather_config():

    config = WeatherConfig(
        provider="openmeteo",
        latitude=51.7,
        longitude=-0.4,
    )

    assert config.provider == "openmeteo"


def test_invalid_weather_provider():

    with pytest.raises(ConfigError):

        WeatherConfig(
            provider="bbc",
            latitude=51.7,
            longitude=-0.4,
        )


def test_missing_weather_coordinates():

    with pytest.raises(ConfigError):

        WeatherConfig(
            provider="openmeteo",
            latitude=None,
            longitude=None,
        )


# ============================================================================
# TankConfig
# ============================================================================

def test_valid_tank_config():

    config = TankConfig(
        volume=250,
        tank_top="sensor.top",
        tank_bottom="sensor.bottom",
    )

    assert config.volume == 250


def test_invalid_tank_volume():

    with pytest.raises(ConfigError):

        TankConfig(
            volume=0,
            tank_top="sensor.top",
            tank_bottom="sensor.bottom",
        )


def test_missing_tank_top_sensor():

    with pytest.raises(ConfigError):

        TankConfig(
            volume=250,
            tank_top="",
            tank_bottom="sensor.bottom",
        )


def test_missing_tank_bottom_sensor():

    with pytest.raises(ConfigError):

        TankConfig(
            volume=250,
            tank_top="sensor.top",
            tank_bottom="",
        )