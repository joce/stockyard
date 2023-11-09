# pylint: disable=protected-access
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import math
import re
from time import monotonic
from typing import Any

import pytest

from appui._enums import SortDirection
from appui._quote_table_data import QuoteRow
from appui.quote_table_state import QuoteTableState

from .fake_yfinance import FakeYFinance
from .helpers import compare_shrunken_ints

# A number with 2 decimal values
NUMBER_RE: re.Pattern = re.compile(r"^(?:-?\d+\.\d{2}|N/A)$", re.M)

# a percentage with 2 decimal values
PERCENT_RE: re.Pattern = re.compile(r"^(?:-?\d+\.\d{2}%|N/A)$", re.M)

# a shrunken int
SHRUNKEN_INT_RE: re.Pattern = re.compile(r"^(?:\d{1,3}(?:\.\d{2}[KMBT])?|N/A)$", re.M)


@pytest.fixture
def fixture_qts() -> QuoteTableState:
    yfin = FakeYFinance()
    qts = QuoteTableState(yfin)
    return qts


def test_load_regular_config(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "last",
        QuoteTableState._SORT_DIRECTION: "desc",
        QuoteTableState._QUOTES: ["AAPL", "F", "VT"],
        QuoteTableState._QUERY_FREQUENCY: 15,
    }
    fixture_qts.load_config(config)
    assert (
        fixture_qts._columns_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + config[QuoteTableState._COLUMNS]
    )
    assert fixture_qts.sort_column_key == config[QuoteTableState._SORT_COLUMN]
    assert fixture_qts.sort_direction.value == config[QuoteTableState._SORT_DIRECTION]
    assert fixture_qts._quotes_symbols == config[QuoteTableState._QUOTES]
    assert fixture_qts.query_frequency == config[QuoteTableState._QUERY_FREQUENCY]


def test_load_empty_config(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}
    fixture_qts.load_config(config)
    assert (
        fixture_qts._columns_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + QuoteTableState._DEFAULT_COLUMN_KEYS
    )
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
    assert fixture_qts.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION
    assert fixture_qts._quotes_symbols == QuoteTableState._DEFAULT_QUOTES
    assert fixture_qts.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_config_invalid_columns(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["truly_not_a_column", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_config_duplicate_columns(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "last", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_config_duplicate_mandatory_column(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: [
            "last",
            "open",
            QuoteTableState._TICKER_COLUMN_KEY,
            "52w_low",
        ],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == [
        QuoteTableState._TICKER_COLUMN_KEY,
        "last",
        "open",
        "52w_low",
    ]


def test_load_config_invalid_sort_column(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "truly_not_a_column",
    }
    fixture_qts.load_config(config)
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY


def test_load_config_invalid_sort_direction(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._SORT_DIRECTION: "amazing",
    }
    fixture_qts.load_config(config)
    assert fixture_qts.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION


def test_load_config_invalid_query_frequency(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._QUERY_FREQUENCY: 0,
    }
    fixture_qts.load_config(config)
    assert fixture_qts.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_config_empty_quote_symbol(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL", "F", "", "VT"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._quotes_symbols == ["AAPL", "F", "VT"]


def test_load_config_duplicate_quote_symbol(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: ["AAPL", "F", "F", "VT", "AAPL"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._quotes_symbols == ["AAPL", "F", "VT"]


def test_save_config_empty_dict(fixture_qts: QuoteTableState):
    config: dict[str, Any] = fixture_qts.save_config()

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == fixture_qts._columns_keys[1:]
    assert config[QuoteTableState._SORT_COLUMN] == fixture_qts.sort_column_key
    assert config[QuoteTableState._SORT_DIRECTION] == fixture_qts.sort_direction.value
    assert config[QuoteTableState._QUOTES] == fixture_qts._quotes_symbols
    assert config[QuoteTableState._QUERY_FREQUENCY] == fixture_qts.query_frequency


def test_save_config_takes_list_copies(fixture_qts: QuoteTableState):
    config: dict[str, Any] = fixture_qts.save_config()
    config[QuoteTableState._COLUMNS][0] = "foo_foo"
    config[QuoteTableState._QUOTES][0] = "ZZZZ"
    assert config[QuoteTableState._COLUMNS] != fixture_qts._columns_keys
    assert config[QuoteTableState._QUOTES] != fixture_qts._quotes_symbols


def test_round_trip_config(fixture_qts: QuoteTableState):
    config: dict[str, Any] = fixture_qts.save_config()

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == fixture_qts._columns_keys[1:]
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
        fixture_qts._columns_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + config[QuoteTableState._COLUMNS]
    )
    assert fixture_qts.sort_column_key == config[QuoteTableState._SORT_COLUMN]
    assert fixture_qts.sort_direction.value == config[QuoteTableState._SORT_DIRECTION]
    assert fixture_qts._quotes_symbols == config[QuoteTableState._QUOTES]
    assert fixture_qts.query_frequency == config[QuoteTableState._QUERY_FREQUENCY]


def test_default_get_quotes_rows(fixture_qts: QuoteTableState):
    columns: list[str] = ["last", "change_percent", "market_cap"]
    # Note the quotes are in alphabetical order, the same as the default sort order.
    # Sorting is tested below in TODO
    quotes: list[str] = ["^DJI", "AAPL", "F", "VT"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
        QuoteTableState._QUOTES: quotes,
    }

    fixture_qts.load_config(config)
    # Make sure the quotes are loaded from an "external" source
    fixture_qts._load_quotes_internal(monotonic())
    rows: list[QuoteRow] = fixture_qts.get_quotes_rows()

    assert len(rows) == len(quotes)

    for i, row in enumerate(rows):
        assert len(row.values) == len(columns) + 1  # +1 for symbol; always there
        assert row.values[0].value == quotes[i]
        assert NUMBER_RE.match(row.values[1].value)  # last
        assert PERCENT_RE.match(row.values[2].value)  # change_percent
        assert SHRUNKEN_INT_RE.match(row.values[3].value)  # market_cap


def test_rows_sorted_on_string(fixture_qts: QuoteTableState):
    # The expectation is that the quotes are in alphabetical order, with symbols first.
    # This is _not_ the default sort order, as capital letters appear before the symbols
    # in ASCII
    quotes: list[str] = ["^DJI", "AAPL", "F", "VT"]  # This is the default sort order
    config: dict[str, Any] = {
        QuoteTableState._QUOTES: quotes,
    }

    fixture_qts.load_config(config)
    # Make sure the quotes are loaded from an "external" source
    fixture_qts._load_quotes_internal(monotonic())

    # this is the default sort key and direction
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY
    assert fixture_qts.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = fixture_qts.get_quotes_rows()

    for i, row in enumerate(rows):
        assert row.values[0].value == quotes[i]

    orig_version: int = fixture_qts.version

    fixture_qts.sort_direction = SortDirection.DESCENDING
    new_version: int = fixture_qts.version

    # The version should have changed following the sort direction change
    assert new_version > orig_version

    rows = fixture_qts.get_quotes_rows()

    # The quotes are in reverse order now
    for i, row in enumerate(rows):
        assert row.values[0].value == quotes[len(quotes) - 1 - i]


def test_rows_sorted_on_float(fixture_qts: QuoteTableState):
    columns: list[str] = ["last"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    fixture_qts.load_config(config)
    # Make sure the quotes are loaded from an "external" source
    fixture_qts._load_quotes_internal(monotonic())

    fixture_qts.sort_column_key = "last"
    assert fixture_qts.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = fixture_qts.get_quotes_rows()

    prev: float = -math.inf  # Init to a value below anything we can encounter

    for row in rows:
        val: float = float(row.values[1].value)
        assert val > prev
        prev = val

    fixture_qts.sort_direction = SortDirection.DESCENDING

    rows = fixture_qts.get_quotes_rows()

    prev: float = math.inf  # Init to a value above anything we can encounter

    # The quotes are in reverse order now
    for row in rows:
        val: float = float(row.values[1].value)
        assert val < prev
        prev = val


def test_rows_sorted_on_percent(fixture_qts: QuoteTableState):
    columns: list[str] = ["change_percent"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    fixture_qts.load_config(config)
    # Make sure the quotes are loaded from an "external" source
    fixture_qts._load_quotes_internal(monotonic())

    fixture_qts.sort_column_key = "change_percent"
    assert fixture_qts.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = fixture_qts.get_quotes_rows()

    prev: float = -math.inf  # Init to a value below anything we can encounter

    for row in rows:
        assert row.values[1].value[-1] == "%"
        val: float = float(row.values[1].value[:-1])
        assert val > prev
        prev = val

    fixture_qts.sort_direction = SortDirection.DESCENDING

    rows = fixture_qts.get_quotes_rows()

    prev: float = math.inf  # Init to a value above anything we can encounter

    # The quotes are in reverse order now
    for row in rows:
        assert row.values[1].value[-1] == "%"
        val: float = float(row.values[1].value[:-1])
        assert val < prev
        prev = val


def test_rows_sorted_on_shrunken_int_and_equal_values(fixture_qts: QuoteTableState):
    columns: list[str] = ["market_cap"]
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: columns,
    }

    fixture_qts.load_config(config)
    # Make sure the quotes are loaded from an "external" source
    fixture_qts._load_quotes_internal(monotonic())

    fixture_qts.sort_column_key = "market_cap"
    assert fixture_qts.sort_direction == SortDirection.ASCENDING

    rows: list[QuoteRow] = fixture_qts.get_quotes_rows()

    prev: QuoteRow = rows[0]

    for row in rows[1:]:
        cmp: int = compare_shrunken_ints(prev.values[1].value, row.values[1].value)
        assert cmp <= 0
        if cmp == 0:
            # If the values are equals (N/A, most likely), it should then be sorted by
            # the ticker.
            # Note that we'er hardcoding the "lower" ticker, as it's the value used
            # for sorting in the ALL_QUOTES_COLUMNS definitions for the ticker.
            assert prev.values[0].value.lower() < row.values[0].value.lower()
        prev = row

    fixture_qts.sort_direction = SortDirection.DESCENDING

    rows = fixture_qts.get_quotes_rows()

    prev: QuoteRow = rows[0]

    for row in rows[1:]:
        cmp: int = compare_shrunken_ints(prev.values[1].value, row.values[1].value)
        assert cmp >= 0
        if cmp == 0:
            # See above
            assert prev.values[0].value.lower() > row.values[0].value.lower()
        prev = row


# TODO - add tests for the following:
# - add_column
# - remove_column
# - move_column
# - add_quote
# - remove_quote
# - current_row
# - thread_running (tricky... using mock?)
