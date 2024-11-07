"""Validate quote table state management, configuration & operations functionality."""

# pylint: disable=protected-access

# pyright: reportPrivateUsage=none

from __future__ import annotations

import math
import re
from contextlib import contextmanager
from time import sleep
from typing import TYPE_CHECKING, Any, Final

import pytest

from appui._enums import SortDirection
from appui.quote_table_state import QuoteTableState
from tests.fake_yfinance import FakeYFinance

from .helpers import compare_compact_ints

if TYPE_CHECKING:
    from appui._quote_table_data import QuoteRow

# A number with 2 decimal values
NUMBER_RE: Final[re.Pattern[str]] = re.compile(r"^(?:-?\d+\.\d{2}|N/A)$", re.MULTILINE)

# A percentage with 2 decimal values
PERCENT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:-?\d+\.\d{2}%|N/A)$", re.MULTILINE
)

# A compacted value
COMPACT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:\d{1,3}(?:\.\d{2}[KMBT])?|N/A)$", re.MULTILINE
)


@pytest.fixture(name="quote_table_state")
def fixture_qts() -> QuoteTableState:
    """
    Provide a QuoteTableState instance for testing.

    Returns:
        QuoteTableState: An instance of the QuoteTableState class, initialized with
        a FakeYFinance instance.
    """

    yfin = FakeYFinance()
    return QuoteTableState(yfin)


@pytest.fixture
def duplicate_column(qts: QuoteTableState) -> str:
    """
    Provide an existing column key for testing column validation.

    Returns:
        str: the key of the duplicate column.
    """

    return qts.quotes_columns[1].key


@contextmanager
def thread_running_context(qts: QuoteTableState):
    """
    Provide a context manager to temporarily set query_thread_running to True.

    This can be used to simulate a running query thread.

    Args:
        qts: The QuoteTableState instance to modify
    """
    qts.query_thread_running = True
    sleep(0.1)
    try:
        yield
    finally:
        qts.query_thread_running = False


##############################################################################
# load_config tests
##############################################################################


def test_load_regular_config(quote_table_state: QuoteTableState):
    """Ensure loading a well formed config works."""

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "last",
        QuoteTableState._SORT_DIRECTION: "desc",
        QuoteTableState._QUOTES: ["AAPL", "F", "VT"],
        QuoteTableState._QUERY_FREQUENCY: 15,
    }
    quote_table_state.load_config(config)
    assert (
        quote_table_state.column_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + config[QuoteTableState._COLUMNS]
    )
    assert quote_table_state.sort_column_key == config[QuoteTableState._SORT_COLUMN]
    assert (
        quote_table_state.sort_direction.value
        == config[QuoteTableState._SORT_DIRECTION]
    )
    assert quote_table_state._quotes_symbols == config[QuoteTableState._QUOTES]
    assert quote_table_state.query_frequency == config[QuoteTableState._QUERY_FREQUENCY]


def test_load_empty_config(quote_table_state: QuoteTableState):
    """Ensure defaults are used when loading an empty config."""

    config: dict[str, Any] = {}
    quote_table_state.load_config(config)
    assert quote_table_state.column_keys == [
        QuoteTableState._TICKER_COLUMN_KEY,
        *QuoteTableState._DEFAULT_COLUMN_KEYS,
    ]
    assert quote_table_state.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
    assert quote_table_state.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION
    assert quote_table_state._quotes_symbols == QuoteTableState._DEFAULT_QUOTES
    assert quote_table_state.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_config_invalid_columns(quote_table_state: QuoteTableState):
    """Ensure invalid columns are ignored when loading config."""

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["truly_not_a_column", "last"],
    }
    quote_table_state.load_config(config)
    assert quote_table_state.column_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_config_duplicate_columns(quote_table_state: QuoteTableState):
    """Ensure duplicate columns are ignored when loading config."""

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "last", "last"],
    }
    quote_table_state.load_config(config)
    assert quote_table_state.column_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_config_duplicate_default_column(quote_table_state: QuoteTableState):
    """Ensure the default column is ignored if specified in the config."""

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: [
            "last",
            "open",
            QuoteTableState._TICKER_COLUMN_KEY,
            "52w_low",
        ],
    }
    quote_table_state.load_config(config)
    assert quote_table_state.column_keys == [
        QuoteTableState._TICKER_COLUMN_KEY,
        "last",
        "open",
        "52w_low",
    ]


def test_load_config_invalid_sort_column(quote_table_state: QuoteTableState):
    """Ensure default column is used when invalid one is provided in config."""

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "truly_not_a_column",
    }
    quote_table_state.load_config(config)
    assert quote_table_state.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY


def test_load_config_invalid_sort_direction(quote_table_state: QuoteTableState):
    """Ensure default sort direction is used when invalid one is provided in config."""

    config: dict[str, Any] = {
        QuoteTableState._SORT_DIRECTION: "amazing",
    }
    quote_table_state.load_config(config)
    assert quote_table_state.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION


def test_load_config_invalid_query_frequency(quote_table_state: QuoteTableState):
    """Ensure invalid query frequency is ignored when loading config."""

    config: dict[str, Any] = {
        QuoteTableState._QUERY_FREQUENCY: 0,
    }
    quote_table_state.load_config(config)
    assert quote_table_state.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_config_empty_quote_symbol(quote_table_state: QuoteTableState):
    """Ensure empty symbols are ignored when loading config."""

    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL", "F", "", "VT"],
    }
    quote_table_state.load_config(config)
    assert quote_table_state._quotes_symbols == ["AAPL", "F", "VT"]


def test_load_config_duplicate_quote_symbol(quote_table_state: QuoteTableState):
    """Ensure duplicated of symbols are ignored when loading config."""

    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL", "F", "F", "VT", "AAPL"],
    }
    quote_table_state.load_config(config)
    assert quote_table_state._quotes_symbols == ["AAPL", "F", "VT"]


##############################################################################
# save_config tests
##############################################################################


def test_save_config(quote_table_state: QuoteTableState):
    """Ensure regular config saving works."""

    config: dict[str, Any] = quote_table_state.save_config()

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == quote_table_state.column_keys[1:]
    assert config[QuoteTableState._SORT_COLUMN] == quote_table_state.sort_column_key
    assert (
        config[QuoteTableState._SORT_DIRECTION]
        == quote_table_state.sort_direction.value
    )
    assert config[QuoteTableState._QUOTES] == quote_table_state._quotes_symbols
    assert config[QuoteTableState._QUERY_FREQUENCY] == quote_table_state.query_frequency


def test_save_config_takes_list_copies(quote_table_state: QuoteTableState):
    """Ensure that saving a config takes a copy of lists."""

    config: dict[str, Any] = quote_table_state.save_config()
    config[QuoteTableState._COLUMNS][0] = "foo_foo"
    config[QuoteTableState._QUOTES][0] = "ZZZZ"
    assert config[QuoteTableState._COLUMNS] != quote_table_state.column_keys
    assert config[QuoteTableState._QUOTES] != quote_table_state._quotes_symbols


def test_round_trip_config(quote_table_state: QuoteTableState):
    """Ensure that a round trip save and load works."""

    config: dict[str, Any] = quote_table_state.save_config()

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == quote_table_state.column_keys[1:]
    assert config[QuoteTableState._SORT_COLUMN] == quote_table_state.sort_column_key
    assert (
        config[QuoteTableState._SORT_DIRECTION]
        == quote_table_state.sort_direction.value
    )
    assert config[QuoteTableState._QUOTES] == quote_table_state._quotes_symbols
    assert config[QuoteTableState._QUERY_FREQUENCY] == quote_table_state.query_frequency

    config.clear()
    config[QuoteTableState._COLUMNS] = ["52w_high", "open"]
    config[QuoteTableState._SORT_COLUMN] = "52w_high"
    config[QuoteTableState._SORT_DIRECTION] = "desc"
    config[QuoteTableState._QUOTES] = ["FOOF"]
    config[QuoteTableState._QUERY_FREQUENCY] = 42

    quote_table_state.load_config(config)
    assert (
        quote_table_state.column_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + config[QuoteTableState._COLUMNS]
    )
    assert quote_table_state.sort_column_key == config[QuoteTableState._SORT_COLUMN]
    assert (
        quote_table_state.sort_direction.value
        == config[QuoteTableState._SORT_DIRECTION]
    )
    assert quote_table_state._quotes_symbols == config[QuoteTableState._QUOTES]
    assert quote_table_state.query_frequency == config[QuoteTableState._QUERY_FREQUENCY]


##############################################################################
# quotes_rows tests
##############################################################################


def test_default_get_quotes_rows(quote_table_state: QuoteTableState):
    """Ensure quote can be retrieved in the right order with expected values."""

    # Note the quotes are in alphabetical order, the same as the default sort order.
    # Sorting is tested below in test_rows_sorted* functions
    quotes: list[str] = ["^DJI", "AAPL", "F", "VT"]
    columns: list[str] = ["last", "change_percent", "market_cap"]
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: quotes,
        QuoteTableState._COLUMNS: columns,
    }

    quote_table_state.load_config(config)
    with thread_running_context(quote_table_state):
        sleep(0)

    rows: list[QuoteRow] = quote_table_state.quotes_rows

    assert len(rows) == len(quotes)

    for i, row in enumerate(rows):
        assert len(row.values) == len(columns) + 1  # +1 for symbol; always there
        assert row.values[0].value == quotes[i]
        assert NUMBER_RE.match(row.values[1].value)  # last
        assert PERCENT_RE.match(row.values[2].value)  # change_percent
        assert COMPACT_RE.match(row.values[3].value)  # market_cap


##############################################################################
# quotes_rows (sorting) tests
##############################################################################

# TODO: Try and parametrize the sorting tests as to only have one.


def test_rows_sorted_on_string(quote_table_state: QuoteTableState):
    """Ensure sorting rows based on string values works."""

    # The expectation is that the quotes are in alphabetical order, with symbols first.
    # This is _not_ the default sort order, as capital letters appear before the symbols
    # in ASCII
    quotes: list[str] = ["^DJI", "AAPL", "F", "VT"]  # This is the default sort order
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: quotes,
    }

    quote_table_state.load_config(config)
    with thread_running_context(quote_table_state):
        sleep(0)

    # this is the default sort key and direction
    assert quote_table_state.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
    assert quote_table_state.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = quote_table_state.quotes_rows
    for i, row in enumerate(rows):
        assert row.values[0].value == quotes[i]

    orig_version: int = quote_table_state.version

    quote_table_state.sort_direction = SortDirection.DESCENDING
    new_version: int = quote_table_state.version

    # The version should have changed following the sort direction change
    assert new_version == orig_version + 1

    rows = quote_table_state.quotes_rows
    for i, row in enumerate(rows):
        # The quotes are in reverse order now
        assert row.values[0].value == quotes[len(quotes) - 1 - i]


def test_rows_sorted_on_float(quote_table_state: QuoteTableState):
    """Ensure sorting rows based on float values works."""

    columns: list[str] = ["last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    quote_table_state.load_config(config)
    with thread_running_context(quote_table_state):
        sleep(0)

    orig_version: int = quote_table_state.version
    quote_table_state.sort_column_key = "last"
    new_version: int = quote_table_state.version

    # Get the column index of the sort column
    sort_column_index: int = quote_table_state.column_keys.index(
        quote_table_state.sort_column_key
    )

    # The version should have changed following the sort column change
    assert new_version == orig_version + 1
    assert quote_table_state.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = quote_table_state.quotes_rows

    prev: float = -math.inf  # Init to a value below anything we can encounter

    for row in rows:
        val: float = float(row.values[sort_column_index].value)
        assert val > prev
        prev = val

    quote_table_state.sort_direction = SortDirection.DESCENDING

    rows = quote_table_state.quotes_rows

    prev: float = math.inf  # Init to a value above anything we can encounter

    # The quotes are in reverse order now
    for row in rows:
        val: float = float(row.values[sort_column_index].value)
        assert val < prev
        prev = val


def test_rows_sorted_on_percent(quote_table_state: QuoteTableState):
    """Ensure sorting rows based on percentage values works."""

    columns: list[str] = ["change_percent"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    quote_table_state.load_config(config)
    with thread_running_context(quote_table_state):
        sleep(0)

    orig_version: int = quote_table_state.version
    quote_table_state.sort_column_key = "change_percent"
    new_version: int = quote_table_state.version

    # Get the column index of the sort column
    sort_column_index: int = quote_table_state.column_keys.index(
        quote_table_state.sort_column_key
    )

    # The version should have changed following the sort column change
    assert new_version == orig_version + 1
    assert quote_table_state.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = quote_table_state.quotes_rows

    prev: float = -math.inf  # Init to a value below anything we can encounter

    for row in rows:
        assert row.values[sort_column_index].value[-1] == "%"
        val: float = float(row.values[sort_column_index].value[:-1])
        assert val > prev
        prev = val

    quote_table_state.sort_direction = SortDirection.DESCENDING

    rows = quote_table_state.quotes_rows

    prev: float = math.inf  # Init to a value above anything we can encounter

    # The quotes are in reverse order now
    for row in rows:
        assert row.values[sort_column_index].value[-1] == "%"
        val: float = float(row.values[sort_column_index].value[:-1])
        assert val < prev
        prev = val


def test_rows_sorted_on_compact_int_and_equal_values(
    quote_table_state: QuoteTableState,
):
    """Ensure sorting rows based on compact integer values works."""

    with thread_running_context(quote_table_state):
        sleep(0)

    orig_version: int = quote_table_state.version
    quote_table_state.sort_column_key = "market_cap"
    new_version: int = quote_table_state.version

    # Get the column index of the sort column
    sort_column_index: int = quote_table_state.column_keys.index(
        quote_table_state.sort_column_key
    )

    # The version should have changed following the sort column change
    assert new_version == orig_version + 1
    assert quote_table_state.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = quote_table_state.quotes_rows

    prev: QuoteRow = rows[0]

    for row in rows[1:]:
        cmp: int = compare_compact_ints(
            prev.values[sort_column_index].value,
            row.values[sort_column_index].value,
        )
        assert cmp <= 0
        if cmp == 0:
            # If the values are equals (N/A, most likely), it should then be sorted
            # by the ticker.
            # Note that we're hardcoding the "lower" ticker, as it's the value used
            # for sorting in the ALL_QUOTES_COLUMNS definitions for the ticker.
            assert prev.values[0].value.lower() < row.values[0].value.lower()
        prev = row

    quote_table_state.sort_direction = SortDirection.DESCENDING

    rows = quote_table_state.quotes_rows

    prev: QuoteRow = rows[0]

    for row in rows[1:]:
        cmp: int = compare_compact_ints(
            prev.values[sort_column_index].value,
            row.values[sort_column_index].value,
        )
        assert cmp >= 0
        if cmp == 0:
            # See above
            assert prev.values[0].value.lower() > row.values[0].value.lower()
        prev = row


##############################################################################
# Row operations tests
##############################################################################


def test_set_current_row(quote_table_state: QuoteTableState):
    """Ensure setting the current row works."""

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    # By default, current row should not be set
    assert quote_table_state.cursor_row == -1
    assert quote_table_state._cursor_symbol == ""  # noqa: PLC1901

    # Set the current row
    new_cursor_row = 2
    orig_version: int = quote_table_state.version
    quote_table_state.cursor_row = new_cursor_row
    new_version: int = quote_table_state.version

    # Setting the cursor row should not change the version
    assert new_version == orig_version
    assert quote_table_state.cursor_row == new_cursor_row
    assert (
        quote_table_state._cursor_symbol
        == quote_table_state.quotes_rows[new_cursor_row].key
    )

    symbol = quote_table_state._cursor_symbol

    # Change the sort order, and verify the row points to the same symbol, but the index
    # of the row has changed
    quote_table_state.sort_direction = (
        SortDirection.DESCENDING
        if quote_table_state.sort_direction == SortDirection.ASCENDING
        else SortDirection.ASCENDING
    )
    assert quote_table_state.cursor_row != new_cursor_row
    assert symbol == quote_table_state._cursor_symbol
    assert symbol == quote_table_state.quotes_rows[quote_table_state.cursor_row].key


def test_delete_row_after_cursor(quote_table_state: QuoteTableState):
    """Ensure deleting a row after the cursor row works."""

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    new_cursor_row = 2
    quote_table_state.cursor_row = new_cursor_row
    symbol = quote_table_state._cursor_symbol

    row_to_remove = len(quote_table_state._cursor_symbol) - 1  # remove last row
    symbol_to_remove = quote_table_state.quotes_rows[row_to_remove].key
    row_count = len(quote_table_state.quotes_rows)
    symbols_count = len(quote_table_state._quotes_symbols)

    orig_version: int = quote_table_state.version
    quote_table_state.remove_row(row_to_remove)
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    assert quote_table_state.cursor_row == new_cursor_row  # This has not moved
    assert symbol == quote_table_state._cursor_symbol  # This has not changed
    assert len(quote_table_state.quotes_rows) == row_count - 1
    assert len(quote_table_state._quotes_symbols) == symbols_count - 1
    assert symbol_to_remove not in quote_table_state._quotes_symbols
    assert symbol_to_remove not in [row.key for row in quote_table_state.quotes_rows]


def test_delete_row_before_cursor(quote_table_state: QuoteTableState):
    """Ensure deleting a row before the cursor row works."""

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    new_cursor_row = 2
    quote_table_state.cursor_row = new_cursor_row
    symbol = quote_table_state._cursor_symbol

    row_to_remove = 0  # remove first row
    symbol_to_remove = quote_table_state.quotes_rows[row_to_remove].key
    row_count = len(quote_table_state.quotes_rows)
    symbols_count = len(quote_table_state._quotes_symbols)

    orig_version: int = quote_table_state.version
    quote_table_state.remove_row(row_to_remove)
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    assert quote_table_state.cursor_row == new_cursor_row - 1  # This is now one less
    assert symbol == quote_table_state._cursor_symbol  # This has not changed
    assert len(quote_table_state.quotes_rows) == row_count - 1
    assert len(quote_table_state._quotes_symbols) == symbols_count - 1
    assert symbol_to_remove not in quote_table_state._quotes_symbols
    assert symbol_to_remove not in [row.key for row in quote_table_state.quotes_rows]


def test_delete_on_cursor_row_middle(quote_table_state: QuoteTableState):
    """Ensure deleting the cursor row when there are items before and after it works."""

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    new_cursor_row = 2
    quote_table_state.cursor_row = new_cursor_row

    row_to_remove = new_cursor_row  # same as cursor row!
    symbol_to_remove = quote_table_state.quotes_rows[row_to_remove].key
    row_count = len(quote_table_state.quotes_rows)
    symbols_count = len(quote_table_state._quotes_symbols)
    expected_new_symbol = quote_table_state.quotes_rows[row_to_remove + 1].key

    orig_version: int = quote_table_state.version
    quote_table_state.remove_row(row_to_remove)
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    assert quote_table_state.cursor_row == new_cursor_row  # This is unchanged
    # This is the new symbol
    assert expected_new_symbol == quote_table_state._cursor_symbol
    assert len(quote_table_state.quotes_rows) == row_count - 1
    assert len(quote_table_state._quotes_symbols) == symbols_count - 1
    assert symbol_to_remove not in quote_table_state._quotes_symbols
    assert symbol_to_remove not in [row.key for row in quote_table_state.quotes_rows]


def test_delete_on_cursor_row_last(quote_table_state: QuoteTableState):
    """Ensure deleting the cursor row when the cursor is at the last row works."""

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    new_cursor_row = len(quote_table_state.quotes_rows) - 1
    quote_table_state.cursor_row = new_cursor_row

    row_to_remove = new_cursor_row  # same as cursor row!
    symbol_to_remove = quote_table_state.quotes_rows[row_to_remove].key
    row_count = len(quote_table_state.quotes_rows)
    symbols_count = len(quote_table_state._quotes_symbols)
    expected_new_symbol = quote_table_state.quotes_rows[row_to_remove - 1].key

    orig_version: int = quote_table_state.version
    quote_table_state.remove_row(row_to_remove)
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    # This will be the former penultimate row
    assert quote_table_state.cursor_row == new_cursor_row - 1
    # This is the new symbol
    assert expected_new_symbol == quote_table_state._cursor_symbol
    assert len(quote_table_state.quotes_rows) == row_count - 1
    assert len(quote_table_state._quotes_symbols) == symbols_count - 1
    assert symbol_to_remove not in quote_table_state._quotes_symbols
    assert symbol_to_remove not in [row.key for row in quote_table_state.quotes_rows]


def test_delete_on_cursor_row_first(quote_table_state: QuoteTableState):
    """Ensure deleting the cursor row when it's top row & table has many rows works."""

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    new_cursor_row = 0
    quote_table_state.cursor_row = new_cursor_row

    row_to_remove = new_cursor_row  # same as cursor row!
    symbol_to_remove = quote_table_state.quotes_rows[row_to_remove].key
    row_count = len(quote_table_state.quotes_rows)
    symbols_count = len(quote_table_state._quotes_symbols)
    expected_new_symbol = quote_table_state.quotes_rows[row_to_remove + 1].key

    orig_version: int = quote_table_state.version
    quote_table_state.remove_row(row_to_remove)
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    assert quote_table_state.cursor_row == new_cursor_row  # We stay at position 0!
    # This is the new symbol
    assert expected_new_symbol == quote_table_state._cursor_symbol
    assert len(quote_table_state.quotes_rows) == row_count - 1
    assert len(quote_table_state._quotes_symbols) == symbols_count - 1
    assert symbol_to_remove not in quote_table_state._quotes_symbols
    assert symbol_to_remove not in [row.key for row in quote_table_state.quotes_rows]


def test_delete_on_cursor_row_only(quote_table_state: QuoteTableState):
    """Ensure deleting the cursor row when it's top and only row works."""

    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL"],
    }

    quote_table_state.load_config(config)

    # Ensure everything is loaded
    with thread_running_context(quote_table_state):
        sleep(0)

    new_cursor_row = 0
    quote_table_state.cursor_row = new_cursor_row

    row_to_remove = new_cursor_row  # same as cursor row!
    expected_new_symbol = ""

    orig_version: int = quote_table_state.version
    quote_table_state.remove_row(row_to_remove)
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    assert quote_table_state.cursor_row == -1  # No more rows, no more cursor
    # This is the new symbol
    assert expected_new_symbol == quote_table_state._cursor_symbol
    assert len(quote_table_state.quotes_rows) == 0
    assert len(quote_table_state._quotes_symbols) == 0


##############################################################################
# Columns operations tests
##############################################################################


def test_add_column(quote_table_state: QuoteTableState):
    """Ensure adding a valid column to the table works."""

    columns: list[str] = ["market_cap"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    quote_table_state.load_config(config)
    with thread_running_context(quote_table_state):
        sleep(0)

    column_count: int = len(columns) + 1  # +1 for the ticker; always there

    assert len(quote_table_state.quotes_columns) == column_count
    assert quote_table_state.quotes_columns[1].key == columns[0]

    rows: list[QuoteRow] = quote_table_state.quotes_rows
    for row in rows:
        assert len(row.values) == column_count

    orig_version: int = quote_table_state.version
    new_column: str = "change_percent"
    quote_table_state.append_column(new_column)
    column_count += 1  # +1 for the new column
    new_version: int = quote_table_state.version

    # Check the rows again and see if the new column has been added
    rows = quote_table_state.quotes_rows
    for row in rows:
        assert len(row.values) == column_count

    # The version should have changed following the column addition
    assert new_version == orig_version + 1
    assert len(quote_table_state.quotes_columns) == column_count
    assert quote_table_state.quotes_columns[2].key == new_column


@pytest.mark.parametrize(
    "column_name",
    [duplicate_column, QuoteTableState._TICKER_COLUMN_KEY, "not_a_valid_column"],
)
def test_add_invalid_column(quote_table_state: QuoteTableState, column_name: str):
    """Ensure we can't add an invalid column to the table."""

    column_count: int = len(quote_table_state.quotes_columns)

    orig_version: int = quote_table_state.version
    quote_table_state.append_column(column_name)
    new_version: int = quote_table_state.version

    # The version should not have changed since nothing has been inserted
    assert new_version == orig_version
    assert len(quote_table_state.quotes_columns) == column_count


@pytest.mark.parametrize(
    ("insertion_idx", "validation_idx"),
    [(1, 1), (2, 2), (3, 3), (4, 4), (100, 4), (-1, 3), (-2, 2), (-3, 1)],
)
def test_insert_column(
    quote_table_state: QuoteTableState, insertion_idx: int, validation_idx: int
):
    """Ensure inserting a valid column in a valid spot to the table works."""

    columns: list[str] = ["market_cap", "change_percent", "last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    quote_table_state.load_config(config)
    column_count: int = len(quote_table_state.quotes_columns)
    assert len(columns) + 1 == column_count

    orig_version: int = quote_table_state.version
    new_column_name: str = "dividend"
    quote_table_state.insert_column(insertion_idx, new_column_name)
    column_count += 1  # +1 for the new column
    new_version: int = quote_table_state.version

    assert new_version == orig_version + 1
    assert len(quote_table_state.quotes_columns) == column_count
    assert quote_table_state.quotes_columns[validation_idx].key == new_column_name


@pytest.mark.parametrize(
    "insertion_idx",
    [0, -4, -100],
)
def test_cant_insert_column_at_invalid_index(
    quote_table_state: QuoteTableState, insertion_idx: int
):
    """Ensure no column can be inserted at the default column's index (0), or before."""

    columns: list[str] = ["market_cap", "change_percent", "last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    quote_table_state.load_config(config)
    column_count: int = len(quote_table_state.quotes_columns)
    assert len(columns) + 1 == column_count

    orig_version: int = quote_table_state.version
    new_column_name: str = "dividend"
    quote_table_state.insert_column(insertion_idx, new_column_name)
    new_version: int = quote_table_state.version

    # No version bump, the column was not inserted
    assert new_version == orig_version
    assert len(quote_table_state.quotes_columns) == column_count
    assert new_column_name not in quote_table_state.column_keys


@pytest.mark.parametrize(
    "column_name",
    [duplicate_column, "not_a_valid_column"],
)
def test_insert_invalid_column(quote_table_state: QuoteTableState, column_name: str):
    """Ensure invalid columns can't be inserted."""

    column_count: int = len(quote_table_state.quotes_columns)

    orig_version: int = quote_table_state.version
    quote_table_state.insert_column(1, column_name)
    new_version: int = quote_table_state.version

    # The version should not have changed since nothing has been inserted
    assert new_version == orig_version
    assert len(quote_table_state.quotes_columns) == column_count


def test_remove_regular_column(quote_table_state: QuoteTableState):
    """Ensure removing a valid column from the table works."""

    column_count: int = len(quote_table_state.quotes_columns)

    orig_version: int = quote_table_state.version
    quote_table_state.remove_column(quote_table_state.quotes_columns[1].key)
    column_count -= 1
    new_version: int = quote_table_state.version

    # The version should not have changed since nothing has been inserted
    assert new_version == orig_version + 1
    assert len(quote_table_state.quotes_columns) == column_count


def test_remove_ticker_column(quote_table_state: QuoteTableState):
    """Ensure removing the ticker column from the table raises a ValueError."""

    with pytest.raises(ValueError, match="Cannot remove ticker column"):
        quote_table_state.remove_column(QuoteTableState._TICKER_COLUMN_KEY)


def test_remove_invalid_column(quote_table_state: QuoteTableState):
    """Ensure removing an invalid column from the table raises a ValueError."""

    column_name: str = "not_a_valid_column"
    with pytest.raises(
        ValueError, match=f"Column key {column_name} does not exist in the quote table"
    ):
        quote_table_state.remove_column(column_name)


def test_remove_sorting_column(quote_table_state: QuoteTableState):
    """Ensure removing the sorting column reverts sorting to the default column."""

    first_column_name: str = quote_table_state.quotes_columns[1].key
    quote_table_state.sort_column_key = first_column_name
    orig_version: int = quote_table_state.version
    quote_table_state.remove_column(first_column_name)
    new_version: int = quote_table_state.version

    # Even though there has also been a change in the sorting column, the version
    # should only have increased by 1 (the removal).
    assert new_version == orig_version + 1
    assert quote_table_state.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
