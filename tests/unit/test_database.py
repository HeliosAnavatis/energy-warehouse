from unittest.mock import Mock

from database.database import Database


# ============================================================================
# Test Helper
# ============================================================================

def create_database():

    db = Database.__new__(Database)

    db.backend = Mock()

    return db


# ============================================================================
# Supplier
# ============================================================================

def test_load_supplier():

    db = create_database()

    db.load_supplier("Octopus")

    db.backend.load_supplier.assert_called_once_with(
        "Octopus",
    )


# ============================================================================
# Account
# ============================================================================

def test_load_account():

    db = create_database()

    db.load_account(
        account_number="A12345",
        supplier_id=1,
        active_from="2024-01-01",
        active_to=None,
    )

    db.backend.load_account.assert_called_once_with(
        "A12345",
        1,
        "2024-01-01",
        None,
    )


# ============================================================================
# Meter
# ============================================================================

def test_load_meter():

    db = create_database()

    db.load_meter(
        account_id=1,
        identifier="123456",
        serial_number="ABC123",
        is_export=False,
        fuel="E",
    )

    db.backend.load_meter.assert_called_once_with(
        1,
        "123456",
        "ABC123",
        False,
        "E",
    )


# ============================================================================
# Tariff
# ============================================================================

def test_load_tariff():

    db = create_database()

    db.load_tariff(
        meter_id=1,
        tariff_code="TEST",
        product_code="PRODUCT",
        tariff_name="Test Tariff",
        tariff_type="Import",
        applies_from="2024-01-01",
        applies_to=None,
    )

    db.backend.load_tariff.assert_called_once()


# ============================================================================
# Meter Readings
# ============================================================================

def test_load_meter_readings():

    db = create_database()

    history = [
        {
            "interval_start":
                "2026-01-01T00:00:00Z",
            "reading":
                1.23,
        }
    ]

    db.load_meter_readings(
        meter_id=1,
        history=history,
    )

    db.backend.load_meter_readings.assert_called_once_with(
        1,
        history,
    )


# ============================================================================
# Energy Rates
# ============================================================================

def test_load_energy_rate():

    db = create_database()

    history = [
        {
            "interval_start":
                "2026-01-01T00:00:00Z",
            "rate":
                10.5,
        }
    ]

    db.load_energy_rate(
        1,
        history,
    )

    db.backend.load_energy_rate.assert_called_once_with(
        1,
        history,
    )


# ============================================================================
# Battery SoC
# ============================================================================

def test_load_battery_soc():

    db = create_database()

    history = [
        {
            "timestamp":
                "2026-01-01T00:00:00Z",
            "soc":
                72.5,
        }
    ]

    db.load_battery_soc(
        history,
    )

    db.backend.load_battery_soc.assert_called_once_with(
        history,
    )


# ============================================================================
# Account Lookup
# ============================================================================

def test_get_account_id():

    db = create_database()

    db.get_account_id(
        "A12345"
    )

    db.backend.get_account_id.assert_called_once_with(
        "A12345"
    )


# ============================================================================
# Meter Lookup
# ============================================================================

def test_get_active_meters():

    db = create_database()

    db.get_active_meters(
        1,
    )

    db.backend.get_active_meters.assert_called_once_with(
        1,
    )


def test_get_active_tariff():

    db = create_database()

    db.get_active_tariff(
        1,
        "2026-01-01",
    )

    db.backend.get_active_tariff.assert_called_once_with(
        1,
        "2026-01-01",
    )


# ============================================================================
# Close
# ============================================================================

def test_close():

    db = create_database()

    db.close()

    db.backend.close.assert_called_once()