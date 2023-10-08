from typing import Any, Callable

from yfinance import YQuote

from ._enums import Justify


class QuoteColumn:
    """Definition of column for the quote table."""

    def __init__(
        self,
        name: str,
        width: int,
        key: str,
        format_func: Callable[[YQuote], str],
        sort_key_func: Callable[[YQuote], Any],
        justify: Justify = Justify.RIGHT,
    ) -> None:
        self.name = name
        """The name of the column."""

        self.width = width
        """The width of the column."""

        self.key = key
        """The key of the column."""

        self.format_func = format_func
        """The function used to format the column."""

        self.sort_key_func = sort_key_func
        """The function used provide the sort key for the column."""

        self.justification = justify
        """The justification of the column. Defaults to Justify.RIGHT."""
