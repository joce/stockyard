"""The state of the quote table."""

import logging
from threading import Thread
from time import monotonic, sleep
from typing import Any, Callable, Optional

from yfinance import YFinance, YQuote

from ._enums import SortDirection, get_enum_member
from ._quote_column_definitions import ALL_QUOTE_COLUMNS
from ._quote_table_data import QuoteCell, QuoteColumn, QuoteRow


class QuoteTableState:
    """The state of the quote table."""

    # Default values
    _DEFAULT_COLUMN_KEYS: list[str] = [
        "ticker",
        "last",
        "change_percent",
        "volume",
        "market_cap",
    ]
    _DEFAULT_QUOTES: list[str] = [
        "AAPL",
        "F",
        "VT",
        "^DJI",
        "ARKK",
        "GC=F",
        "EURUSD=X",
        "BTC-USD",
    ]
    _DEFAULT_SORT_DIRECTION: SortDirection = SortDirection.ASCENDING
    _DEFAULT_QUERY_FREQUENCY: int = 10

    # Config file keys
    _COLUMNS: str = "columns"
    _SORT_COLUMN: str = "sort_column"
    _SORT_DIRECTION: str = "sort_direction"
    _QUOTES: str = "quotes"
    _QUERY_FREQUENCY: str = "query_frequency"

    def __init__(self, yfin: YFinance) -> None:
        self._yfin: YFinance = yfin

        self._columns_keys: list[str] = QuoteTableState._DEFAULT_COLUMN_KEYS[:]
        self._quotes_symbols: list[str] = QuoteTableState._DEFAULT_QUOTES[:]

        # TODO Another quick and dirty hack. This information will be retrieved from the config file as well.
        self._sort_column_key: str = self._columns_keys[2]
        self._sort_direction: SortDirection = QuoteTableState._DEFAULT_SORT_DIRECTION
        self._query_frequency: int = QuoteTableState._DEFAULT_QUERY_FREQUENCY

        self._columns: list[QuoteColumn] = [
            ALL_QUOTE_COLUMNS[column] for column in self._columns_keys
        ]

        self._sort_key_func: Callable[[YQuote], Any] = ALL_QUOTE_COLUMNS[
            self._sort_column_key
        ].sort_key_func

        self._cursor_symbol: str = self._quotes_symbols[0]

        self._query_thread_running: bool = False
        self._query_thread: Thread = Thread(target=self._query_quotes)
        self._last_query_time = monotonic()
        self._version: int = 0

        self._quotes: list[YQuote] = []

    def __del__(self) -> None:
        # Make sure the query thread is stopped
        if self.query_thread_running:
            self.query_thread_running = False

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
        """Whether the quote query thread is currently running."""

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

    @property
    def sort_column_key(self) -> str:
        """The key of the column to sort by."""

        return self._sort_column_key

    @sort_column_key.setter
    def sort_column_key(self, value: str) -> None:
        if value == self._sort_column_key:
            return
        self._sort_column_key = value
        self._sort_key_func = ALL_QUOTE_COLUMNS[self._sort_column_key].sort_key_func
        self._sort_quotes()
        self._version += 1

    @property
    def sort_direction(self) -> SortDirection:
        """The direction of the sort."""

        return self._sort_direction

    @sort_direction.setter
    def sort_direction(self, value: SortDirection) -> None:
        if value == self._sort_direction:
            return
        self._sort_direction = value
        self._sort_quotes()
        self._version += 1

    @property
    def current_row(self) -> int:
        """The current row of the cursor."""

        # Return the index of the quote (from _quotes) whose ticker symbol matches the cursor symbol
        return next(
            (
                i
                for i, quote in enumerate(self._quotes)
                if quote.symbol == self._cursor_symbol
            ),
            -1,
        )

    @current_row.setter
    def current_row(self, value: int) -> None:
        if value >= len(self._quotes_symbols):
            raise ValueError("Invalid row index")

        if (
            value < len(self._quotes_symbols)
            and self._quotes_symbols[value] == self._cursor_symbol
        ):
            return
        self._cursor_symbol = self._quotes[value].symbol
        # Setting the current row does not change the version. It's just mirroring the cursor position from the UI.

    def get_quotes(self) -> list[QuoteRow]:
        """
        Get the quotes to display in the quote table. Each quote is comprised of the elements required for each column.

        Returns:
            list[QuoteRow]: The quotes to display in the quote table.
        """

        quote_info: list[QuoteRow] = [
            QuoteRow(
                q.symbol,
                [
                    QuoteCell(
                        ALL_QUOTE_COLUMNS[column].format_func(q),
                        ALL_QUOTE_COLUMNS[column].sign_indicator_func(q),
                        ALL_QUOTE_COLUMNS[column].justification,
                    )
                    for column in self._columns_keys
                ],
            )
            for q in self._quotes
        ]

        return quote_info

    def _query_quotes(self) -> None:
        """Query for the quotes and update the change version."""

        now: float = monotonic()
        while self._query_thread_running:
            self._quotes = self._yfin.get_quotes(self._quotes_symbols)
            self._sort_quotes()
            self._last_query_time = now
            self._version += 1

            while now - self._last_query_time < self._query_frequency:
                if not self._query_thread_running:
                    return
                sleep(1)
                now = monotonic()

    def _sort_quotes(self):
        """Sort the quotes, according to the sort column and direction."""

        self._quotes.sort(
            key=self._sort_key_func,
            reverse=(self._sort_direction == SortDirection.DESCENDING),
        )

    def load_config(self, config: dict[str, Any]) -> None:
        """
        Load the configuration for the quote table.

        Args:
            config (dict[str, Any]): The configuration dictionary to load.
        """

        columns_keys: Optional[list[str]] = (
            config[QuoteTableState._COLUMNS]
            if QuoteTableState._COLUMNS in config
            else None
        )
        sort_column_key: Optional[str] = (
            config[QuoteTableState._SORT_COLUMN]
            if QuoteTableState._SORT_COLUMN in config
            else None
        )
        sort_direction: Optional[str] = (
            config[QuoteTableState._SORT_DIRECTION]
            if QuoteTableState._SORT_DIRECTION in config
            else None
        )
        quotes_symbols: Optional[list[str]] = (
            config[QuoteTableState._QUOTES]
            if QuoteTableState._QUOTES in config
            else None
        )
        query_frequency: Optional[int] = (
            config[QuoteTableState._QUERY_FREQUENCY]
            if QuoteTableState._QUERY_FREQUENCY in config
            else None
        )

        # TODO: Check if values are actually changed, and if so, bump the version

        # Validate the column keys
        if columns_keys is None or len(columns_keys) == 0:
            logging.warning("No columns specified in config file")
            self._columns_keys = QuoteTableState._DEFAULT_COLUMN_KEYS[:]
        else:
            self._columns_keys = columns_keys[:]

        # Make sure the column keys are supported
        for i in reversed(range(len(self._columns_keys))):
            if self._columns_keys[i] not in ALL_QUOTE_COLUMNS:
                logging.warning(
                    "Invalid column key '%s' specified in config file",
                    self._columns_keys[i],
                )
                self._columns_keys.pop(i)

        # Validate the sort column key
        if sort_column_key is None or sort_column_key not in self._columns_keys:
            self._sort_column_key = self._columns_keys[0]
        else:
            self._sort_column_key = sort_column_key

        # Validate the sort direction
        try:
            self._sort_direction = get_enum_member(SortDirection, sort_direction)
        except ValueError:
            self._sort_direction = QuoteTableState._DEFAULT_SORT_DIRECTION

        # Validate the quotes symbols
        if quotes_symbols is None or len(quotes_symbols) == 0:
            logging.warning("No quotes specified in config file")
            self._quotes_symbols = QuoteTableState._DEFAULT_QUOTES[:]
        else:
            self._quotes_symbols.clear()
            for i in reversed(range(len(quotes_symbols))):
                if quotes_symbols[i] == "":
                    logging.warning("Empty quote symbol specified in config file")
                    quotes_symbols.pop(i)
                else:
                    self._quotes_symbols.insert(0, quotes_symbols[i].upper())

        # Validate the query frequency
        if query_frequency is None or query_frequency <= 1:
            logging.warning("Invalid query frequency specified in config file")
            self._query_frequency = QuoteTableState._DEFAULT_QUERY_FREQUENCY
        else:
            self._query_frequency = query_frequency

        # Set other properties based on the configuration
        self._columns = [ALL_QUOTE_COLUMNS[column] for column in self._columns_keys]
        self._sort_key_func = ALL_QUOTE_COLUMNS[self._sort_column_key].sort_key_func

    def save_config(self, config: dict[str, Any]) -> None:
        """
        Save the configuration for the quote table.

        Args:
            config (dict[str, Any]): A dictionary to save the configuration.

        Raises:
            ValueError: If the configuration dictionary is not empty
        """

        if len(config) > 0:
            raise ValueError("Configuration dictionary must be empty")

        config[QuoteTableState._COLUMNS] = self._columns_keys[:]
        config[QuoteTableState._SORT_COLUMN] = self._sort_column_key
        config[QuoteTableState._SORT_DIRECTION] = self._sort_direction.value
        config[QuoteTableState._QUOTES] = self._quotes_symbols[:]
        config[QuoteTableState._QUERY_FREQUENCY] = self._query_frequency
