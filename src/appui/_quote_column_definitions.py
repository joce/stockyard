"""Definitions of the available columns for the quote table."""

from __future__ import annotations

from math import inf
from typing import Final, TypeVar

from rich.text import Text

from yfinance.yquote import YQuote

from ._enums import Justify
from ._formatting import as_compact, as_float, as_percent
from .enhanced_data_table import EnhancedColumn

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


ALL_QUOTE_COLUMNS: Final[dict[str, EnhancedColumn[YQuote]]] = {
    "ticker": (
        EnhancedColumn(
            "Ticker",
            width=8,
            key="ticker",
            cell_format_func=lambda q: Text(
                q.symbol.upper(), justify=Justify.LEFT.value
            ),
            sort_key_func=lambda q: q.symbol.lower(),
            justification=Justify.LEFT,
        )
    ),
    "last": (
        EnhancedColumn(
            "Last",
            width=10,
            key="last",
            cell_format_func=lambda q: Text(
                as_float(q.regular_market_price, q.price_hint)
            ),
            sort_key_func=lambda q: (q.regular_market_price, q.symbol.lower()),
        )
    ),
    "change": (
        EnhancedColumn(
            "Change",
            width=10,
            key="change",
            cell_format_func=lambda q: Text(
                as_float(q.regular_market_change, q.price_hint),
                style=_get_style_for_value(q.regular_market_change),
            ),
            sort_key_func=lambda q: (q.regular_market_change, q.symbol.lower()),
        )
    ),
    "change_percent": (
        EnhancedColumn(
            "Chg %",
            width=8,
            key="change_percent",
            cell_format_func=lambda q: Text(
                as_percent(q.regular_market_change_percent),
                style=_get_style_for_value(q.regular_market_change_percent),
            ),
            sort_key_func=lambda q: (q.regular_market_change_percent, q.symbol.lower()),
        )
    ),
    "open": (
        EnhancedColumn(
            "Open",
            width=10,
            key="open",
            cell_format_func=lambda q: Text(
                as_float(q.regular_market_open, q.price_hint)
            ),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_open),
                q.symbol.lower(),
            ),
        )
    ),
    "low": (
        EnhancedColumn(
            "Low",
            width=10,
            key="low",
            cell_format_func=lambda q: Text(
                as_float(q.regular_market_day_low, q.price_hint)
            ),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_day_low),
                q.symbol.lower(),
            ),
        )
    ),
    "high": (
        EnhancedColumn(
            "High",
            width=10,
            key="high",
            cell_format_func=lambda q: Text(
                as_float(q.regular_market_day_high, q.price_hint)
            ),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_day_high),
                q.symbol.lower(),
            ),
        )
    ),
    "52w_low": (
        EnhancedColumn(
            "52w Low",
            width=10,
            key="52w_low",
            cell_format_func=lambda q: Text(
                as_float(q.fifty_two_week_low, q.price_hint)
            ),
            sort_key_func=lambda q: (q.fifty_two_week_low, q.symbol.lower()),
        )
    ),
    "52w_high": (
        EnhancedColumn(
            "52w High",
            width=10,
            key="52w_high",
            cell_format_func=lambda q: Text(
                as_float(q.fifty_two_week_high, q.price_hint)
            ),
            sort_key_func=lambda q: (q.fifty_two_week_high, q.symbol.lower()),
        )
    ),
    "volume": (
        EnhancedColumn(
            "Volume",
            width=10,
            key="volume",
            cell_format_func=lambda q: Text(as_compact(q.regular_market_volume)),
            sort_key_func=lambda q: (
                _safe_value(q.regular_market_volume),
                q.symbol.lower(),
            ),
        )
    ),
    "avg_volume": (
        EnhancedColumn(
            "Avg Vol",
            width=10,
            key="avg_volume",
            cell_format_func=lambda q: Text(as_compact(q.average_daily_volume_3_month)),
            sort_key_func=lambda q: (
                _safe_value(q.average_daily_volume_3_month),
                q.symbol.lower(),
            ),
        )
    ),
    "pe": (
        EnhancedColumn(
            "P/E",
            width=6,
            key="pe",
            cell_format_func=lambda q: Text(as_float(q.trailing_pe)),
            sort_key_func=lambda q: (_safe_value(q.trailing_pe), q.symbol.lower()),
        )
    ),
    "dividend": (
        EnhancedColumn(
            "Div",
            width=6,
            key="dividend",
            cell_format_func=lambda q: Text(as_float(q.dividend_yield)),
            sort_key_func=lambda q: (_safe_value(q.dividend_yield), q.symbol.lower()),
        )
    ),
    "market_cap": (
        EnhancedColumn(
            "Mkt Cap",
            width=10,
            key="market_cap",
            cell_format_func=lambda q: Text(as_compact(q.market_cap)),
            sort_key_func=lambda q: (_safe_value(q.market_cap), q.symbol.lower()),
        )
    ),
}
"""
A dictionary that contains QuoteColumns available for the quote table.

Each QuoteColumn is keyed by its key name.
"""
