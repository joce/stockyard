"""Various enums used throughout the application."""

from enum import Enum
from typing import Optional, Type, TypeVar


class Justify(Enum):
    """Justify enum for the justify property of the Label class."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class SortDirection(Enum):
    """SortDirection enum for the sort_direction property of the QuoteTableState class."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class TimeFormat(Enum):
    """TimeFormat enum for time display format."""

    TWELVE_HOUR = "12h"
    TWENTY_FOUR_HOUR = "24h"


T = TypeVar("T", bound=Enum)
U = TypeVar("U", str, int, float)


def get_enum_member(enum_type: Type[T], value: Optional[U]) -> T:
    """Get the enum member for a given string value.

    Args:
        enum_type (Type[T]): The enum type.
        value (Optional[U]): The value to get the enum member for.

    Raises:
        ValueError: If the value is not a valid member of the enum.

    Returns:
        T: The enum member.
    """
    for member in enum_type:
        if member.value == value:
            return member
    raise ValueError(f"Value '{value}' is not a valid member of {enum_type.__name__}")
