# pylint: disable=protected-access
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import math
import re
import sys
from contextlib import contextmanager
from time import sleep
from typing import Any

import pytest

from appui._enums import SortDirection
from appui._quote_table_data import QuoteRow
from appui.quote_table_state import QuoteTableState

from .fake_yfinance import FakeYFinance
from .helpers import compare_shrunken_ints

# A number with 2 decimal values
NUMBER_RE: re.Pattern = re.compile(r"^(?:-?\d+\.\d{2}|N/A)$", re.M)

# A percentage with 2 decimal values
PERCENT_RE: re.Pattern = re.compile(r"^(?:-?\d+\.\d{2}%|N/A)$", re.M)

# A shrunken int
SHRUNKEN_INT_RE: re.Pattern = re.compile(r"^(?:\d{1,3}(?:\.\d{2}[KMBT])?|N/A)$", re.M)


@pytest.fixture
def fixture_qts() -> QuoteTableState:
    """
    An instance of the QuoteTableState class, with a FakeYFinance instance to get the
    quotes.
    """
    yfin = FakeYFinance()
    qts = QuoteTableState(yfin)
    return qts


@pytest.fixture
def duplicate_column(fixture_qts: QuoteTableState):
    """
    Helper fixture for testing invalid column addition and insertion.
    """
    return fixture_qts.quotes_columns[1].key


@contextmanager
def thread_running_context(qts: QuoteTableState):
    qts.query_thread_running = True
    sleep(0.1)
    try:
        yield
    finally:
        qts.query_thread_running = False


##############################################################################
## load_config tests
##############################################################################


def test_load_regular_config(fixture_qts: QuoteTableState):
    """
    Regular config loading.
    This is expected to work.
    """

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "last",
        QuoteTableState._SORT_DIRECTION: "desc",
        QuoteTableState._QUOTES: ["AAPL", "F", "VT"],
        QuoteTableState._QUERY_FREQUENCY: 15,
    }
    fixture_qts.load_config(config)
    assert (
        fixture_qts.column_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + config[QuoteTableState._COLUMNS]
    )
    assert fixture_qts.sort_column_key == config[QuoteTableState._SORT_COLUMN]
    assert fixture_qts.sort_direction.value == config[QuoteTableState._SORT_DIRECTION]
    assert fixture_qts._quotes_symbols == config[QuoteTableState._QUOTES]
    assert fixture_qts.query_frequency == config[QuoteTableState._QUERY_FREQUENCY]


def test_load_empty_config(fixture_qts: QuoteTableState):
    """
    Empty config loading.
    This is expected to work.
    The defaults should be used.
    """

    config: dict[str, Any] = {}
    fixture_qts.load_config(config)
    assert (
        fixture_qts.column_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + QuoteTableState._DEFAULT_COLUMN_KEYS
    )
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
    assert fixture_qts.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION
    assert fixture_qts._quotes_symbols == QuoteTableState._DEFAULT_QUOTES
    assert fixture_qts.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_config_invalid_columns(fixture_qts: QuoteTableState):
    """
    Config loading with an invalid column.
    This is expected to work.
    The invalid column should be ignored.
    """

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["truly_not_a_column", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts.column_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_config_duplicate_columns(fixture_qts: QuoteTableState):
    """
    Config loading with an a column defined more than once.
    This is expected to work.
    The duplicated columns should be ignored.
    """

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "last", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts.column_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_config_duplicate_default_column(fixture_qts: QuoteTableState):
    """
    Config loading with the default specified in the config.
    This is expected to work.
    The default column should be added again.
    """

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: [
            "last",
            "open",
            QuoteTableState._TICKER_COLUMN_KEY,
            "52w_low",
        ],
    }
    fixture_qts.load_config(config)
    assert fixture_qts.column_keys == [
        QuoteTableState._TICKER_COLUMN_KEY,
        "last",
        "open",
        "52w_low",
    ]


def test_load_config_invalid_sort_column(fixture_qts: QuoteTableState):
    """
    Config loading an invalid sort column.
    This is expected to work.
    The default column should be used as sort column.
    """

    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "truly_not_a_column",
    }
    fixture_qts.load_config(config)
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY


def test_load_config_invalid_sort_direction(fixture_qts: QuoteTableState):
    """
    Config loading an invalid sort direction.
    This is expected to work.
    The default sort direction should be used.
    """

    config: dict[str, Any] = {
        QuoteTableState._SORT_DIRECTION: "amazing",
    }
    fixture_qts.load_config(config)
    assert fixture_qts.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION


def test_load_config_invalid_query_frequency(fixture_qts: QuoteTableState):
    """
    Config loading an invalid quote querying frequency.
    This is expected to work.
    The default query frequency should be used.
    """

    config: dict[str, Any] = {
        QuoteTableState._QUERY_FREQUENCY: 0,
    }
    fixture_qts.load_config(config)
    assert fixture_qts.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_config_empty_quote_symbol(fixture_qts: QuoteTableState):
    """
    Config loading a quote symbol that is an empty string.
    This is expected to work.
    The invalid quote symbol should be ignored.
    """

    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL", "F", "", "VT"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._quotes_symbols == ["AAPL", "F", "VT"]


def test_load_config_duplicate_quote_symbol(fixture_qts: QuoteTableState):
    """
    Config loading with quote symbols defined more than once.
    This is expected to work.
    The duplicated quote symbols should be ignored.
    """

    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL", "F", "F", "VT", "AAPL"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._quotes_symbols == ["AAPL", "F", "VT"]


##############################################################################
## save_config tests
##############################################################################


def test_save_config(fixture_qts: QuoteTableState):
    """
    Regular config saving.
    This is expected to work.
    """

    config: dict[str, Any] = fixture_qts.save_config()

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == fixture_qts.column_keys[1:]
    assert config[QuoteTableState._SORT_COLUMN] == fixture_qts.sort_column_key
    assert config[QuoteTableState._SORT_DIRECTION] == fixture_qts.sort_direction.value
    assert config[QuoteTableState._QUOTES] == fixture_qts._quotes_symbols
    assert config[QuoteTableState._QUERY_FREQUENCY] == fixture_qts.query_frequency


def test_save_config_takes_list_copies(fixture_qts: QuoteTableState):
    """
    Make sure that saving a config takes a copy of lists.
    This is expected to work.
    """

    config: dict[str, Any] = fixture_qts.save_config()
    config[QuoteTableState._COLUMNS][0] = "foo_foo"
    config[QuoteTableState._QUOTES][0] = "ZZZZ"
    assert config[QuoteTableState._COLUMNS] != fixture_qts.column_keys
    assert config[QuoteTableState._QUOTES] != fixture_qts._quotes_symbols


def test_round_trip_config(fixture_qts: QuoteTableState):
    """
    Make sure that a round trip save and load works.
    This is expected to work.
    """

    config: dict[str, Any] = fixture_qts.save_config()

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == fixture_qts.column_keys[1:]
    assert config[QuoteTableState._SORT_COLUMN] == fixture_qts.sort_column_key
    assert config[QuoteTableState._SORT_DIRECTION] == fixture_qts.sort_direction.value
    assert config[QuoteTableState._QUOTES] == fixture_qts._quotes_symbols
    assert config[QuoteTableState._QUERY_FREQUENCY] == fixture_qts.query_frequency

    config.clear()
    config[QuoteTableState._COLUMNS] = ["52w_high", "open"]
    config[QuoteTableState._SORT_COLUMN] = "52w_high"
    config[QuoteTableState._SORT_DIRECTION] = "desc"
    config[QuoteTableState._QUOTES] = ["FOOF"]
    config[QuoteTableState._QUERY_FREQUENCY] = 42

    fixture_qts.load_config(config)
    assert (
        fixture_qts.column_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + config[QuoteTableState._COLUMNS]
    )
    assert fixture_qts.sort_column_key == config[QuoteTableState._SORT_COLUMN]
    assert fixture_qts.sort_direction.value == config[QuoteTableState._SORT_DIRECTION]
    assert fixture_qts._quotes_symbols == config[QuoteTableState._QUOTES]
    assert fixture_qts.query_frequency == config[QuoteTableState._QUERY_FREQUENCY]


##############################################################################
## quotes_rows tests
##############################################################################


def test_default_get_quotes_rows(fixture_qts: QuoteTableState):
    """
    Make sure quote can be retrieved, their order is correct, and the values
    correct.
    This is expected to work.
    """

    # Note the quotes are in alphabetical order, the same as the default sort order.
    # Sorting is tested below in test_rows_sorted* functions
    quotes: list[str] = ["^DJI", "AAPL", "F", "VT"]
    columns: list[str] = ["last", "change_percent", "market_cap"]
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: quotes,
        QuoteTableState._COLUMNS: columns,
        QuoteTableState._QUERY_FREQUENCY: sys.maxsize,
    }

    fixture_qts.load_config(config)
    with thread_running_context(fixture_qts):
        rows: list[QuoteRow] = fixture_qts.quotes_rows

        assert len(rows) == len(quotes)

        for i, row in enumerate(rows):
            assert len(row.values) == len(columns) + 1  # +1 for symbol; always there
            assert row.values[0].value == quotes[i]
            assert NUMBER_RE.match(row.values[1].value)  # last
            assert PERCENT_RE.match(row.values[2].value)  # change_percent
            assert SHRUNKEN_INT_RE.match(row.values[3].value)  # market_cap


##############################################################################
## quotes_rows (sorting) tests
##############################################################################

# TODO: Try and parametrize the sorting tests as to only have one.


def test_rows_sorted_on_string(fixture_qts: QuoteTableState):
    # The expectation is that the quotes are in alphabetical order, with symbols first.
    # This is _not_ the default sort order, as capital letters appear before the symbols
    # in ASCII
    quotes: list[str] = ["^DJI", "AAPL", "F", "VT"]  # This is the default sort order
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: quotes,
        QuoteTableState._QUERY_FREQUENCY: sys.maxsize,
    }

    fixture_qts.load_config(config)
    with thread_running_context(fixture_qts):
        # this is the default sort key and direction
        assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
        assert fixture_qts.sort_direction == SortDirection.ASCENDING

        rows: list[QuoteRow] = fixture_qts.quotes_rows
        for i, row in enumerate(rows):
            assert row.values[0].value == quotes[i]

        orig_version: int = fixture_qts.version

        fixture_qts.sort_direction = SortDirection.DESCENDING
        new_version: int = fixture_qts.version

        # The version should have changed following the sort direction change
        assert new_version == orig_version + 1

        rows = fixture_qts.quotes_rows
        for i, row in enumerate(rows):
            # The quotes are in reverse order now
            assert row.values[0].value == quotes[len(quotes) - 1 - i]


def test_rows_sorted_on_float(fixture_qts: QuoteTableState):
    columns: list[str] = ["last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
        QuoteTableState._QUERY_FREQUENCY: sys.maxsize,
    }

    fixture_qts.load_config(config)
    with thread_running_context(fixture_qts):
        orig_version: int = fixture_qts.version
        fixture_qts.sort_column_key = "last"
        new_version: int = fixture_qts.version

        # Get the column index of the sort column
        sort_column_index: int = fixture_qts.column_keys.index(
            fixture_qts.sort_column_key
        )

        # The version should have changed following the sort column change
        assert new_version == orig_version + 1
        assert fixture_qts.sort_direction == SortDirection.ASCENDING

        rows: list[QuoteRow] = fixture_qts.quotes_rows

        prev: float = -math.inf  # Init to a value below anything we can encounter

        for row in rows:
            val: float = float(row.values[sort_column_index].value)
            assert val > prev
            prev = val

        fixture_qts.sort_direction = SortDirection.DESCENDING

        rows = fixture_qts.quotes_rows

        prev: float = math.inf  # Init to a value above anything we can encounter

        # The quotes are in reverse order now
        for row in rows:
            val: float = float(row.values[sort_column_index].value)
            assert val < prev
            prev = val


def test_rows_sorted_on_percent(fixture_qts: QuoteTableState):
    columns: list[str] = ["change_percent"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
        QuoteTableState._QUERY_FREQUENCY: sys.maxsize,
    }

    fixture_qts.load_config(config)
    with thread_running_context(fixture_qts):
        orig_version: int = fixture_qts.version
        fixture_qts.sort_column_key = "change_percent"
        new_version: int = fixture_qts.version

        # Get the column index of the sort column
        sort_column_index: int = fixture_qts.column_keys.index(
            fixture_qts.sort_column_key
        )

        # The version should have changed following the sort column change
        assert new_version == orig_version + 1
        assert fixture_qts.sort_direction == SortDirection.ASCENDING

        rows: list[QuoteRow] = fixture_qts.quotes_rows

        prev: float = -math.inf  # Init to a value below anything we can encounter

        for row in rows:
            assert row.values[sort_column_index].value[-1] == "%"
            val: float = float(row.values[sort_column_index].value[:-1])
            assert val > prev
            prev = val

        fixture_qts.sort_direction = SortDirection.DESCENDING

        rows = fixture_qts.quotes_rows

        prev: float = math.inf  # Init to a value above anything we can encounter

        # The quotes are in reverse order now
        for row in rows:
            assert row.values[sort_column_index].value[-1] == "%"
            val: float = float(row.values[sort_column_index].value[:-1])
            assert val < prev
            prev = val


def test_rows_sorted_on_shrunken_int_and_equal_values(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._QUERY_FREQUENCY: sys.maxsize,
    }

    fixture_qts.load_config(config)
    with thread_running_context(fixture_qts):
        orig_version: int = fixture_qts.version
        fixture_qts.sort_column_key = "market_cap"
        new_version: int = fixture_qts.version

        # Get the column index of the sort column
        sort_column_index: int = fixture_qts.column_keys.index(
            fixture_qts.sort_column_key
        )

        # The version should have changed following the sort column change
        assert new_version == orig_version + 1
        assert fixture_qts.sort_direction == SortDirection.ASCENDING

        rows: list[QuoteRow] = fixture_qts.quotes_rows

        prev: QuoteRow = rows[0]

        for row in rows[1:]:
            cmp: int = compare_shrunken_ints(
                prev.values[sort_column_index].value,
                row.values[sort_column_index].value,
            )
            assert cmp <= 0
            if cmp == 0:
                # If the values are equals (N/A, most likely), it should then be sorted by
                # the ticker.
                # Note that we'er hardcoding the "lower" ticker, as it's the value used
                # for sorting in the ALL_QUOTES_COLUMNS definitions for the ticker.
                assert prev.values[0].value.lower() < row.values[0].value.lower()
            prev = row

        fixture_qts.sort_direction = SortDirection.DESCENDING

        rows = fixture_qts.quotes_rows

        prev: QuoteRow = rows[0]

        for row in rows[1:]:
            cmp: int = compare_shrunken_ints(
                prev.values[sort_column_index].value,
                row.values[sort_column_index].value,
            )
            assert cmp >= 0
            if cmp == 0:
                # See above
                assert prev.values[0].value.lower() > row.values[0].value.lower()
            prev = row


##############################################################################
## Columns operations tests
##############################################################################


def test_add_column(fixture_qts: QuoteTableState):
    """
    Try to add a valid column to the table.
    This is expected to work.
    """

    columns: list[str] = ["market_cap"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
        QuoteTableState._QUERY_FREQUENCY: sys.maxsize,
    }

    fixture_qts.load_config(config)
    with thread_running_context(fixture_qts):
        column_count: int = len(columns) + 1  # +1 for the ticker; always there

        assert len(fixture_qts.quotes_columns) == column_count
        assert fixture_qts.quotes_columns[1].key == columns[0]

        rows: list[QuoteRow] = fixture_qts.quotes_rows
        for row in rows:
            assert len(row.values) == column_count

        orig_version: int = fixture_qts.version
        new_column: str = "change_percent"
        fixture_qts.append_column(new_column)
        column_count += 1  # +1 for the new column
        new_version: int = fixture_qts.version

        # Check the rows again and see if the new column has been added
        rows = fixture_qts.quotes_rows
        for row in rows:
            assert len(row.values) == column_count

        # The version should have changed following the column addition
        assert new_version == orig_version + 1
        assert len(fixture_qts.quotes_columns) == column_count
        assert fixture_qts.quotes_columns[2].key == new_column


@pytest.mark.parametrize(
    "column_name",
    [duplicate_column, QuoteTableState._TICKER_COLUMN_KEY, "not_a_valid_column"],
)
def test_add_invalid_column(fixture_qts: QuoteTableState, column_name: str):
    """
    Try to add an invalid column to the table.
    This is not expected to work.
    """

    column_count: int = len(fixture_qts.quotes_columns)

    orig_version: int = fixture_qts.version
    fixture_qts.append_column(column_name)
    new_version: int = fixture_qts.version

    # The version should not have changed since nothing has been inserted
    assert new_version == orig_version
    assert len(fixture_qts.quotes_columns) == column_count


@pytest.mark.parametrize(
    "insertion_idx, validation_idx",
    [(1, 1), (2, 2), (3, 3), (4, 4), (100, 4), (-1, 3), (-2, 2), (-3, 1)],
)
def test_insert_column(
    fixture_qts: QuoteTableState, insertion_idx: int, validation_idx: int
):
    """
    Try to insert a valid column in a valid spot to the table.
    This is expected to work.
    """

    columns: list[str] = ["market_cap", "change_percent", "last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    fixture_qts.load_config(config)
    column_count: int = len(fixture_qts.quotes_columns)
    assert len(columns) + 1 == column_count

    orig_version: int = fixture_qts.version
    new_column_name: str = "dividend"
    fixture_qts.insert_column(insertion_idx, new_column_name)
    column_count += 1  # +1 for the new column
    new_version: int = fixture_qts.version

    assert new_version == orig_version + 1
    assert len(fixture_qts.quotes_columns) == column_count
    assert fixture_qts.quotes_columns[validation_idx].key == new_column_name


@pytest.mark.parametrize(
    "insertion_idx",
    [0, -4, -100],
)
def test_cant_insert_column_at_invalid_index(
    fixture_qts: QuoteTableState, insertion_idx: int
):
    """
    Try to insert a valid column at the position of the default column, or below.
    This is not expected to work.
    """

    columns: list[str] = ["market_cap", "change_percent", "last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    fixture_qts.load_config(config)
    column_count: int = len(fixture_qts.quotes_columns)
    assert len(columns) + 1 == column_count

    orig_version: int = fixture_qts.version
    new_column_name: str = "dividend"
    fixture_qts.insert_column(insertion_idx, new_column_name)
    new_version: int = fixture_qts.version

    # No version bump, the column was not inserted
    assert new_version == orig_version
    assert len(fixture_qts.quotes_columns) == column_count
    assert new_column_name not in fixture_qts.column_keys


@pytest.mark.parametrize(
    "column_name",
    [duplicate_column, "not_a_valid_column"],
)
def test_insert_invalid_column(fixture_qts: QuoteTableState, column_name: str):
    """
    Try to insert an invalid column at a valid spot to the table.
    This is not expected to work.
    """

    column_count: int = len(fixture_qts.quotes_columns)

    orig_version: int = fixture_qts.version
    fixture_qts.insert_column(1, column_name)
    new_version: int = fixture_qts.version

    # The version should not have changed since nothing has been inserted
    assert new_version == orig_version
    assert len(fixture_qts.quotes_columns) == column_count


def test_remove_regular_column(fixture_qts: QuoteTableState):
    """
    Try to remove a valid column from the table.
    This is expected to work.
    """

    column_count: int = len(fixture_qts.quotes_columns)

    orig_version: int = fixture_qts.version
    fixture_qts.remove_column(fixture_qts.quotes_columns[1].key)
    column_count -= 1
    new_version: int = fixture_qts.version

    # The version should not have changed since nothing has been inserted
    assert new_version == orig_version + 1
    assert len(fixture_qts.quotes_columns) == column_count


@pytest.mark.parametrize(
    "column_name",
    # Can't remove the default column, or a column that doesn't exist
    [QuoteTableState._TICKER_COLUMN_KEY, "not_a_valid_column"],
)
def test_remove_invalid_column(fixture_qts: QuoteTableState, column_name: str):
    """
    Try to remove an invalid column from the table.
    This is not expected to work.
    """

    with pytest.raises(ValueError):
        fixture_qts.remove_column(column_name)


def test_remove_sorting_column(fixture_qts: QuoteTableState):
    """
    Try to remove the column on which the sorting is based.
    This is expected to work.
    The new sorting column should be the default column.
    """

    first_column_name: str = fixture_qts.quotes_columns[1].key
    fixture_qts.sort_column_key = first_column_name
    orig_version: int = fixture_qts.version
    fixture_qts.remove_column(first_column_name)
    new_version: int = fixture_qts.version

    # Even though there has also been a change in the sorting column, the version
    # should only have increased by 1 (the removal).
    assert new_version == orig_version + 1
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
