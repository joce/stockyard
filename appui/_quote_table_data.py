"""
This module provides the data structures for the quote table in the application user interface (appui).
It defines the QuoteCell, QuoteRow and QuoteColumn classes, which represent a cell, a row and a column
in the quote table respectively.
"""

from typing import Any, Callable

from yfinance import YQuote

from ._enums import Justify


class QuoteCell:
    """Definition of a cell for the quote table."""

    def __init__(self, value: str, sign: int, justify: Justify) -> None:
        """
        Definition of a cell for the quote table.

        Args:
            value (str): The value to display.
            sign (int): The sign of the value, i.e. negative (-1), positive (1) or neutral (0).
            justification (Justify): The justification of the text in the cell.
        """

        self._value = value
        self._sign = sign
        self._justify = justify

    @property
    def value(self) -> str:
        """The value to display."""

        return self._value

    @property
    def sign(self) -> int:
        """The sign of the value, i.e. negative (-1), positive (1) or neutral (0)."""

        return self._sign

    @property
    def justify(self) -> Justify:
        """The justification of the text in the cell."""

        return self._justify


class QuoteRow:
    """Definition of row for the quote table."""

    def __init__(self, key: str, values: list[QuoteCell]) -> None:
        """
        Definition of a row for the quote table.

        Args:
            key (str): The key of the row.
            values (list[QuoteCell]): The values of the row.
        """

        self._key = key
        self._values = values

    @property
    def key(self) -> str:
        """The key of the row."""

        return self._key

    @property
    def values(self) -> list[QuoteCell]:
        """The values of the row."""

        return self._values


class QuoteColumn:
    """
    This class represents a column in the quote table. It defines the properties and
    behaviors of the column, such as its name, width, key, and formatting function.
    """

    def __init__(
        self,
        name: str,
        width: int,
        key: str,
        format_func: Callable[[YQuote], str],
        sort_key_func: Callable[[YQuote], Any],
        sign_indicator_func: Callable[[YQuote], int] = lambda _: 0,
        justify: Justify = Justify.RIGHT,
    ) -> None:
        """
        Initializes the QuoteColumn object.

        Args:
            name (str): The name of the column.
            width (int): The width of the column.
            key (str): The key of the column.
            format_func (Callable[[YQuote], str]): The function used to format the column.
            sort_key_func (Callable[[YQuote], Any]): The function used provide the sort key for the column.
            sign_indicator_func (Callable[[YQuote], int], optional):
                The function used to provide the sign indicator for the column. Defaults to a function that returns 0 (neutral).
            justify (Justify, optional): The justification of the column. Defaults to Justify.RIGHT.
        """

        self._name: str = name
        self._width: int = width
        self._key: str = key
        self._format_func: Callable[[YQuote], str] = format_func
        self._sort_key_func: Callable[[YQuote], Any] = sort_key_func
        self._sign_indicator_func: Callable[[YQuote], int] = sign_indicator_func
        self._justification: Justify = justify

    @property
    def name(self) -> str:
        """The name of the column."""

        return self._name

    @property
    def width(self) -> int:
        """The width of the column."""

        return self._width

    @property
    def key(self) -> str:
        """The key of the column."""

        return self._key

    @property
    def format_func(self) -> Callable[[YQuote], str]:
        """The function used to format the column."""

        return self._format_func

    @property
    def sort_key_func(self) -> Callable[[YQuote], Any]:
        """The function used provide the sort key for the column."""

        return self._sort_key_func

    @property
    def sign_indicator_func(self) -> Callable[[YQuote], int]:
        """The function used to provide the sign indicator for the column."""

        return self._sign_indicator_func

    @property
    def justification(self) -> Justify:
        """The justification of the column. Defaults to Justify.RIGHT."""

        return self._justification
