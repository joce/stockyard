"""Various enums used throughout the application."""

from enum import Enum


class Justify(Enum):
    """Justify enum for the justify property of the Label class."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class SortDirection(Enum):
    """SortDirection enum for the sort_direction property of the QuoteTableState class."""

    ASCENDING = "ascending"
    ASC = ASCENDING
    DESCENDING = "descending"
    DESC = DESCENDING
