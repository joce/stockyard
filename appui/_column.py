from typing import Any, Callable

from yfinance import YQuote

from .enums import Justify


class Column:
    """Definition of column for the quote table."""

    def __init__(
        self,
        name: str,
        width: int,
        key: str,
        format_func: Callable[[YQuote], str],
        sort_key: Callable[[YQuote], Any],
        justify: Justify = Justify.RIGHT,
    ) -> None:
        self.name = name
        self.width = width
        self.key = key
        self.format_func = format_func
        self.sort_key = sort_key
        self.justification = justify
