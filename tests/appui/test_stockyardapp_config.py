"""Test behavior of StockyardConfig model."""

from __future__ import annotations

import logging

import pytest

from appui._enums import TimeFormat
from appui.stockyard_config import StockyardConfig


def test_default_values() -> None:
    """Test that default values are set correctly."""
    config = StockyardConfig()

    assert config.title == "Stockyard"
    assert config.log_level == logging.INFO
    assert config.time_format == TimeFormat.TWENTY_FOUR_HOUR


def test_basic_assignment() -> None:
    """Test basic field assignment with valid values."""
    config = StockyardConfig(
        title="Custom Title",
        log_level=logging.DEBUG,
        time_format=TimeFormat.TWELVE_HOUR,
    )

    assert config.title == "Custom Title"
    assert config.log_level == logging.DEBUG
    assert config.time_format == TimeFormat.TWELVE_HOUR


@pytest.mark.parametrize(
    ("input_level", "expected_level"),
    [
        (logging.NOTSET, logging.NOTSET),
        (logging.DEBUG, logging.DEBUG),
        (logging.INFO, logging.INFO),
        (logging.WARNING, logging.WARNING),
        (logging.ERROR, logging.ERROR),
        (logging.CRITICAL, logging.CRITICAL),
        (9999, logging.ERROR),
    ],
)
def test_log_level_validator_with_valid_values(
    input_level: int, expected_level: int
) -> None:
    """Test log level validator with valid integer values."""
    config = StockyardConfig(log_level=input_level)
    assert config.log_level == expected_level


@pytest.mark.parametrize(
    ("input_string", "expected_level"),
    [
        ("NOTSET", logging.NOTSET),
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
        ("INVALID", logging.ERROR),
    ],
)
def test_log_level_validator_with_string_via_model_validate(
    input_string: str, expected_level: int
) -> None:
    """Test log level validator with string values via model_validate."""
    data = {"log_level": input_string}
    config = StockyardConfig.model_validate(data)
    assert config.log_level == expected_level


@pytest.mark.parametrize(
    ("input_string", "expected_format"),
    [
        ("12h", TimeFormat.TWELVE_HOUR),
        ("24h", TimeFormat.TWENTY_FOUR_HOUR),
        ("invalid", TimeFormat.TWENTY_FOUR_HOUR),
    ],
)
def test_time_format_validator_with_string_via_model_validate(
    input_string: str, expected_format: TimeFormat
) -> None:
    """Test time format validator with string values via model_validate."""
    data = {"time_format": input_string}
    config = StockyardConfig.model_validate(data)
    assert config.time_format == expected_format


def test_roundtrip_serialization() -> None:
    """Model dumps and validates back with equivalent values."""
    original = StockyardConfig(
        title="Test Config",
        log_level=logging.WARNING,
        time_format=TimeFormat.TWELVE_HOUR,
    )

    # Serialize
    data = original.model_dump()

    # Deserialize
    restored = StockyardConfig.model_validate(data)

    assert restored.title == original.title
    assert restored.log_level == original.log_level
    assert restored.time_format == original.time_format
