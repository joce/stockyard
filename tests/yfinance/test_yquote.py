# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from yfinance import YQuote

from ..fake_yfinance import FakeYFinance


def test_yquote_dates():
    """Making sure the date formats are consistent for different versions of Python."""

    aapl_quote: YQuote
    gold_fut: YQuote
    aapl_quote, gold_fut = FakeYFinance().retrieve_quotes(["AAPL", "GC=F"])
    assert (
        gold_fut.expire_date is not None
        and gold_fut.expire_date.strftime("%Y-%m-%d %H:%M:%S") == "2023-12-27 00:00:00"
    )
    assert (
        aapl_quote.earnings_datetime is not None
        and aapl_quote.earnings_datetime.strftime("%Y-%m-%d %H:%M:%S")
        == "2023-11-02 17:00:00"
    )
