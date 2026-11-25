# tests/integration/test_homeassistant_pipeline.py

from database.sqlite import SQLiteBackend
from sources.homeassistant.collector import (
    HomeAssistantCollector,
)


class MockHomeAssistantClient:

    def get_state(self, entity_id):

        data = {
            "sensor.tank_top": {
                "state": "54.3",
            },
            "sensor.tank_bottom": {
                "state": "42.1",
            },
        }

        return data[entity_id]


def test_homeassistant_pipeline(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "tank.db"
        )
    )

    collector = HomeAssistantCollector(
        client=MockHomeAssistantClient(),
        tank_top="sensor.tank_top",
        tank_bottom="sensor.tank_bottom",
    )

    temperatures = (
        collector.get_tank_temperatures()
    )

    db.load_tank_temperature(
        sensor_entity_id="sensor.tank_top",
        history=[
            {
                "timestamp":
                    "2026-01-01T12:00:00",
                "value":
                    temperatures["top"],
            }
        ],
    )

    db.load_tank_temperature(
        sensor_entity_id="sensor.tank_bottom",
        history=[
            {
                "timestamp":
                    "2026-01-01T12:00:00",
                "value":
                    temperatures["bottom"],
            }
        ],
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM tank_temps
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 2

    db.cursor.execute(
        """
        SELECT
            sensor_id,
            value
        FROM tank_temps
        ORDER BY sensor_id
        """
    )

    rows = db.cursor.fetchall()

    assert rows[0][1] == 54.3
    assert rows[1][1] == 42.1

    db.close()

def test_homeassistant_pipeline_is_idempotent(
    tmp_path,
):

    db = SQLiteBackend(
        str(
            tmp_path / "tank.db"
        )
    )

    history = [
        {
            "timestamp":
                "2026-01-01T12:00:00",
            "value":
                54.3,
        }
    ]

    db.load_tank_temperature(
        "sensor.tank_top",
        history,
    )

    db.load_tank_temperature(
        "sensor.tank_top",
        history,
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM tank_temps
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 1

    db.close()