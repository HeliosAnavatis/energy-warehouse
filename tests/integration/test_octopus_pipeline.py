from database.sqlite import SQLiteBackend
from sources.octopus.collector import (
    OctopusCollector,
)


class MockOctopusClient:

    def get_readings(
        self,
        meter_point,
        meter_serial,
        meter_fuel,
        start,
        end,
    ):

        return {
            "results": [
                {
                    "interval_start":
                        "2026-01-01T00:30:00Z",
                    "consumption":
                        2.0,
                },
                {
                    "interval_start":
                        "2026-01-01T00:00:00Z",
                    "consumption":
                        1.0,
                },
            ]
        }


def test_octopus_meter_reading_pipeline(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "octopus.db"
        )
    )

    #
    # Create account hierarchy
    #

    supplier_id = db.load_supplier(
        "Octopus"
    )

    account_id = db.load_account(
        account_number="A12345",
        supplier_id=supplier_id,
        active_from="2026-01-01",
        active_to=None,
    )

    meter_id = db.load_meter(
        account_id=account_id,
        identifier="123456789",
        serial_number="ABC123",
        is_export=False,
        fuel="E",
    )

    #
    # Collect readings
    #

    collector = OctopusCollector(
        MockOctopusClient()
    )

    readings = collector.get_reading_history(
        meter_point="123456789",
        meter_serial="ABC123",
        meter_fuel="E",
        start="2026-01-01T00:00:00Z",
        end="2026-01-01T01:00:00Z",
    )

    #
    # Persist readings
    #

    db.load_meter_readings(
        meter_id,
        readings,
    )

    #
    # Verify data
    #

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
        1.0,
    )

    assert rows[1] == (
        "2026-01-01T00:30:00Z",
        2.0,
    )

    db.close()

def test_octopus_meter_reading_pipeline_is_idempotent(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "octopus.db"
        )
    )

    supplier_id = db.load_supplier(
        "Octopus"
    )

    account_id = db.load_account(
        "A12345",
        supplier_id,
        "2026-01-01",
        None,
    )

    meter_id = db.load_meter(
        account_id,
        "123456789",
        "ABC123",
        False,
        "E",
    )

    collector = OctopusCollector(
        MockOctopusClient()
    )

    readings = collector.get_reading_history(
        "123456789",
        "ABC123",
        "E",
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
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