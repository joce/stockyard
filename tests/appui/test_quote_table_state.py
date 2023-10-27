# pylint: disable=protected-access
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

from typing import Any

import pytest

from appui.quote_table_state import QuoteTableState
from yfinance import YFinance


@pytest.fixture
def fixture_qts() -> QuoteTableState:
    yfin = YFinance()
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


def test_load_invalid_columns(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["truly_not_a_column", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_duplicate_columns(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "last", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == [QuoteTableState._TICKER_COLUMN_KEY, "last"]


def test_load_duplicate_mandatory_column(fixture_qts: QuoteTableState):
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


def test_load_invalid_sort_column(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._COLUMNS: ["last", "change_percent"],
        QuoteTableState._SORT_COLUMN: "truly_not_a_column",
    }
    fixture_qts.load_config(config)
    assert fixture_qts.sort_column_key == QuoteTableState._TICKER_COLUMN_KEY


def test_load_invalid_sort_direction(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._SORT_DIRECTION: "amazing",
    }
    fixture_qts.load_config(config)
    assert fixture_qts.sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION


def test_load_invalid_query_frequency(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        QuoteTableState._QUERY_FREQUENCY: 0,
    }
    fixture_qts.load_config(config)
    assert fixture_qts.query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_save_config_empty_dict(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}
    fixture_qts.save_config(config)

    # The first column, "ticker", is not saved
    assert config[QuoteTableState._COLUMNS] == fixture_qts._columns_keys[1:]
    assert config[QuoteTableState._SORT_COLUMN] == fixture_qts.sort_column_key
    assert config[QuoteTableState._SORT_DIRECTION] == fixture_qts.sort_direction.value
    assert config[QuoteTableState._QUOTES] == fixture_qts._quotes_symbols
    assert config[QuoteTableState._QUERY_FREQUENCY] == fixture_qts.query_frequency


def test_save_config_takes_list_copies(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}
    fixture_qts.save_config(config)
    config[QuoteTableState._COLUMNS][0] = "foo_foo"
    config[QuoteTableState._QUOTES][0] = "ZZZZ"
    assert config[QuoteTableState._COLUMNS] != fixture_qts._columns_keys
    assert config[QuoteTableState._QUOTES] != fixture_qts._quotes_symbols


def test_save_config_non_empty_dict(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {"dummy_key": "dummy_value"}
    with pytest.raises(ValueError):
        fixture_qts.save_config(config)


def test_round_trip_config(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}

    fixture_qts.save_config(config)

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


# TODO - add tests for the following:
# - add_column
# - remove_column
# - move_column
# - add_quote
# - remove_quote
# - get_quotes
# - current_row
# - sort_direction
# - sort_column_key
# - columns
# - thread_running (tricky... using mock?)
