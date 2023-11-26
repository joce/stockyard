"""
This module provides the data structures for the quote table in the application user
interface (appui).
It defines the QuoteCell, QuoteRow and QuoteColumn classes, which represent a cell, a
row and a column in the quote table respectively.
"""

from dataclasses import dataclass
from typing import Any, Callable

from yfinance import YQuote

from ._enums import Justify


@dataclass(frozen=True)
class QuoteCell:
    """Definition of a cell for the quote table."""

    value: str
    """The value to display."""

    sign: int
    """The sign of the value, i.e. negative (-1), positive (1) or neutral (0)."""

    justify: Justify
    """The justification of the text in the cell."""


@dataclass(frozen=True)
class QuoteRow:
    """Definition of row for the quote table."""

    key: str
    """The key of the row."""

    values: list[QuoteCell]
    """The values of the row."""


@dataclass(frozen=True)
class QuoteColumn:
    """
    This class represents a column in the quote table. It defines the properties and
    behaviors of the column, such as its name, width, key, and formatting function.
    """

    name: str
    """The name of the column."""

    width: int
    """The width of the column."""

    key: str
    """The key of the column."""

    format_func: Callable[[YQuote], str]
    """ The function used to format the column."""

    sort_key_func: Callable[[YQuote], Any]
    """The function used provide the sort key for the column."""

    sign_indicator_func: Callable[[YQuote], int] = lambda _: 0
    """
    The function used to provide the sign indicator for the column.
    Defaults to a function that returns 0 (neutral).
    """

    justification: Justify = Justify.RIGHT
    """
    The justification of the column.
    Defaults to Justify.RIGHT.
    """
