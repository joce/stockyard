# """The state of the quote table."""

# from __future__ import annotations

# import logging
# from threading import Lock, Thread
# from time import monotonic, sleep
# from typing import TYPE_CHECKING, Any, Callable, Final

# from ._enums import SortDirection, get_enum_member
# from ._quote_column_definitions import ALL_QUOTE_COLUMNS
# from ._quote_table_data import QuoteCell, QuoteColumn, QuoteRow

# if TYPE_CHECKING:
#     from yfinance import YFinance, YQuote


# class QuoteTableState:
#     """The state of the quote table."""

#     class QuoteLockError(RuntimeError):
#         """Quote lock exception."""

#         def __init__(self, call_site: str) -> None:
#             """
#             Initialize the exception.

#             Args:
#                 call_site: The site where the exception was raised.
#             """

#             super().__init__(
#                 f"The `_quotes_lock` must be acquired before calling `{call_site}`."
#             )

#     class InvalidRowIndexError(ValueError):
#         """Invalid row index exception."""

#         def __init__(self, index: int) -> None:
#             """
#             Initialize the exception.

#             Args:
#                 index: The (invalid) row index.
#             """

#             super().__init__(f"Invalid row index `{index}`.")


#     def __init__(self, yfin: YFinance) -> None:
#         """
#         Initialize state management for the quote table.

#         Establishes thread-safe market data fetching, sets up default display
#         preferences, and initializes table sorting behavior.

#         Args:
#             yfin: Market data provider instance used for quote retrieval
#         """


#         # Transient state
#         self._cursor_symbol: str = ""
#         self._version: int = 0
#         self._quotes: list[YQuote] = []
#         self._sort_key_func: Callable[[YQuote], Any] = ALL_QUOTE_COLUMNS[
#             self._sort_column_key
#         ].sort_key_func

#         # Query thread
#         self._query_thread_running: bool = False
#         self._query_thread: Thread = Thread(target=self._retrieve_quotes)
#         self._last_query_time: float = monotonic()

#         # Other
#         self._yfin: YFinance = yfin
#         self._quotes_lock: Lock = Lock()
#         self._logger = logging.getLogger(__name__)


#     @property
#     def query_thread_running(self) -> bool:
#         """Whether the quote query thread is currently running."""

#         return self._query_thread_running

#     @query_thread_running.setter
#     def query_thread_running(self, value: bool) -> None:
#         if value == self._query_thread_running:
#             return

#         self._query_thread_running = value
#         if self._query_thread_running:
#             self._last_query_time = monotonic()
#             self._query_thread.start()
#         else:
#             self._query_thread.join()


#     @property
#     def query_frequency(self) -> int:
#         """The frequency (in seconds) to query for quotes."""

#         return self._query_frequency

#     @query_frequency.setter
#     def query_frequency(self, value: int) -> None:
#         self._query_frequency = value
#         # Don't change the version. This is a setting for the backend, not the UI.


#     @property
#     def cursor_row(self) -> int:
#         """The current row of the cursor."""

#         with self._quotes_lock:
#             return self._get_cursor_row_no_lock()

#     @cursor_row.setter
#     def cursor_row(self, value: int) -> None:
#         with self._quotes_lock:
#             # Setting the current row does not change the version. It's just used to
#             # mirror the cursor position from the UI.
#             self._set_cursor_row_no_lock(value)


#     @property
#     def quotes_rows(self) -> list[QuoteRow]:
#         """
#         The quotes to display in the quote table.

#         Note:
#             Each quote is comprised of the elements required for each column.

#         Returns:
#             list[QuoteRow]: The quotes to display in the quote table.
#         """

#         with self._quotes_lock:
#             quote_info: list[QuoteRow] = [
#                 QuoteRow(
#                     q.symbol,
#                     # TODO Could it be possible to have this array be fixed and
#                     # saved whenever we change the columns?
#                     [
#                         QuoteCell(
#                             ALL_QUOTE_COLUMNS[column.key].format_func(q),
#                             ALL_QUOTE_COLUMNS[column.key].sign_indicator_func(q),
#                             ALL_QUOTE_COLUMNS[column.key].justification,
#                         )
#                         for column in self._columns
#                     ],
#                 )
#                 for q in self._quotes
#             ]

#             return quote_info


#     @property
#     def quotes_symbols(self) -> tuple[str, ...]:
#         """The symbols of the quotes in the quote table."""

#         return tuple(self._quotes_symbols)


#     def insert_column(self, index: int, column_key: str) -> None:
#         """
#         Insert a new column to the quote table, at the given index.

#         Attempting to insert a column that is already present or that doesn't exist will
#         have no effect.

#         Args:
#             index (int): The index at which to insert the column.
#                 It's important to note that the index is 1-based, as index 0 is reserved
#                 for the ticker column. Attempting to insert at index 0 or at a negative
#                 index smaller than -(len(self._columns)-1) will have no effect.
#             column_key (str): The identifier of the column to insert.
#                 The identifier of the column is expected to match the ones found in the
#                 ALL_QUOTE_COLUMNS definition.
#         """

#         if not self._can_add_column(column_key):
#             return

#         # Do not insert at index 0 or below
#         if (index == 0) or (index < -(len(self._columns) - 1)):
#             return

#         self._columns.insert(index, ALL_QUOTE_COLUMNS[column_key])
#         self._version += 1

#     def remove_column(self, column_key: str) -> None:
#         """
#         Remove a column from the quote table.

#         Attempting to remove a column that is not present in the table will have no
#         effect.

#         Args:
#             column_key (str): The identifier of the column to remove.
#                 The identifier of the column is expected to match the ones found in the
#                 ALL_QUOTE_COLUMNS definition.

#         Raises:
#             ValueError: If the column key does not exist in the table.
#         """

#         try:
#             if column_key == QuoteTableState._TICKER_COLUMN_KEY:
#                 error_msg = "Cannot remove ticker column"
#                 raise ValueError(error_msg)
#             self._columns.remove(ALL_QUOTE_COLUMNS[column_key])
#             if self._sort_column_key == column_key:
#                 self._sort_column_key = QuoteTableState._TICKER_COLUMN_KEY

#             self._version += 1
#         except KeyError as exc:
#             error_msg = f"Column key {column_key} does not exist in the quote table"
#             raise ValueError(error_msg) from exc

#     def _can_add_column(self, column_key: str) -> bool:
#         """
#         Check if the column can be added to the quote table.

#         Args:
#             column_key (str): The identifier of the column to add.

#         Returns:
#             bool: Whether the column can be added to the quote table.
#         """

#         if column_key not in ALL_QUOTE_COLUMNS:
#             self._logger.warning(
#                 "Invalid column key '%s' specified in config file",
#                 column_key,
#             )
#             return False

#         if column_key in self.column_keys:
#             self._logger.warning(
#                 "Duplicate column key '%s' specified in config file",
#                 column_key,
#             )
#             return False

#         return True

#     def remove_row(self, index: int) -> None:
#         """
#         Remove a row from the quote table.

#         Args:
#             index (int): The index of the row to remove.

#         Raises:
#             QuoteTableState.InvalidRowIndexError: If the row index is invalid.
#         """

#         if index < 0 or index >= len(self._quotes):
#             raise QuoteTableState.InvalidRowIndexError(index)

#         with self._quotes_lock:
#             # Can't use cursor_row here because it's also using the lock.

#             # Compute a new current row if the removed row is the current row
#             if index == self._get_cursor_row_no_lock():
#                 if len(self._quotes) == 1:
#                     self._set_cursor_row_no_lock(-1)
#                 elif index == len(self._quotes) - 1:
#                     self._set_cursor_row_no_lock(index - 1)
#                 else:
#                     self._set_cursor_row_no_lock(index + 1)

#             # remove the symbol from both the list of quotes to fetch and the current
#             # list of quotes
#             symbol = self._quotes[index].symbol
#             self._quotes_symbols.remove(symbol)
#             self._quotes.pop(index)
#             self._version += 1

#     def _retrieve_quotes(self) -> None:
#         """Query for the quotes and update the change version."""

#         now: float = monotonic()
#         while self._query_thread_running:
#             self._retrieve_quotes_internal(now)

#             while now - self._last_query_time < self._query_frequency:
#                 if not self._query_thread_running:
#                     return
#                 sleep(1)
#                 now = monotonic()

#     def _retrieve_quotes_internal(self, monotonic_clock: float) -> None:
#         """
#         Query for the quotes from the YFinance interface and update the change version.

#         Note:
#             Not for external use. Created for testing purposes only.

#         Args:
#             monotonic_clock (float): A monotonic clock time.
#         """

#         with self._quotes_lock:
#             self._quotes = self._yfin.retrieve_quotes(self._quotes_symbols)
#             self._sort_quotes()
#         self._last_query_time = monotonic_clock
#         self._version += 1

#     def _sort_quotes(self) -> None:
#         """
#         Sort the quotes, according to the sort column and direction.

#         Raises:
#             QuoteTableState.QuoteLockError: If the _quotes_lock is not acquired.
#         """

#         if not self._quotes_lock.locked():
#             raise QuoteTableState.QuoteLockError(__name__)

#         self._quotes.sort(
#             key=self._sort_key_func,
#             reverse=(self._sort_direction == SortDirection.DESCENDING),
#         )

#     def _get_cursor_row_no_lock(self) -> int:
#         """
#         Get the current row of the cursor.

#         This method expects the _quotes_lock to have been acquired beforehand.

#         Raises:
#             QuoteTableState.QuoteLockError: If the _quotes_lock has not been acquired.

#         Returns:
#             The index of the quote (from _quotes) whose ticker symbol matches the
#             cursor symbol
#         """

#         if not self._quotes_lock.locked():
#             raise QuoteTableState.QuoteLockError(__name__)

#         # Return the index of the quote (from _quotes) whose ticker symbol matches the
#         # cursor symbol
#         return next(
#             (
#                 i
#                 for i, quote in enumerate(self._quotes)
#                 if quote.symbol == self._cursor_symbol
#             ),
#             -1,
#         )

#     def _set_cursor_row_no_lock(self, value: int) -> None:
#         """
#         Set the current row of the cursor.

#         This method expects the _quotes_lock to have been acquired beforehand.

#         Args:
#             value: The index of the quote (from _quotes) whose ticker symbol matches the
#             cursor symbol

#         Raises:
#             QuoteTableState.QuoteLockError: If the _quotes_lock has not been acquired.
#             QuoteTableState.InvalidRowIndexError: If value is out of range.
#         """

#         if not self._quotes_lock.locked():
#             raise QuoteTableState.QuoteLockError(__name__)

#         if value == 0 and len(self._quotes_symbols) == 0:
#             self._cursor_symbol = ""
#             return

#         if value >= len(self._quotes_symbols):
#             raise QuoteTableState.InvalidRowIndexError(value)

#         if value < 0:
#             self._cursor_symbol = ""
#             return

#         if self._quotes[value].symbol == self._cursor_symbol:
#             return

#         self._cursor_symbol = self._quotes[value].symbol
