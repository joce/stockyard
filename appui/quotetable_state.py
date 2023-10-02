from yfinance import YFinance, YQuote

from ._column import Column
from ._column_definitions import ALL_COLUMNS


class QuoteTableState:
    def __init__(self, yfin: YFinance) -> None:
        # TODO Temp...
        # We need to be able to load the columns from a config file
        self._columns_keys: list[str] = [
            "ticker",
            "last",
            "change_percent",
            "volume",
            "market_cap",
        ]

        self._columns: list[Column] = [
            ALL_COLUMNS[column] for column in self._columns_keys
        ]

        self._yfin: YFinance = yfin

        # TODO TEMP TEMP TEMP
        # This is just to get something to show quickly.
        self._quotes: list[YQuote] = self._yfin.get_quotes(
            ["TSLA", "GOOG", "MSFT", "F", "NUMI.TO", "AQB"]
        )

        # TODO Another quick and dirty hack. This information will be retrieved from the config file as well.
        self._sort_column: Column = self._columns[2]
        self._sort_ascending: bool = False

        # TODO: add a dirty flag and an indicator of what has been dirtied

    @property
    def columns(self) -> list[Column]:
        """The columns of the quote table."""
        return self._columns

    def get_quotes(self) -> list[list[str]]:
        """
        Get the quotes to display in the quote table. Each quote is comprised of the elements required for each column.

        Returns:
            list[list[str]]: The quotes strings
        """

        # TODO: sort only when the sort order change, or when we get a new batch of quotes
        self._quotes.sort(
            key=self._sort_column.sort_key, reverse=not self._sort_ascending
        )

        quote_info: list[list[str]] = [
            [ALL_COLUMNS[column].format_func(q) for column in self._columns_keys]
            for q in self._quotes
        ]

        return quote_info
