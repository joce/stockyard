"""Validate enumeration member retrieval and validation functionality."""

from __future__ import annotations

from enum import Enum

import pytest

from appui._enums import TimeFormat, coerce_enum_member


class IntTestEnum(Enum):
    """Test fixture enum containing integer values."""

    ONE = 1
    TWO = 2
    NINETY_NINE = 99


class FloatTestEnum(Enum):
    """Test fixture enum containing float values."""

    ONE_ONE = 1.1
    ONE_TWO = 1.2
    ONE_NINETY_NINE = 1.99


@pytest.mark.parametrize(
    ("enum_type", "value", "enum_member"),
    [
        (TimeFormat, "12h", TimeFormat.TWELVE_HOUR),
        (TimeFormat, "24h", TimeFormat.TWENTY_FOUR_HOUR),
        (TimeFormat, "TWELVE_HOUR", TimeFormat.TWELVE_HOUR),
        (TimeFormat, " 24H ", TimeFormat.TWENTY_FOUR_HOUR),
        (TimeFormat, TimeFormat.TWENTY_FOUR_HOUR, TimeFormat.TWENTY_FOUR_HOUR),
        (IntTestEnum, 1, IntTestEnum.ONE),
        (IntTestEnum, 2, IntTestEnum.TWO),
        (IntTestEnum, "TWO", IntTestEnum.TWO),
        (IntTestEnum, 99, IntTestEnum.NINETY_NINE),
        (FloatTestEnum, 1.1, FloatTestEnum.ONE_ONE),
        (FloatTestEnum, "ONE_TWO", FloatTestEnum.ONE_TWO),
        (FloatTestEnum, 1.2, FloatTestEnum.ONE_TWO),
        (FloatTestEnum, 1.99, FloatTestEnum.ONE_NINETY_NINE),
    ],
)
def test_coerce_enum_member_succeeds(
    enum_type: type[Enum], value: str | float | TimeFormat, enum_member: Enum
) -> None:
    """Verify successful conversion of values to their corresponding enum members."""

    assert coerce_enum_member(enum_type, value) == enum_member


def test_coerce_enum_member_with_unknown_values_returns_none() -> None:
    """Non-matching values produce ``None`` when strict mode is disabled."""

    assert coerce_enum_member(TimeFormat, "1h") is None
    assert coerce_enum_member(TimeFormat, None) is None


def test_coerce_enum_member_strict_with_unknown_values_raises() -> None:
    """Strict mode raises a ``ValueError`` for unknown values."""

    with pytest.raises(
        ValueError, match=r"Value '1h' is not a valid member of TimeFormat"
    ):
        coerce_enum_member(TimeFormat, "1h", strict=True)

    with pytest.raises(
        ValueError, match=r"Value 'None' is not a valid member of TimeFormat"
    ):
        coerce_enum_member(TimeFormat, None, strict=True)
