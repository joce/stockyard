"""Definitions of the available columns for the quote table."""

from __future__ import annotations

from math import inf
from typing import Final, TypeVar

from rich.text import Text

from ._enums import Justify
from ._formatting import as_compact, as_float, as_percent
from ._quote_table_data import QuoteColumn

T = TypeVar("T", int, float)
"""TypeVar T is defined to be either an int or a float."""

TICKER_COLUMN_KEY: Final[str] = "ticker"

# TODO: Make these configurable
_GAINING_COLOR: Final[str] = "#00DD00"
_LOSING_COLOR: Final[str] = "#DD0000"


def _safe_value(v: T | None) -> float:
    """Safely retrieves the value of v.

    Note:
        If v is None, it returns the smallest representable value for type T.

    Args:
        v (T | None): The value to be retrieved. Can be of type int or float.

    Returns:
        float: The value of v if it's not None, otherwise the smallest representable
            value for type T.
    """

    return -inf if v is None else v


def _get_style_for_value(value: float) -> str:
    """Get the style string based on the sign of a value.

    Args:
        value (float): The value for which to provide a style for.

    Returns:
        str: The style string corresponding to the sign.
            - Returns _GAINING_COLOR if sign is > 0.
            - Returns _LOSING_COLOR if sign is < 0.
            - Returns an empty string if sign is 0.
    """

    return _GAINING_COLOR if value > 0 else _LOSING_COLOR if value < 0 else ""


ALL_QUOTE_COLUMNS: Final[dict[str, QuoteColumn]] = {
    "ticker": (
        QuoteColumn(
            "Ticker",
            width=8,
            key="ticker",
            format_func=lambda q: Text(q.symbol.upper(), justify=Justify.LEFT.value),
            sort_key_func=lambda q: q.symbol.lower(),
            justification=Justify.LEFT,
        )
    ),
    "last": (
        QuoteColumn(
            "Last",
            width=10,
            key="last",
            format_func=lambda q: Text(as_float(q.regular_market_price, q.price_hint)),
            sort_key_func=lambda q: (q.regular_market_price, q.symbol.lower()),
        )
    ),
    "change": (
        QuoteColumn(
            "Change",
            width=10,
            key="change",
            format_func=lambda q: Text(
                as_float(q.regular_market_change, q.price_hint),
                style=_get_style_for_value(q.regular_market_change),
            ),
            sort_key_func=lambda q: (q.regular_market_change, q.symbol.lower()),
        )
    ),
    "change_percent": (
        QuoteColumn(
            "Chg %",
            width=8,
            key="change_percent",
            format_func=lambda q: Text(
                as_percent(q.regular_market_change_percent),
                style=_get_style_for_value(q.regular_market_change_percent),
            ),
            sort_key_func=lambda q: (q.regular_market_change_percent, q.symbol.lower()),
        )
    ),
    "open": (
        QuoteColumn(
            "Open",
            width=10,
            key="open",
            format_func=lambda q: Text(as_float(q.regular_market_open, q.price_hint)),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_open),
                q.symbol.lower(),
            ),
        )
    ),
    "low": (
        QuoteColumn(
            "Low",
            width=10,
            key="low",
            format_func=lambda q: Text(
                as_float(q.regular_market_day_low, q.price_hint)
            ),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_day_low),
                q.symbol.lower(),
            ),
        )
    ),
    "high": (
        QuoteColumn(
            "High",
            width=10,
            key="high",
            format_func=lambda q: Text(
                as_float(q.regular_market_day_high, q.price_hint)
            ),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_day_high),
                q.symbol.lower(),
            ),
        )
    ),
    "52w_low": (
        QuoteColumn(
            "52w Low",
            width=10,
            key="52w_low",
            format_func=lambda q: Text(as_float(q.fifty_two_week_low, q.price_hint)),
            sort_key_func=lambda q: (q.fifty_two_week_low, q.symbol.lower()),
        )
    ),
    "52w_high": (
        QuoteColumn(
            "52w High",
            width=10,
            key="52w_high",
            format_func=lambda q: Text(as_float(q.fifty_two_week_high, q.price_hint)),
            sort_key_func=lambda q: (q.fifty_two_week_high, q.symbol.lower()),
        )
    ),
    "volume": (
        QuoteColumn(
            "Volume",
            width=10,
            key="volume",
            format_func=lambda q: Text(as_compact(q.regular_market_volume)),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_volume),
                q.symbol.lower(),
            ),
        )
    ),
    "avg_volume": (
        QuoteColumn(
            "Avg Vol",
            width=10,
            key="avg_volume",
            format_func=lambda q: Text(as_compact(q.average_daily_volume_3_month)),
            sort_key_func=lambda q: (
                _safe_value(q.average_daily_volume_3_month),
                q.symbol.lower(),
            ),
        )
    ),
    "pe": (
        QuoteColumn(
            "P/E",
            width=6,
            key="pe",
            format_func=lambda q: Text(as_float(q.trailing_pe)),
            sort_key_func=lambda q: (_safe_value(q.trailing_pe), q.symbol.lower()),
        )
    ),
    "dividend": (
        QuoteColumn(
            "Div",
            width=6,
            key="dividend",
            format_func=lambda q: Text(as_float(q.dividend_yield)),
            sort_key_func=lambda q: (_safe_value(q.dividend_yield), q.symbol.lower()),
        )
    ),
    "market_cap": (
        QuoteColumn(
            "Mkt Cap",
            width=10,
            key="market_cap",
            format_func=lambda q: Text(as_compact(q.market_cap)),
            sort_key_func=lambda q: (_safe_value(q.market_cap), q.symbol.lower()),
        )
    ),
}
"""
A dictionary that contains QuoteColumns available for the quote table.

Each QuoteColumn is keyed by its key name.
"""
