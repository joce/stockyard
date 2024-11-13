"""Validate The behavior of the `YQuote` class."""

from typing import TYPE_CHECKING

from tests.fake_yfinance import FakeYFinance

if TYPE_CHECKING:
    from yfinance import YQuote


def test_yquote_dates():
    """Ensure the date formats are consistent for different versions of Python."""

    aapl_quote: YQuote
    gold_fut: YQuote
    aapl_quote, gold_fut = FakeYFinance().retrieve_quotes(["AAPL", "GC=F"])
    assert gold_fut.expire_date is not None
    assert gold_fut.expire_date.strftime("%Y-%m-%d %H:%M:%S") == "2023-12-27 00:00:00"
    assert aapl_quote.earnings_datetime is not None
    assert (
        aapl_quote.earnings_datetime.strftime("%Y-%m-%d %H:%M:%S")
        == "2023-11-02 17:00:00"
    )
