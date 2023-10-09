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
        sign_indicator_func: Callable[[YQuote], int] = lambda _: 0,
        justify: Justify = Justify.RIGHT,
    ) -> None:
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
