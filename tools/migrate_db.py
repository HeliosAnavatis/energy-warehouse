#!/usr/bin/env python3

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

import argparse
import sqlite3
import psycopg

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
)

from utils.config import load_config

from database.sqlite import SQLiteBackend
from database.postgres import PostgreSQLBackend

BATCH_SIZE = 1000

TABLES = [
    "supplier",
    "account",
    "meter",
    "tariff",
    "sensor",
    "location",
    "tank_temps",
    "weather",
    "battery_soc",
    "reading",
    "rate_period",
]

console = Console()


# ============================================================================
def get_sqlite_connection(config):

    return sqlite3.connect(
        config.sqlite.path
    )


# ============================================================================
def get_postgres_connection(config):

    return psycopg.connect(
        host=config.postgres.host,
        port=config.postgres.port,
        dbname=config.postgres.database,
        user=config.postgres.user,
        password=config.postgres.password,
    )

# ============================================================================
def transform_row(
    table,
    row,
):

    row = list(row)

    if table == "meter":

        #
        # SQLite INTEGER -> PostgreSQL BOOLEAN
        #
        row[4] = bool(row[4])

    return tuple(row)


# ============================================================================
def row_count(connection, table):

    cursor = connection.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    return cursor.fetchone()[0]


# ============================================================================
def get_columns(connection, table):

    cursor = connection.cursor()

    if connection.__class__.__module__.startswith(
        "sqlite3"
    ):

        cursor.execute(
            f"PRAGMA table_info({table})"
        )

        return [row[1] for row in cursor.fetchall()]

    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    )

    return [row[0] for row in cursor.fetchall()]


# ============================================================================
def truncate_table(config, connection, table):

    cursor = connection.cursor()

    try:

        if connection.__class__.__module__.startswith(
            "sqlite3"
        ):

            cursor.execute(
                f"DELETE FROM {table}"
            )

        else:

            cursor.execute(
                f"TRUNCATE TABLE "
                f"{config.postgres.schema}.{table} "
                f"RESTART IDENTITY CASCADE"
            )

        connection.commit()

    finally:

        cursor.close()


# ============================================================================
def copy_table(
    source,
    destination,
    table,
):

    source_cursor = source.cursor()
    dest_cursor = destination.cursor()

    total_rows = row_count(
        source,
        table,
    )

    console.print(
        f"\n[bold cyan]{table}[/bold cyan] "
        f"({total_rows:,} rows)"
    )

    source_cursor.execute(
        f"SELECT * FROM {table}"
    )

    columns = [
        description[0]
        for description in source_cursor.description
    ]

    placeholders = []

    if destination.__class__.__module__.startswith(
        "sqlite3"
    ):

        placeholders = [
            "?"
            for _ in columns
        ]

    else:

        placeholders = [
            "%s"
            for _ in columns
        ]

    insert_sql = f"""
        INSERT INTO {table}
        ({",".join(columns)})
        VALUES
        ({",".join(placeholders)})
    """

    with Progress(
        TextColumn(
            "[progress.description]{task.description}"
        ),
        BarColumn(),
        TextColumn(
            "{task.completed:,}/{task.total:,}"
        ),
        TimeElapsedColumn(),
    ) as progress:

        task = progress.add_task(
            table,
            total=total_rows,
        )

        while True:

            rows = source_cursor.fetchmany(
                BATCH_SIZE
            )

            if not rows:
                break

            rows = [
                transform_row(
                    table,
                    row,
                )
                for row in rows
            ]

            try:

                dest_cursor.executemany(
                    insert_sql,
                    rows,
                )

                destination.commit()

            except Exception:

                destination.rollback()

                print()
                print("TABLE:", table)

                raise

            progress.update(
                task,
                advance=len(rows),
            )

    source_cursor.close()
    dest_cursor.close()


# ============================================================================
def verify_counts(
    source,
    destination,
):

    console.print(
        "\n[bold green]Verification[/bold green]"
    )

    failed = False

    for table in TABLES:

        source_count = row_count(
            source,
            table,
        )

        dest_count = row_count(
            destination,
            table,
        )

        status = "OK"

        if source_count != dest_count:

            failed = True
            status = "FAILED"

        console.print(
            f"{table:15s} "
            f"{source_count:10,d} -> "
            f"{dest_count:10,d} "
            f"{status}"
        )

    if failed:

        raise RuntimeError(
            "Verification failed"
        )


# ============================================================================
def initialise_destination(config, target):

    if target == "sqlite":

        backend = SQLiteBackend(
            config.sqlite.path,
        )

    elif target == "postgres":

        backend = PostgreSQLBackend(
            host=config.postgres.host,
            port=config.postgres.port,
            database=config.postgres.database,
            username=config.postgres.user,
            password=config.postgres.password,
            schema=config.postgres.schema,
        )

    else:

        raise ValueError(
            f"Unknown target: {target}"
        )

    backend.close()


# ============================================================================
def reset_postgres_sequences(
    connection,
    schema,
):

    cursor = connection.cursor()

    sequence_map = {
        "supplier": ("supplier_id", "supplier_supplier_id_seq"),
        "account": ("account_id", "account_account_id_seq"),
        "meter": ("meter_id", "meter_meter_id_seq"),
        "tariff": ("tariff_id", "tariff_tariff_id_seq"),
        "sensor": ("sensor_id", "sensor_sensor_id_seq"),
        "location": ("location_id", "location_location_id_seq"),
        "tank_temps": ("reading_id", "tank_temps_reading_id_seq"),
        "weather": ("reading_id", "weather_reading_id_seq"),
        "battery_soc": ("soc_id", "battery_soc_soc_id_seq"),
        "reading": ("reading_id", "reading_reading_id_seq"),
        "rate_period": ("period_id", "rate_period_period_id_seq"),
    }

    for table, (column, sequence) in sequence_map.items():

        cursor.execute(
            f"""
            SELECT setval(
                '{schema}.{sequence}',
                COALESCE(
                    (
                        SELECT MAX({column})
                        FROM {schema}.{table}
                    ),
                    1
                )
            )
            """
        )

    connection.commit()
    cursor.close()


# ============================================================================
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        required=True,
        choices=[
            "sqlite",
            "postgres",
        ],
    )

    parser.add_argument(
        "--target",
        required=True,
        choices=[
            "sqlite",
            "postgres",
        ],
    )

    parser.add_argument(
        "-c",
        "--config",
        default=None,
    )

    parser.add_argument(
        "-s",
        "--secrets",
        default=None,
    )

    parser.add_argument(
        "--replace",
        action="store_true",
        help="Overwrite destination database",
    )

    args = parser.parse_args()

    if not args.replace:

        raise RuntimeError(
            "Refusing to overwrite destination database. "
            "Use --replace to continue."
        )
    
    if args.source == args.target:

        raise ValueError(
            "source and target "
            "must be different"
        )

    config = load_config(
        config_file=args.config,
        secrets_file=args.secrets,
    )

    console.print(
        f"\nSQLite : {config.sqlite.path}"
    )

    console.print(
        f"Postgres: "
        f"{config.postgres.host}:"
        f"{config.postgres.port}/"
        f"{config.postgres.database}"
    )

    console.print(
        f"Schema: {config.postgres.schema}"
    )

    sqlite_conn = get_sqlite_connection(
        config
    )

    postgres_conn = get_postgres_connection(
        config
    )

    with postgres_conn.cursor() as cursor:

        cursor.execute(
            f"CREATE SCHEMA IF NOT EXISTS {config.postgres.schema}"
        )

        cursor.execute(
            f"SET search_path TO {config.postgres.schema}"
        )

    postgres_conn.commit()

    source = (
        sqlite_conn
        if args.source == "sqlite"
        else postgres_conn
    )

    destination = (
        postgres_conn
        if args.target == "postgres"
        else sqlite_conn
    )

    try:

        console.print(
            f"\nMigrating "
            f"{args.source} -> {args.target}"
        )

        initialise_destination(
            config,
            args.target,
        )

        for table in reversed(TABLES):

            truncate_table(
                config,
                destination,
                table,
            )

        for table in TABLES:

            copy_table(
                source,
                destination,
                table,
            )

        if args.target == "postgres":

            reset_postgres_sequences(
                destination,
                config.postgres.schema,
            )

        verify_counts(
            source,
            destination,
        )

        console.print(
            "\n[bold green]"
            "Migration complete"
            "[/bold green]"
        )

    finally:

        sqlite_conn.close()
        postgres_conn.close()


if __name__ == "__main__":
    main()