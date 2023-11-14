"""The state of the quote table."""

import logging
from re import S
from threading import Lock, Thread
from time import monotonic, sleep
from typing import Any, Callable, Optional

from yfinance import YFinance, YQuote

from ._enums import SortDirection, get_enum_member
from ._quote_column_definitions import ALL_QUOTE_COLUMNS
from ._quote_table_data import QuoteCell, QuoteColumn, QuoteRow


class QuoteTableState:
    """The state of the quote table."""

    _TICKER_COLUMN_KEY: str = "ticker"

    # Default values
    _DEFAULT_COLUMN_KEYS: list[str] = [
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
    _DEFAULT_QUERY_FREQUENCY: int = 60

    # Config file keys
    _COLUMNS: str = "columns"
    _SORT_COLUMN: str = "sort_column"
    _SORT_DIRECTION: str = "sort_direction"
    _QUOTES: str = "quotes"
    _QUERY_FREQUENCY: str = "query_frequency"

    def __init__(self, yfin: YFinance) -> None:
        self._yfin: YFinance = yfin

        self._quotes_symbols: list[str] = QuoteTableState._DEFAULT_QUOTES[:]

        self._sort_column_key: str = QuoteTableState._TICKER_COLUMN_KEY
        self._sort_direction: SortDirection = QuoteTableState._DEFAULT_SORT_DIRECTION
        self._query_frequency: int = QuoteTableState._DEFAULT_QUERY_FREQUENCY

        # Ticker is *always* the first column
        columns_keys: list[str] = [
            QuoteTableState._TICKER_COLUMN_KEY
        ] + QuoteTableState._DEFAULT_COLUMN_KEYS[:]
        self._columns: list[QuoteColumn] = [
            ALL_QUOTE_COLUMNS[column] for column in columns_keys
        ]

        self._sort_key_func: Callable[[YQuote], Any] = ALL_QUOTE_COLUMNS[
            self._sort_column_key
        ].sort_key_func

        self._cursor_symbol: str = self._quotes_symbols[0]

        self._query_thread_running: bool = False
        self._query_thread: Thread = Thread(target=self._retrieve_quotes)
        self._last_query_time = monotonic()
        self._version: int = 0

        self._quotes: list[YQuote] = []
        self._quotes_lock = Lock()

    def __del__(self) -> None:
        # Make sure the query thread is stopped
        if self.query_thread_running:
            self.query_thread_running = False

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
        with self._quotes_lock:
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
        with self._quotes_lock:
            self._sort_quotes()
        self._version += 1

    @property
    def query_frequency(self) -> int:
        """The frequency (in seconds) to query for quotes."""

        return self._query_frequency

    @query_frequency.setter
    def query_frequency(self, value: int) -> None:
        self._query_frequency = value
        # Don't change the version. This is a setting for the backend, not the UI.

    @property
    def current_row(self) -> int:
        """The current row of the cursor."""

        with self._quotes_lock:
            # Return the index of the quote (from _quotes) whose ticker symbol matches
            # the cursor symbol
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

        with self._quotes_lock:
            self._cursor_symbol = self._quotes[value].symbol
        # Setting the current row does not change the version. It's just mirroring the
        # cursor position from the UI.

    @property
    def quotes_columns(self) -> list[QuoteColumn]:
        """The columns of the quote table."""

        return self._columns

    @property
    def quotes_rows(self) -> list[QuoteRow]:
        """
        The quotes to display in the quote table. Each quote is comprised of the
        elements required for each column.

        Returns:
            list[QuoteRow]: The quotes to display in the quote table.
        """

        with self._quotes_lock:
            quote_info: list[QuoteRow] = [
                QuoteRow(
                    q.symbol,
                    # TODO Could it be possible to have this array be fixed and
                    # saved whenever we change the columns?
                    [
                        QuoteCell(
                            ALL_QUOTE_COLUMNS[column].format_func(q),
                            ALL_QUOTE_COLUMNS[column].sign_indicator_func(q),
                            ALL_QUOTE_COLUMNS[column].justification,
                        )
                        for column in self.column_keys
                    ],
                )
                for q in self._quotes
            ]

            return quote_info

    @property
    def column_keys(self) -> list[str]:
        """The keys of the columns of the quote table."""

        return [c.key for c in self._columns]

    def append_column(self, column_key: str) -> None:
        """
        Append a new column to the quote table.

        Attempting to add a column that is already present or that doesn't exist will
        have no effect.

        The column is added at the end of the list of existing columns.

        Args:
            column_key (str): The identifier of the column to add.
                The identifier of the column is expected to match the ones found in the
                ALL_QUOTE_COLUMNS definition.
        """

        if not self._can_add_column(column_key):
            return

        self._columns.append(ALL_QUOTE_COLUMNS[column_key])
        self._version += 1

    def insert_column(self, index: int, column_key: str) -> None:
        """
        Insert a new column to the quote table, at the given index.

        Attempting to insert a column that is already present or that doesn't exist will
        have no effect.

        Args:
            index (int): The index at which to insert the column.
                It's important to note that the index is 1-based, as index 0 is reserved
                for the ticker column. Attempting to insert at index 0 or at a negative
                index smaller than -(len(self._columns)-1) will have no effect.
            column_key (str): The identifier of the column to insert.
                The identifier of the column is expected to match the ones found in the
                ALL_QUOTE_COLUMNS definition.
        """

        if not self._can_add_column(column_key):
            return

        # Do not insert at index 0 or below
        if (index == 0) or (index < -(len(self._columns) - 1)):
            return

        self._columns.insert(index, ALL_QUOTE_COLUMNS[column_key])
        self._version += 1

    def remove_column(self, column_key: str) -> None:
        """
        Remove a column from the quote table.

        Attempting to remove a column that is not present in the table will have no
        effect.

        Args:
            column_key (str): The identifier of the column to remove.
                The identifier of the column is expected to match the ones found in the
                ALL_QUOTE_COLUMNS definition.
        """

        try:
            if column_key == QuoteTableState._TICKER_COLUMN_KEY:
                raise ValueError("Cannot remove ticker column")
            self._columns.remove(ALL_QUOTE_COLUMNS[column_key])
            if self._sort_column_key == column_key:
                self._sort_column_key = QuoteTableState._TICKER_COLUMN_KEY

            self._version += 1
        except KeyError as exc:
            raise ValueError(
                f"Column key {column_key} does not exist in the quote table",
            ) from exc

    def _can_add_column(self, column_key: str) -> bool:
        """
        Check if the column can be added to the quote table

        Args:
            column_key (str): The identifier of the column to add.

        Returns:
            bool: Whether the column can be added to the quote table
        """

        if column_key not in ALL_QUOTE_COLUMNS:
            logging.warning(
                "Invalid column key '%s' specified in config file",
                column_key,
            )
            return False

        if column_key in self.column_keys:
            logging.warning(
                "Duplicate column key '%s' specified in config file",
                column_key,
            )
            return False

        return True

    def _retrieve_quotes(self) -> None:
        """Query for the quotes and update the change version."""

        now: float = monotonic()
        while self._query_thread_running:
            self._retrieve_quotes_internal(now)

            while now - self._last_query_time < self._query_frequency:
                if not self._query_thread_running:
                    return
                sleep(1)
                now = monotonic()

    def _retrieve_quotes_internal(self, monotonic_clock: float) -> None:
        """
        Query for the quotes from the YFinance interface and update the change version.

        Note: Not for external use. Created for testing purposes only.

        Args:
            monotonic_clock (float): A monotonic clock time.
        """

        with self._quotes_lock:
            self._quotes = self._yfin.retrieve_quotes(self._quotes_symbols)
            self._sort_quotes()
        self._last_query_time = monotonic_clock
        self._version += 1

    def _sort_quotes(self):
        """Sort the quotes, according to the sort column and direction."""

        if not self._quotes_lock.locked():
            raise RuntimeError(
                "The _quotes_lock must be acquired before calling this function"
            )

        self._quotes.sort(
            key=self._sort_key_func,
            reverse=(self._sort_direction == SortDirection.DESCENDING),
        )

    ##############################################################################
    ## Configuration load and save
    ##############################################################################
    def load_config(self, config: dict[str, Any]) -> None:
        """
        Load the configuration for the quote table.

        Args:
            config (dict[str, Any]): The configuration dictionary to load.
        """

        columns_keys: list[str] = (
            config[QuoteTableState._COLUMNS][:]
            if QuoteTableState._COLUMNS in config
            else []
        )
        sort_key: Optional[str] = (
            config[QuoteTableState._SORT_COLUMN]
            if QuoteTableState._SORT_COLUMN in config
            else None
        )
        sort_direction: Optional[str] = (
            config[QuoteTableState._SORT_DIRECTION]
            if QuoteTableState._SORT_DIRECTION in config
            else None
        )
        quotes_symbols: list[str] = (
            config[QuoteTableState._QUOTES][:]
            if QuoteTableState._QUOTES in config
            else []
        )
        query_frequency: Optional[int] = (
            config[QuoteTableState._QUERY_FREQUENCY]
            if QuoteTableState._QUERY_FREQUENCY in config
            else None
        )

        # TODO: Check if values are actually changed, and if so, bump the version

        # Validate the column keys
        if len(columns_keys) == 0:
            logging.warning("No columns specified in config file")
            columns_keys = [
                QuoteTableState._TICKER_COLUMN_KEY
            ] + QuoteTableState._DEFAULT_COLUMN_KEYS[:]
        else:
            # Ticker is *always* the first column
            columns_keys.insert(0, QuoteTableState._TICKER_COLUMN_KEY)

        self._columns.clear()
        # Make sure the column keys are supported and there are no duplicates
        for column_key in columns_keys:
            self.append_column(column_key)

        # Validate the sort column key
        if sort_key is None or sort_key not in self.column_keys:
            self._sort_column_key = self._columns[0].key
        else:
            self._sort_column_key = sort_key

        # Validate the sort direction
        try:
            self._sort_direction = get_enum_member(SortDirection, sort_direction)
        except ValueError:
            self._sort_direction = QuoteTableState._DEFAULT_SORT_DIRECTION

        # Validate the quotes symbols
        if len(quotes_symbols) == 0:
            logging.warning("No quotes specified in config file")
            self._quotes_symbols = QuoteTableState._DEFAULT_QUOTES[:]
        else:
            self._quotes_symbols.clear()
            for quote_symbol in quotes_symbols:
                if quote_symbol == "":
                    logging.warning("Empty quote symbol specified in config file")
                elif quote_symbol in self._quotes_symbols:
                    logging.warning(
                        "Duplicate quote symbol %s specified in config file",
                        quote_symbol,
                    )
                else:
                    self._quotes_symbols.append(quote_symbol.upper())

        # Validate the query frequency
        if query_frequency is None or query_frequency <= 1:
            logging.warning("Invalid query frequency specified in config file")
            self._query_frequency = QuoteTableState._DEFAULT_QUERY_FREQUENCY
        else:
            self._query_frequency = query_frequency

        # Set other properties based on the configuration
        self._sort_key_func = ALL_QUOTE_COLUMNS[self._sort_column_key].sort_key_func

    def save_config(self) -> dict[str, Any]:
        """
        Save the configuration for the quote table.

        Returns:
            (dict[str, Any]): A dictionary containing the configuration.
        """

        return {
            QuoteTableState._COLUMNS: self.column_keys[1:],
            QuoteTableState._SORT_COLUMN: self._sort_column_key,
            QuoteTableState._SORT_DIRECTION: self._sort_direction.value,
            QuoteTableState._QUOTES: self._quotes_symbols[:],
            QuoteTableState._QUERY_FREQUENCY: self._query_frequency,
        }
