# pylint: disable=protected-access
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

from typing import Any

import pytest

from appui._enums import SortDirection
from appui.quote_table_state import QuoteTableState
from yfinance import YFinance


@pytest.fixture
def fixture_qts() -> QuoteTableState:
    yfin = YFinance()
    qts = QuoteTableState(yfin)
    return qts


def test_load_regular_config(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        "columns": ["ticker", "last", "change_percent"],
        "sort_column": "last",
        "sort_direction": "ASCENDING",
        "quotes": ["AAPL", "F", "VT"],
        "query_frequency": 15,
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == config["columns"]
    assert fixture_qts._sort_column_key == config["sort_column"]
    assert fixture_qts._sort_direction.name == config["sort_direction"]
    assert fixture_qts._quotes_symbols == config["quotes"]
    assert fixture_qts._query_frequency == config["query_frequency"]


def test_load_empty_config(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == QuoteTableState._DEFAULT_COLUMN_KEYS
    assert fixture_qts._sort_column_key == QuoteTableState._DEFAULT_COLUMN_KEYS[0]
    assert fixture_qts._sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION
    assert fixture_qts._quotes_symbols == QuoteTableState._DEFAULT_QUOTES
    assert fixture_qts._query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_invalid_columns(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        "columns": ["ticker", "truly_not_a_column", "last"],
    }
    fixture_qts.load_config(config)
    assert fixture_qts._columns_keys == ["ticker", "last"]


def test_load_invalid_sort_column(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        "columns": ["ticker", "last", "change_percent"],
        "sort_column": "truly_not_a_column",
    }
    fixture_qts.load_config(config)
    assert fixture_qts._sort_column_key == "ticker"


def test_load_invalid_sort_direction(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        "sort_direction": "AMAZING",
    }
    fixture_qts.load_config(config)
    assert fixture_qts._sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION


def test_load_alternate_sort_direction(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        "sort_direction": "DESC",
    }
    fixture_qts.load_config(config)
    assert fixture_qts._sort_direction == SortDirection.DESCENDING


def test_load_invalid_query_frequency(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {
        "query_frequency": 0,
    }
    fixture_qts.load_config(config)
    assert fixture_qts._query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_save_config_empty_dict(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}
    fixture_qts.save_config(config)
    assert config["columns_keys"] == fixture_qts._columns_keys
    assert config["sort_column_key"] == fixture_qts._sort_column_key
    assert config["sort_direction"] == fixture_qts._sort_direction.name
    assert config["quotes_symbols"] == fixture_qts._quotes_symbols
    assert config["query_frequency"] == fixture_qts._query_frequency


def test_save_config_takes_list_copies(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {}
    fixture_qts.save_config(config)
    config["columns_keys"][0] = "foo_foo"
    config["quotes_symbols"][0] = "ZZZZ"
    assert config["columns_keys"] != fixture_qts._columns_keys
    assert config["quotes_symbols"] != fixture_qts._quotes_symbols


def test_save_config_non_empty_dict(fixture_qts: QuoteTableState):
    config: dict[str, Any] = {"dummy_key": "dummy_value"}
    with pytest.raises(ValueError):
        fixture_qts.save_config(config)
