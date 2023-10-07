"""
Definition for the available columns
"""
from ._formatting import as_float, as_percent, as_shrunk_int
from ._quote_column import QuoteColumn
from .enums import Justify

ALL_QUOTE_COLUMNS: dict[str, QuoteColumn] = {
    "ticker": (
        QuoteColumn(
            "Ticker",
            8,
            "ticker",
            lambda q: q.symbol,
            lambda q: q.symbol.lower(),
            Justify.LEFT,
        )
    ),
    "last": (
        QuoteColumn(
            "Last",
            10,
            "last",
            lambda q: as_float(q.regular_market_price, q.price_hint),
            lambda q: q.regular_market_price,
        )
    ),
    "change": (
        QuoteColumn(
            "Change",
            8,
            "change",
            lambda q: as_float(q.regular_market_change, q.price_hint),
            lambda q: q.regular_market_change,
        )
    ),
    "change_percent": (
        QuoteColumn(
            "Change%",
            8,
            "change_percent",
            lambda q: as_percent(q.regular_market_change_percent),
            lambda q: q.regular_market_change_percent,
        )
    ),
    "open": (
        QuoteColumn(
            "Open",
            10,
            "open",
            lambda q: as_float(q.regular_market_open, q.price_hint),
            lambda q: q.regular_market_open,
        )
    ),
    "low": (
        QuoteColumn(
            "Low",
            10,
            "low",
            lambda q: as_float(q.regular_market_day_low, q.price_hint),
            lambda q: q.regular_market_day_low,
        )
    ),
    "high": (
        QuoteColumn(
            "High",
            10,
            "high",
            lambda q: as_float(q.regular_market_day_high, q.price_hint),
            lambda q: q.regular_market_day_high,
        )
    ),
    "52w_low": (
        QuoteColumn(
            "52w Low",
            10,
            "52_low",
            lambda q: as_float(q.fifty_two_week_low, q.price_hint),
            lambda q: q.fifty_two_week_low,
        )
    ),
    "52w_high": (
        QuoteColumn(
            "52w High",
            10,
            "52_high",
            lambda q: as_float(q.fifty_two_week_high, q.price_hint),
            lambda q: q.fifty_two_week_high,
        )
    ),
    "volume": (
        QuoteColumn(
            "Volume",
            8,
            "volume",
            lambda q: as_shrunk_int(q.regular_market_volume),
            lambda q: q.regular_market_volume,
        )
    ),
    "avg_volume": (
        QuoteColumn(
            "Avg Vol",
            8,
            "avg_volume",
            lambda q: as_shrunk_int(q.average_daily_volume_3_month),
            lambda q: q.average_daily_volume_3_month,
        )
    ),
    "pe": (
        QuoteColumn(
            "P/E", 6, "pe", lambda q: as_float(q.trailing_pe), lambda q: q.trailing_pe
        )
    ),
    "dividend": (
        QuoteColumn(
            "Dividend",
            6,
            "dividend",
            lambda q: as_float(q.dividend_yield),
            lambda q: q.dividend_yield,
        )
    ),
    "market_cap": (
        QuoteColumn(
            "Mkt Cap",
            8,
            "market_cap",
            lambda q: as_shrunk_int(q.market_cap),
            lambda q: q.market_cap,
        )
    ),
}
"""
A dictionary of Columns and the associated lambda functions to format the a YQuote data into a string
"""
