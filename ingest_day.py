#!/usr/bin/env python3

import argparse
import sys
import time

from datetime import (datetime, timedelta, timezone, )

from utils.config import load_config
from database.database import Database
from sources.homeassistant.client import (HomeAssistantClient)
from sources.octopus.client import (OctopusClient)
from sources.octopus.collector import (OctopusCollector)
from sources.weather.client import (WeatherClient)
from sources.weather.collector import (WeatherCollector)
from sources.solarassistant.collector import (SolarAssistantCollector)
from sources.solarassistant.client import (SolarAssistantClient)

from utils.logger import get_logger

MAX_RETRIES = 3
RETRY_DELAY = 5

logger = get_logger(__name__)

#==============================================================================
def retry(operation_name, fn):

    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            logger.info("%s (attempt %s/%s)",operation_name, attempt, MAX_RETRIES,)
            return fn()

        except Exception as ex:

            last_exception = ex

            print(
                logger.error("%s failed: %s",operation_name,ex,)
            )

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    raise last_exception

#==============================================================================
def ingest_weather(db, config, ingest_date):
    # ---------------------------------------------------------------------
    # Weather
    # ---------------------------------------------------------------------

    logger.info("=== Weather ===")

    weather_client = WeatherClient(
        latitude=config.weather.latitude,
        longitude=config.weather.longitude,
    )

    weather_collector = WeatherCollector(
        weather_client,
    )

    weather_history = retry(
        "Collect weather",
        lambda: weather_collector.get_day_hourly(
            ingest_date
        ),
    )

    db.load_weather(weather_history,)

    logger.info("Loaded %s weather observations",len(weather_history),)

#==============================================================================
def ingest_tank_temps(db, config, start, end):
    # ---------------------------------------------------------------------
    # Tank temperatures
    # ---------------------------------------------------------------------
    logger.info("=== Tank Temperatures ===")

    ha_client = HomeAssistantClient(
        base_url=config.homeassistant.url,
        token=config.homeassistant_secrets.token,
        timeout=config.homeassistant.timeout,
    )

    for sensor_entity_id in [
        config.tank.tank_top,
        config.tank.tank_bottom,
    ]:

        history = retry(
            f"Collect {sensor_entity_id}",
            lambda sensor=sensor_entity_id:
                ha_client.get_history_buckets(
                    entity_id=sensor,
                    start=start.isoformat(),
                    end=end.isoformat(),
                    group_by="30m",
                    agg="max",
                ),
        )

        if not history:
            print (f"No history for "
                f"{sensor_entity_id}")
        else:
            db.load_tank_temperature(
                sensor_entity_id,
                history,
            )

        logger.info("Loaded %s readings for sensor %s",len(history),sensor_entity_id,)

#==============================================================================
def ingest_octopus(db, config, start, end, ingest_date):
    # ---------------------------------------------------------------------
    # Octopus
    # ---------------------------------------------------------------------

    logger.info("=== Octopus ===")

    octopus_client = OctopusClient(
        base_url=config.octopus.url,
        account_number=(
            config.octopus_secrets.account_number
        ),
        api_key=config.octopus_secrets.api_key,
        timeout=config.octopus.timeout,
    )

    octopus_collector = OctopusCollector(
        octopus_client,
    )

    # ---------------------------------------------------------------------
    # Metering Data
    # ---------------------------------------------------------------------
    account_id = db.get_account_id(config.octopus_secrets.account_number)
    meters = db.get_active_meters(account_id)
    for meter in meters:

        readings = retry(
            "Collect meter readings",
            lambda: octopus_collector.get_reading_history(
                meter_serial=meter["serial_number"],
                meter_point=meter["identifier"],
                meter_fuel=meter["fuel"],
                start=start.isoformat(),
                end=end.isoformat(),
            ),
        )

        db.load_meter_readings(
            meter["meter_id"],
            readings,
        )

        logger.info("Loaded %s meter readings",len(readings),)

        tariff = db.get_active_tariff(
            meter["meter_id"],
            ingest_date,
        )

        if tariff is None:
            logger.info ("No tariff code for %s",meter["meter_id"])
            continue
        else:
            logger.info ("Tariff code for %s: %s",meter["meter_id"], tariff["tariff_code"])

        rates = octopus_collector.get_rates(
            tariff["tariff_code"],
            start=start.isoformat(),
            end=end.isoformat(),
        )

        db.load_energy_rate(
            meter["meter_id"],
            rates,
        )

        logger.info("Loaded %s rate readings",len(rates),)

#==============================================================================
def ingest_solarassistant(db, config, start, end):
    # ---------------------------------------------------------------------
    # Home Energy - Solar Assistant
    # ---------------------------------------------------------------------
    logger.info("=== Solar Assistant ===")

    solarassistant_client = SolarAssistantClient(
        base_url=config.solarassistant.url,
        timeout=config.solarassistant.timeout,
        topics=config.solarassistant.topics,
        username=config.solarassistant_secrets.username,
        password=config.solarassistant_secrets.password,
    )

    solarassistant_collector = SolarAssistantCollector(solarassistant_client, ) 

    # TODO: Select account ID
    account_id = db.get_account_id("solar-assistant")
    meters = db.get_active_meters(account_id)
    for meter in meters:
        readings = retry(
            "Collect Home Energy readings",
            lambda: solarassistant_collector.get_readings(
                meter_id=meter["identifier"],
                start=start,
                end=end,
            )
        )

        if readings:
            db.load_meter_readings(
                meter["meter_id"],
                readings,
            )
        else:
            print ("No readings returned")

        logger.info("Loaded %s readings for %s",len(readings),meter["identifier"],)

    #
    # Battery SoC
    #
    soc = retry(
        "Collect Battery SoC",
        lambda: solarassistant_collector.get_soc(
            start=start,
            end=end,
        )
    )

    db.load_battery_soc(
        soc
    )

    logger.info("Loaded %s Battery SoC readings",len(soc),)

#==============================================================================
MODULES = {
    "weather": ingest_weather,
    "tank": ingest_tank_temps,
    "octopus": ingest_octopus,
    "solarassistant": ingest_solarassistant,
}

#==============================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="Date to ingest (YYYY-MM-DD)", )
    parser.add_argument("-c", "--config",  help="Config file",  default=None, )
    parser.add_argument("-s", "--secrets", help="Secrets file", default=None, )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-i",
        "--include",
        help="Comma-separated list of modules to run",
        default=None,
    )

    group.add_argument(
        "-x",
        "--exclude",
        help="Comma-separated list of modules to skip",
        default=None,
    )

    args = parser.parse_args()

    config = load_config(config_file=args.config, secrets_file=args.secrets, )
    selected_modules = set(MODULES.keys())

    if args.include:
        selected_modules = {
            module.strip().lower()
            for module in args.include.split(",")
        }

    elif args.exclude:
        selected_modules -= {
            module.strip().lower()
            for module in args.exclude.split(",")
        }

    unknown_modules = selected_modules - set(MODULES.keys())

    if unknown_modules:
        parser.error(
            f"Unknown modules: "
            f"{', '.join(sorted(unknown_modules))}"
        )
    ingest_date = datetime.strptime(
        args.date,
        "%Y-%m-%d",
    ).date()

    start = datetime.combine(
        ingest_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    end = start + timedelta(days=1)
    db = Database(config)

    try:
        if "weather" in selected_modules:
            ingest_weather(
                db,
                config,
                ingest_date,
            )

        if "tank" in selected_modules:
            ingest_tank_temps(
                db,
                config,
                start,
                end,
            )

        if "octopus" in selected_modules:
            ingest_octopus(
                db,
                config,
                start,
                end,
                ingest_date,
            )

        if "solarassistant" in selected_modules:
            ingest_solarassistant(
                db,
                config,
                start,
                end,
            )

        logger.info("Completed ingest for date: %s",ingest_date,)

    finally:

        db.close()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logger.exception("Unhandled exception")
        sys.exit(1)