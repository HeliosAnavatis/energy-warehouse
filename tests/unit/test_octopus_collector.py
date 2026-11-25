from sources.octopus.collector import (
    OctopusCollector,
)

class MockClient:

    def get_readings(
        self,
        *args,
        **kwargs
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

def test_get_region_code():

    collector = OctopusCollector(
        MockClient()
    )

    assert (
        collector._get_region_code(
            "E-1R-TEST-A"
        )
        == "_A"
    )

def test_reading_history_sorted_oldest_first():

    collector = OctopusCollector(
        MockClient()
    )

    readings = collector.get_reading_history(
        meter_point="123",
        meter_serial="ABC",
        meter_fuel="E",
        start="A",
        end="B",
    )

    assert readings[0]["reading"] == 1.0
    assert readings[1]["reading"] == 2.0

class NullReadingClient:

    def get_readings(
        self,
        *args,
        **kwargs
    ):

        return {
            "results": [
                {
                    "interval_start":
                        "2026-01-01T00:30:00Z",
                    "consumption":
                        None,
                },
                {
                    "interval_start":
                        "2026-01-01T00:00:00Z",
                    "consumption":
                        1.0,
                },
            ]
        }


def test_null_readings_removed():

    collector = OctopusCollector(
        NullReadingClient()
    )

    readings = collector.get_reading_history(
        "123",
        "ABC",
        "E",
        "A",
        "B",
    )

    assert len(readings) == 1

def test_expand_single_rate():

    collector = OctopusCollector(
        MockClient()
    )

    tariff = {
        "direct_debit_monthly": {
            "standard_unit_rate_inc_vat":
                25.0
        }
    }

    results = collector._expand_single_rate(
        tariff,
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
    )

    assert len(results) == 3

    assert results[0]["rate"] == 0.25

def test_expand_flexible_rates():

    collector = OctopusCollector(
        MockClient()
    )

    response = {
        "results": [
            {
                "valid_from":
                    "2026-01-01T00:00:00Z",
                "valid_to":
                    "2026-01-01T01:00:00Z",
                "value_inc_vat":
                    30.0,
            }
        ]
    }

    results = collector._expand_flexible_rates(
        response,
        "2026-01-01T01:00:00Z",
    )

    assert len(results) == 2

    assert results[0]["rate"] == 0.30

