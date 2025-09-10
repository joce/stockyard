"""Validate The behavior of the `YQuote` class."""

import sys
from typing import TYPE_CHECKING

from tests.fake_yfinance import FakeYFinance
from yfinance.enums import MarketState, QuoteType

if TYPE_CHECKING:
    from datetime import datetime

    from yfinance import YQuote

if sys.version_info >= (3, 11):
    from zoneinfo import ZoneInfo

else:
    import pytz


def test_yquote_dates() -> None:
    """Ensure the date formats are consistent for different versions of Python."""

    aapl_quote: YQuote
    gold_fut: YQuote
    aapl_quote, gold_fut = FakeYFinance().retrieve_quotes(["AAPL", "GC=F"])
    assert gold_fut.expire_date is not None
    assert gold_fut.expire_date.strftime("%Y-%m-%d %H:%M:%S") == "2023-12-27 00:00:00"
    assert gold_fut.quote_type == QuoteType.FUTURE
    assert gold_fut.market_state == MarketState.REGULAR

    assert aapl_quote.earnings_datetime is not None
    assert aapl_quote.quote_type == QuoteType.EQUITY
    assert aapl_quote.market_state == MarketState.REGULAR

    tz_adjusted_datetime: datetime
    if sys.version_info >= (3, 11):
        tz_info: ZoneInfo = ZoneInfo(aapl_quote.exchange_timezone_name)
        tz_adjusted_datetime = aapl_quote.earnings_datetime.astimezone(tz_info)

    else:
        tz_info = pytz.timezone(aapl_quote.exchange_timezone_name)
        tz_adjusted_datetime = aapl_quote.earnings_datetime.astimezone(tz_info)

    assert tz_adjusted_datetime.strftime("%Y-%m-%d %H:%M:%S") == "2023-11-02 17:00:00"
