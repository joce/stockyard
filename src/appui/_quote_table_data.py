"""Define data structures for managing and displaying quote tables in the app's UI.

Contains the core classes QuoteCell, QuoteRow, and QuoteColumn that together form the
building blocks of a quote table's structure and behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from ._enums import Justify

if TYPE_CHECKING:
    from yfinance import YQuote


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
    """Represents a quote table column and defines its display properties and behaviors.

    Contains settings for the column's appearance (name, width, justification) and
    behavior (formatting, sorting, and sign indication).
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
