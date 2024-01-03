"""Definitions of the available columns for the quote table."""

from __future__ import annotations

from math import inf
from typing import Final, Optional, TypeVar

from ._enums import Justify
from ._formatting import as_float, as_percent, as_shrunk_int
from ._quote_table_data import QuoteColumn

T = TypeVar("T", int, float)
"""TypeVar T is defined to be either an int or a float."""


def _safe_value(v: Optional[T]) -> float:
    """
    Safely retrieves the value of v. If v is None, it returns the smallest representable
    value for type T.

    Args:
        v (Optional[T]): The value to be retrieved. Can be of type int or float.

    Returns:
        float: The value of v if it's not None, otherwise the smallest representable
            value for type T.
    """

    return -inf if v is None else v


def _sign(v: T) -> int:
    """
    Determines the sign of a given value.

    Args:
        v (T): The value for which the sign is to be determined.

    Returns:
        int: Returns 1 if the value is greater than 0, -1 if less than 0, and 0 if the
            value is exactly 0.
    """

    return 1 if v > 0 else -1 if v < 0 else 0


ALL_QUOTE_COLUMNS: Final[dict[str, QuoteColumn]] = {
    "ticker": (
        QuoteColumn(
            "Ticker",
            8,
            "ticker",
            lambda q: q.symbol.upper(),
            lambda q: q.symbol.lower(),
            justification=Justify.LEFT,
        )
    ),
    "last": (
        QuoteColumn(
            "Last",
            10,
            "last",
            lambda q: as_float(q.regular_market_price, q.price_hint),
            lambda q: (q.regular_market_price, q.symbol.lower()),
        )
    ),
    "change": (
        QuoteColumn(
            "Change",
            10,
            "change",
            lambda q: as_float(q.regular_market_change, q.price_hint),
            lambda q: (q.regular_market_change, q.symbol.lower()),
            lambda q: _sign(q.regular_market_change),
        )
    ),
    "change_percent": (
        QuoteColumn(
            "Chg %",
            8,
            "change_percent",
            lambda q: as_percent(q.regular_market_change_percent),
            lambda q: (q.regular_market_change_percent, q.symbol.lower()),
            lambda q: _sign(q.regular_market_change_percent),
        )
    ),
    "open": (
        QuoteColumn(
            "Open",
            10,
            "open",
            lambda q: as_float(q.regular_market_open, q.price_hint),
            lambda q: (_safe_value(q.regular_market_open), q.symbol.lower()),
        )
    ),
    "low": (
        QuoteColumn(
            "Low",
            10,
            "low",
            lambda q: as_float(q.regular_market_day_low, q.price_hint),
            lambda q: (_safe_value(q.regular_market_day_low), q.symbol.lower()),
        )
    ),
    "high": (
        QuoteColumn(
            "High",
            10,
            "high",
            lambda q: as_float(q.regular_market_day_high, q.price_hint),
            lambda q: (_safe_value(q.regular_market_day_high), q.symbol.lower()),
        )
    ),
    "52w_low": (
        QuoteColumn(
            "52w Low",
            10,
            "52w_low",
            lambda q: as_float(q.fifty_two_week_low, q.price_hint),
            lambda q: (q.fifty_two_week_low, q.symbol.lower()),
        )
    ),
    "52w_high": (
        QuoteColumn(
            "52w High",
            10,
            "52w_high",
            lambda q: as_float(q.fifty_two_week_high, q.price_hint),
            lambda q: (q.fifty_two_week_high, q.symbol.lower()),
        )
    ),
    "volume": (
        QuoteColumn(
            "Volume",
            10,
            "volume",
            lambda q: as_shrunk_int(q.regular_market_volume),
            lambda q: (_safe_value(q.regular_market_volume), q.symbol.lower()),
        )
    ),
    "avg_volume": (
        QuoteColumn(
            "Avg Vol",
            10,
            "avg_volume",
            lambda q: as_shrunk_int(q.average_daily_volume_3_month),
            lambda q: (_safe_value(q.average_daily_volume_3_month), q.symbol.lower()),
        )
    ),
    "pe": (
        QuoteColumn(
            "P/E",
            6,
            "pe",
            lambda q: as_float(q.trailing_pe),
            lambda q: (_safe_value(q.trailing_pe), q.symbol.lower()),
        )
    ),
    "dividend": (
        QuoteColumn(
            "Div",
            6,
            "dividend",
            lambda q: as_float(q.dividend_yield),
            lambda q: (_safe_value(q.dividend_yield), q.symbol.lower()),
        )
    ),
    "market_cap": (
        QuoteColumn(
            "Mkt Cap",
            10,
            "market_cap",
            lambda q: as_shrunk_int(q.market_cap),
            lambda q: (_safe_value(q.market_cap), q.symbol.lower()),
        )
    ),
}
"""
A dictionary that contains QuoteColumns available for the quote table.
Each QuoteColumn is keyed by its key name.
"""
