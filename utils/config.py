# config.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import ipaddress
import tomllib

class ConfigError(Exception):
    """Raised when configuration is invalid."""

# ---------------------------------------------------------------------
# Active Database
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class ActiveDatabaseConfig:
    engine: str

    def __post_init__(self) -> None:

        if self.engine.lower() not in {
            "sqlite",
            "postgres",
        }:

            raise ConfigError(
                f"Unsupported database engine "
                f"'{self.engine}'"
                )

# ---------------------------------------------------------------------
# SQLite
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class SQLiteConfig:

    type: str
    path: str

    def __post_init__(self) -> None:

        if self.type.lower() != "sqlite":

            raise ConfigError(
                "sqlite.type must be 'sqlite'"
            )

        if not self.path:

            raise ConfigError(
                "sqlite.path is required"
            )

# ---------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class PostgresConfig:

    type: str
    host: str
    port: int
    database: str
    schema: str
    user: str
    password: str

    def __post_init__(self) -> None:

        if self.type.lower() != "postgres":

            raise ConfigError(
                "postgres.type must be "
                "'postgres'"
            )

        if not self.host:
            raise ConfigError(
                "postgres.host is empty"
            )

        if not self.database:
            raise ConfigError(
                "postgres.database is empty"
            )

        if not self.schema:
            raise ConfigError(
                "postgres.schema is empty"
            )

        if not self.user:
            raise ConfigError(
                "postgres.user is empty"
            )

        if not self.password:
            raise ConfigError(
                "postgres.password is empty"
            )

        if not (
            1 <= self.port <= 65535
        ):
            raise ConfigError(
                f"Invalid postgres.port "
                f"{self.port}"
            )

# ---------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ServiceConfig:
    url: str
    timeout: int

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)

        if parsed.scheme not in {"http", "https"}:
            raise ConfigError(
                f"Invalid URL scheme: {self.url}"
            )

        if not parsed.hostname:
            raise ConfigError(
                f"Invalid URL hostname: {self.url}"
            )

        if not 1 <= self.timeout <= 300:
            raise ConfigError(
                "timeout must be between 1 and 300 seconds"
            )

@dataclass(frozen=True)
class SolarAssistantConfig:
    url: str
    timeout: int
    topics: dict[str, str]

    def __post_init__(self) -> None:

        parsed = urlparse(self.url)

        if parsed.scheme not in {"http", "https"}:
            raise ConfigError(
                f"Invalid URL scheme: {self.url}"
            )

        if not parsed.hostname:
            raise ConfigError(
                f"Invalid URL hostname: {self.url}"
            )

        if not 1 <= self.timeout <= 300:
            raise ConfigError(
                "timeout must be between 1 and 300 seconds"
            )


@dataclass(frozen=True)
class SolarAssistantSecrets:
    username: str
    password: str

    def __post_init__(self) -> None:
        if not self.username:
            raise ConfigError("solarassistant.username is empty")

        if not self.password:
            raise ConfigError("solarassistant.password is empty")


@dataclass(frozen=True)
class HomeAssistantSecrets:
    token: str

    def __post_init__(self) -> None:
        if not self.token:
            raise ConfigError("homeassistant.token is empty")


@dataclass(frozen=True)
class OctopusSecrets:
    account_number: str
    api_key: str

    def __post_init__(self) -> None:
        if not self.account_number:
            raise ConfigError(
                "octopus.account_number is empty"
            )

        if not self.api_key:
            raise ConfigError(
                "octopus.api_key is empty"
            )


# ---------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class TankConfig:
    volume: float
    tank_top: str
    tank_bottom: str

    def __post_init__(self) -> None:
        if self.volume <= 0:
            raise ConfigError(
                "tank.volume must be positive"
            )
        if not self.tank_top:
            raise ConfigError(
                "tank.tank_top is empty"
            )
        if not self.tank_bottom:
            raise ConfigError(
                "tank.tank_bottom is empty"
            )


# ---------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class WeatherConfig:
    provider: str
    latitude: float | None
    longitude: float | None

    def __post_init__(self) -> None:
        if self.provider.lower() != "openmeteo":
            raise ConfigError(
                f"Unsupported weather provider: {self.provider}"
            )
        if self.latitude is None or self.longitude is None:
            raise ConfigError(
                "weather.latitude and weather.longitude are required"
            )

# ---------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class CollectorConfig:
    timezone: str
    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ConfigError(
                "collector.name is empty"
            )


# ---------------------------------------------------------------------
# Root Config
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Config:
    database: ActiveDatabaseConfig
    sqlite: SQLiteConfig
    postgres: PostgresConfig

    solarassistant: SolarAssistantConfig
    homeassistant: ServiceConfig
    octopus: ServiceConfig

    weather: WeatherConfig
    tank: TankConfig
    collector: CollectorConfig

    octopus_secrets: OctopusSecrets
    solarassistant_secrets: SolarAssistantSecrets
    homeassistant_secrets: HomeAssistantSecrets


# ---------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------

def load_config(
    config_file: str | Path | None = None,
    secrets_file: str | Path | None = None,
) -> Config:

    if config_file is None:
        config_file = "config.toml"

    if secrets_file is None:
        secrets_file = "secrets/secrets.toml"

    config_file = Path(config_file)
    secrets_file = Path(secrets_file)

    if not config_file.exists():
        raise ConfigError(
            f"Config file not found: {config_file}"
        )

    if not secrets_file.exists():
        raise ConfigError(
            f"Secrets file not found: {secrets_file}"
        )

    with config_file.open("rb") as fh:
        cfg = tomllib.load(fh)

    with secrets_file.open("rb") as fh:
        secrets = tomllib.load(fh)

    database = ActiveDatabaseConfig(
        engine=cfg["database"]["engine"],
    )

    sqlite = SQLiteConfig(
        **cfg["sqlite"]
    )

    postgres = PostgresConfig(
        type=cfg["postgres"]["type"],
        host=cfg["postgres"]["host"],
        port=cfg["postgres"]["port"],
        database=cfg["postgres"]["database"],
        schema=cfg["postgres"]["schema"],
        user=secrets["postgres"]["user"],
        password=secrets["postgres"]["password"],
    )

    sa_cfg = cfg["solarassistant"]

    return Config(
        database=database,

        sqlite=sqlite,

        postgres=postgres,

        solarassistant=SolarAssistantConfig(
            url=sa_cfg["url"],
            timeout=sa_cfg["timeout"],
            topics={
                k: v
                for k, v in sa_cfg.items()
                if k not in {"url", "timeout"}
            },
        ),

        homeassistant=ServiceConfig(
            **cfg["homeassistant"]
        ),

        octopus=ServiceConfig(
            **cfg["octopus"]
        ),

        weather=WeatherConfig(
            **cfg["weather"]
        ),

        tank=TankConfig(
            **cfg["tank"]
        ),

        collector=CollectorConfig(
            **cfg["collector"]
        ),

        octopus_secrets=OctopusSecrets(
            **secrets["octopus"]
        ),

        solarassistant_secrets=SolarAssistantSecrets(
            **secrets["solarassistant"]
        ),

        homeassistant_secrets=HomeAssistantSecrets(
            **secrets["homeassistant"]
        ),
    )