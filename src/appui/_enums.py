"""Various enums used throughout the application."""

from __future__ import annotations

import logging
from enum import Enum, IntEnum
from tkinter import N
from typing import TypeVar


class StockyardEnum(Enum):
    """Base class for all Stockyard enums.

    StockyardEnum subclasses must have lowercase string values.
    """

    def __str__(self) -> str:
        return str(self.value)


class Justify(StockyardEnum):
    """Justify enum for the Label class."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class SortDirection(StockyardEnum):
    """SortDirection enum for the QuoteTableState class."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class TimeFormat(StockyardEnum):
    """TimeFormat enum for time display format."""

    TWELVE_HOUR = "12h"
    TWENTY_FOUR_HOUR = "24h"


class LoggingLevel(IntEnum):
    """Logging levels supported by the Stockyard application."""

    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


T = TypeVar("T", bound=StockyardEnum)
U = TypeVar("U", str, int, float, None)


def get_enum_member(enum_type: type[T], value: U) -> T:
    """Get the enum member for a given string value.

    Args:
        enum_type (Type[T]): The enum type.
        value (U | None): The value to get the enum member for.

    Raises:
        ValueError: If the value is not a valid member of the enum.

    Returns:
        T: The enum member.
    """

    for member in enum_type:
        if member.value == value:
            return member
    error_msg = f"Value '{value}' is not a valid member of {enum_type.__name__}"
    raise ValueError(error_msg)


def coerce_enum_member(enum_type: type[T], value: U) -> T | None:
    """Attempt to coerce ``value`` into a member of ``enum_type``.

    Args:
        enum_type: The Enum class to coerce into.
        value: The incoming value that may represent an enum member.

    Returns:
        The matching enum member, or ``None`` if no match can be deduced.
    """

    if isinstance(value, enum_type):
        return value
    if isinstance(value, str):
        try:
            return get_enum_member(enum_type, value.lower())
        except ValueError:
            return None
    return None
