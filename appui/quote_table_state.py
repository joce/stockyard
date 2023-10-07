from threading import Thread
from time import monotonic, sleep

from yfinance import YFinance, YQuote

from ._quote_column import QuoteColumn
from ._quote_column_definitions import ALL_QUOTE_COLUMNS
from ._quote_row import QuoteRow


class QuoteTableState:
    def __init__(self, yfin: YFinance) -> None:
        self._yfin: YFinance = yfin

        # TODO We need to be able to load the symbols from a config file
        self._quotes_symbols: list[str] = [
            "TSLA",
            "GOOG",
            "MSFT",
            "F",
            "NUMI.TO",
            "AQB",
        ]

        # TODO We need to be able to load the columns from a config file
        self._columns_keys: list[str] = [
            "ticker",
            "last",
            "change_percent",
            "volume",
            "market_cap",
        ]

        self._columns: list[QuoteColumn] = [
            ALL_QUOTE_COLUMNS[column] for column in self._columns_keys
        ]

        # TODO Another quick and dirty hack. This information will be retrieved from the config file as well.
        # TODO We should store the column key name rather than the column object
        self._sort_column: QuoteColumn = self._columns[0]
        self._sort_ascending: bool = True
        self._query_frequency: int = 10

        self._query_thread_running: bool = False
        self._query_thread: Thread = Thread(target=self._query_quotes)
        self._last_query_time = monotonic()
        self._version: int = 0

        self._quotes: list[YQuote] = []

    @property
    def columns(self) -> list[QuoteColumn]:
        """The columns of the quote table."""
        return self._columns

    @property
    def version(self) -> int:
        """The version of the quote data."""
        return self._version

    @property
    def query_thread_running(self) -> bool:
        """
        Whether the quote query thread is currently running.
        """
        return self._query_thread_running

    @query_thread_running.setter
    def query_thread_running(self, value: bool) -> None:
        if value == self._query_thread_running:
            return

        self._query_thread_running = value
        if self._query_thread_running:
            self._last_query_time = monotonic()
            self._query_thread.start()
        else:
            self._query_thread.join()

    def get_quotes(self) -> list[QuoteRow]:
        """
        Get the quotes to display in the quote table. Each quote is comprised of the elements required for each column.

        Returns:
            list[list[str]]: The quotes strings
        """

        # TODO: sort only when the sort order change, or when we get a new batch of quotes
        self._quotes.sort(
            key=self._sort_column.sort_key, reverse=not self._sort_ascending
        )

        quote_info: list[QuoteRow] = [
            QuoteRow(
                q.symbol,
                [
                    (
                        ALL_QUOTE_COLUMNS[column].format_func(q),
                        ALL_QUOTE_COLUMNS[column].justification,
                    )
                    for column in self._columns_keys
                ],
            )
            for q in self._quotes
        ]

        return quote_info

    def _query_quotes(self) -> None:
        """
        Query for the quotes and update the change version.
        """
        now: float = monotonic()
        while self._query_thread_running:
            self._quotes = self._yfin.get_quotes(self._quotes_symbols)
            self._last_query_time = now
            self._version += 1

            while now - self._last_query_time < self._query_frequency:
                if not self._query_thread_running:
                    return
                sleep(1)
                now = monotonic()
