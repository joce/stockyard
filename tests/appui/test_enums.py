# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from enum import Enum
from typing import Any, Type

import pytest

from appui._enums import TimeFormat, get_enum_member


class IntTestEnum(Enum):
    ONE = 1
    TWO = 2
    NINETY_NINE = 99


class FloatTestEnum(Enum):
    ONE_ONE = 1.1
    ONE_TWO = 1.2
    ONE_NINETY_NINE = 1.99


@pytest.mark.parametrize(
    "enum_type, value, enum_member",
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
def test_get_enum_member(enum_type: Type[Enum], value: Any, enum_member: Any):
    assert get_enum_member(enum_type, value) == enum_member


def test_get_enum_member_invalid():
    with pytest.raises(ValueError):
        get_enum_member(TimeFormat, "1h")
