"""Validate enumeration member retrieval and validation functionality."""

from enum import Enum
from typing import Any

import pytest

from appui._enums import TimeFormat, get_enum_member


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
        (IntTestEnum, 1, IntTestEnum.ONE),
        (IntTestEnum, 2, IntTestEnum.TWO),
        (IntTestEnum, 99, IntTestEnum.NINETY_NINE),
        (FloatTestEnum, 1.1, FloatTestEnum.ONE_ONE),
        (FloatTestEnum, 1.2, FloatTestEnum.ONE_TWO),
        (FloatTestEnum, 1.99, FloatTestEnum.ONE_NINETY_NINE),
    ],
)
def test_get_enum_member(
    enum_type: type[Enum], value: Any, enum_member: Any  # noqa: ANN401
) -> None:  # fmt: skip
    """Verify successful conversion of values to their corresponding enum members."""
    assert get_enum_member(enum_type, value) == enum_member


def test_get_enum_member_invalid() -> None:
    """Verify ValueError is raised when converting invalid values to enum members."""

    with pytest.raises(
        ValueError, match=r"Value '1h' is not a valid member of TimeFormat"
    ):
        get_enum_member(TimeFormat, "1h")
