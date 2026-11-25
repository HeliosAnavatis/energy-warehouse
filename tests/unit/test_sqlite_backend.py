from database.sqlite import SQLiteBackend


def create_db(tmp_path):

    db_file = tmp_path / "test.db"

    return SQLiteBackend(
        str(db_file)
    )


# ============================================================================
# Supplier
# ============================================================================

def test_load_supplier_creates_supplier(
    tmp_path,
):

    db = create_db(tmp_path)

    supplier_id = db.load_supplier(
        "Octopus"
    )

    assert supplier_id == 1

    db.close()


def test_load_supplier_is_idempotent(
    tmp_path,
):

    db = create_db(tmp_path)

    id1 = db.load_supplier(
        "Octopus"
    )

    id2 = db.load_supplier(
        "Octopus"
    )

    assert id1 == id2

    db.close()


# ============================================================================
# Account
# ============================================================================

def test_load_account_creates_account(
    tmp_path,
):

    db = create_db(tmp_path)

    supplier_id = db.load_supplier(
        "Octopus"
    )

    account_id = db.load_account(
        account_number="A12345",
        supplier_id=supplier_id,
        active_from="2024-01-01",
        active_to=None,
    )

    assert account_id == 1

    db.close()


def test_get_account_id(
    tmp_path,
):

    db = create_db(tmp_path)

    supplier_id = db.load_supplier(
        "Octopus"
    )

    db.load_account(
        account_number="A12345",
        supplier_id=supplier_id,
        active_from="2024-01-01",
        active_to=None,
    )

    account_id = db.get_account_id(
        "A12345"
    )

    assert account_id == 1

    db.close()


# ============================================================================
# Meter
# ============================================================================

def test_load_meter_creates_meter(
    tmp_path,
):

    db = create_db(tmp_path)

    supplier_id = db.load_supplier(
        "Octopus"
    )

    account_id = db.load_account(
        "A12345",
        supplier_id,
        "2024-01-01",
        None,
    )

    meter_id = db.load_meter(
        account_id=account_id,
        identifier="123456",
        serial_number="ABC123",
        is_export=False,
        fuel="E",
    )

    assert meter_id == 1

    db.close()


def test_get_active_meters(
    tmp_path,
):

    db = create_db(tmp_path)

    supplier_id = db.load_supplier(
        "Octopus"
    )

    account_id = db.load_account(
        "A12345",
        supplier_id,
        "2024-01-01",
        None,
    )

    db.load_meter(
        account_id=account_id,
        identifier="123456",
        serial_number="ABC123",
        is_export=False,
        fuel="E",
    )

    meters = db.get_active_meters(
        account_id
    )

    assert len(meters) == 1

    assert (
        meters[0]["identifier"]
        == "123456"
    )

    db.close()


# ============================================================================
# Tariff
# ============================================================================

def test_load_tariff_creates_tariff(
    tmp_path,
):

    db = create_db(tmp_path)

    supplier_id = db.load_supplier(
        "Octopus"
    )

    account_id = db.load_account(
        "A12345",
        supplier_id,
        "2024-01-01",
        None,
    )

    meter_id = db.load_meter(
        account_id,
        "123456",
        "ABC123",
        False,
        "E",
    )

    tariff_id = db.load_tariff(
        meter_id=meter_id,
        tariff_code="E-TEST",
        product_code="TEST",
        tariff_name="Test Tariff",
        tariff_type="Import",
        applies_from="2024-01-01",
        applies_to=None,
    )

    assert tariff_id == 1

    db.close()


# ============================================================================
# Meter Readings
# ============================================================================

def test_load_meter_readings(
    tmp_path,
):

    db = create_db(tmp_path)

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

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM reading
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 1

    db.close()


def test_meter_readings_upsert(
    tmp_path,
):

    db = create_db(tmp_path)

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

    db.load_meter_readings(
        meter_id=1,
        history=history,
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM reading
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 1

    db.close()


# ============================================================================
# Weather
# ============================================================================

class WeatherConfig:

    latitude = 51.7
    longitude = -0.4


def test_load_weather(
    tmp_path,
):

    db = create_db(tmp_path)

    history = [
        {
            "timestamp":
                "2026-01-01T00:00",
            "temperature":
                10.0,
            "cloud_cover":
                50,
            "solar_radiation":
                5.0,
        }
    ]

    db.load_weather(
        WeatherConfig(),
        history,
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM weather
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 1

    db.close()


# ============================================================================
# Battery SoC
# ============================================================================

def test_load_battery_soc(
    tmp_path,
):

    db = create_db(tmp_path)

    history = [
        {
            "timestamp":
                "2026-01-01T00:00:00",
            "soc":
                75.0,
        }
    ]

    db.load_battery_soc(
        history
    )

    db.cursor.execute(
        """
        SELECT COUNT(*)
        FROM battery_soc
        """
    )

    count = db.cursor.fetchone()[0]

    assert count == 1

    db.close()