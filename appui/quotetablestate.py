from enum import Enum

from yfinance import YFinance, YQuote

from ._formatting import as_float, as_percent, as_shrunk_int


class Justify(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class Column:
    def __init__(
        self, name: str, width: int, key: str, justify: Justify = Justify.RIGHT
    ) -> None:
        self.name = name
        self.width = width
        self.key = key
        self.justification = justify


class QuoteTableState:
    def __init__(self, yfin: YFinance) -> None:
        # TODO Temp...
        # We will need to have a complete list of all the possible properties that can be "columnized", and pick from that.
        # We will also need a way to change the column order, and to add/remove columns.
        self._columns: list[Column] = [
            Column("Ticker", 8, "tick", Justify.LEFT),
            Column("Last", 10, "last"),
            Column("Change", 8, "chg"),
            Column("Change%", 8, "chg_p"),
            Column("Open", 10, "open"),
            Column("Low", 10, "low"),
            Column("High", 10, "high"),
            Column("52w Low", 10, "52_l"),
            Column("52w High", 10, "52_h"),
            Column("Volume", 8, "vol"),
            Column("Avg Vol", 8, "a_vol"),
            Column("P/E", 6, "pe"),
            Column("Dividend", 6, "div"),
            Column("Mkt Cap", 8, "mcap"),
        ]
        self._yfin: YFinance = yfin

        # TODO TEMP TEMP TEMP
        # This is just to get something to show quickly.
        self._quotes: list[YQuote] = self._yfin.get_quotes(
            ["TSLA", "GOOG", "MSFT", "F", "NUMI.TO", "AQB"]
        )

        # TODO: add a dirty flag and an indicator of what has been dirtied

    @property
    def columns(self) -> list[Column]:
        """The columns of the quote table."""
        return self._columns

    def get_quotes(self) -> list[list[str]]:
        # TODO TEMP TEMP TEMP
        # This is bad. Just hacking this quickly to have something that displays
        quotes: list[list[str]] = []
        idx: int = 0
        for q in self._quotes:
            hint = q.price_hint
            quotes.append(
                [
                    q.symbol,
                    as_float(q.regular_market_price, hint),
                    as_float(q.regular_market_change, hint),
                    as_percent(q.regular_market_change_percent),
                    as_float(q.regular_market_open, hint),
                    as_float(q.regular_market_day_low, hint),
                    as_float(q.regular_market_day_high, hint),
                    as_float(q.fifty_two_week_low, hint),
                    as_float(q.fifty_two_week_high, hint),
                    as_shrunk_int(q.regular_market_volume),
                    as_shrunk_int(q.average_daily_volume_3_month),
                    as_float(q.trailing_pe),
                    as_float(q.dividend_yield, hint),
                    as_shrunk_int(q.market_cap),
                ]
            )
            idx += 1
        return quotes
