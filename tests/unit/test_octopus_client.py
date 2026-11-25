from unittest.mock import Mock
from unittest.mock import patch

import pytest

from sources.octopus.client import (
    OctopusClient,
)

def test_tariff_to_product_code():

    client = OctopusClient(
        "https://api.octopus.energy/v1",
        "ACCOUNT",
        "KEY",
    )

    product = client.tariff_to_product_code(
        "E-1R-IOG-SMB-FIX-LOYAL2-12M-26-09-28-A"
    )

    assert (
        product
        == "IOG-SMB-FIX-LOYAL2-12M-26-09-28"
    )

def test_get_readings_invalid_fuel():

    client = OctopusClient(
        "https://api.octopus.energy/v1",
        "ACCOUNT",
        "KEY",
    )

    with pytest.raises(ValueError):

        client.get_readings(
            meter_point="123",
            meter_serial="ABC",
            meter_fuel="X",
            start="2026-01-01",
            end="2026-01-02",
        )

@patch(
    "sources.octopus.client.requests.get"
)
def test_get_readings_electricity(
    mock_get
):

    response = Mock()

    response.json.return_value = {}

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = OctopusClient(
        "https://api.octopus.energy/v1",
        "ACCOUNT",
        "KEY",
    )

    client.get_readings(
        meter_point="123456",
        meter_serial="ABC123",
        meter_fuel="E",
        start="A",
        end="B",
    )

    args, _ = mock_get.call_args

    assert (
        "/electricity-meter-points/"
        in args[0]
    )

@patch(
    "sources.octopus.client.requests.get"
)
def test_get_readings_gas(
    mock_get
):

    response = Mock()

    response.json.return_value = {}

    response.raise_for_status.return_value = None

    mock_get.return_value = response

    client = OctopusClient(
        "https://api.octopus.energy/v1",
        "ACCOUNT",
        "KEY",
    )

    client.get_readings(
        meter_point="123456",
        meter_serial="ABC123",
        meter_fuel="G",
        start="A",
        end="B",
    )

    args, _ = mock_get.call_args

    assert (
        "/gas-meter-points/"
        in args[0]
    )

