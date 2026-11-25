from datetime import datetime

from database.sqlite import SQLiteBackend
from sources.solarassistant.collector import (
    SolarAssistantCollector,
)


class MockSolarAssistantClient:

    def get_readings(
        self,
        meter_id,
        start,
        end,
    ):

        return {
            "points": [
                (
                    "2026-01-01T00:00:00Z",
                    1000,
                ),
                (
                    "2026-01-01T00:30:00Z",
                    2000,
                ),
            ]
        }


def test_solarassistant_pipeline(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "solar.db"
        )
    )

    supplier_id = db.load_supplier(
        "Home Energy System"
    )

    account_id = db.load_account(
        account_number="TEST",
        supplier_id=supplier_id,
        active_from="2026-01-01",
        active_to=None,
    )

    meter_id = db.load_meter(
        account_id=account_id,
        identifier="pv-generation",
        serial_number="SOLAR",
        is_export=False,
        fuel="S",
    )

    collector = SolarAssistantCollector(
        MockSolarAssistantClient()
    )

    readings = collector.get_readings(
        meter_id="pv-generation",
        start=datetime.now(),
        end=datetime.now(),
    )

    db.load_meter_readings(
        meter_id,
        readings,
    )

    db.cursor.execute(
        """
        SELECT
            interval_start,
            energy
        FROM reading
        ORDER BY interval_start
        """
    )

    rows = db.cursor.fetchall()

    assert len(rows) == 2

    assert rows[0] == (
        "2026-01-01T00:00:00Z",
        0.5,
    )

    assert rows[1] == (
        "2026-01-01T00:30:00Z",
        1.0,
    )

    db.close()

def test_solarassistant_pipeline_is_idempotent(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "solar.db"
        )
    )

    supplier_id = db.load_supplier(
        "Home Energy System"
    )

    account_id = db.load_account(
        "TEST",
        supplier_id,
        "2026-01-01",
        None,
    )

    meter_id = db.load_meter(
        account_id,
        "pv-generation",
        "SOLAR",
        False,
        "S",
    )

    collector = SolarAssistantCollector(
        MockSolarAssistantClient()
    )

    readings = collector.get_readings(
        "pv-generation",
        datetime.now(),
        datetime.now(),
    )

    db.load_meter_readings(
        meter_id,
        readings,
    )

    db.load_meter_readings(
        meter_id,
        readings,
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM reading
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 2

    db.close()