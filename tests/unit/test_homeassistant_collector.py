# tests/unit/homeassistant/test_homeassistant_collector.py

from sources.homeassistant.collector import (
    HomeAssistantCollector,
)


class MockClient:

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


def test_get_tank_temperatures():

    collector = HomeAssistantCollector(
        client=MockClient(),
        tank_top="sensor.tank_top",
        tank_bottom="sensor.tank_bottom",
    )

    result = collector.get_tank_temperatures()

    assert result == {
        "top": 54.3,
        "bottom": 42.1,
    }


def test_returns_floats():

    collector = HomeAssistantCollector(
        client=MockClient(),
        tank_top="sensor.tank_top",
        tank_bottom="sensor.tank_bottom",
    )

    result = collector.get_tank_temperatures()

    assert isinstance(
        result["top"],
        float,
    )

    assert isinstance(
        result["bottom"],
        float,
    )