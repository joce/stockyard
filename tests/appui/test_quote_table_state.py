# pylint: disable=protected-access
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import pytest

from appui._enums import SortDirection
from appui.quote_table_state import QuoteTableState
from yfinance import YFinance


@pytest.fixture
def setup():
    yfin = YFinance()
    qts = QuoteTableState(yfin)
    return qts


def test_load_regular_config(setup):
    qts = setup
    config = {
        "columns": ["ticker", "last", "change_percent"],
        "sort_column": "last",
        "sort_direction": "ASCENDING",
        "quotes": ["AAPL", "F", "VT"],
        "query_frequency": 15,
    }
    qts.load_config(config)
    assert qts._columns_keys == config["columns"]
    assert qts._sort_column_key == config["sort_column"]
    assert qts._sort_direction.name == config["sort_direction"]
    assert qts._quotes_symbols == config["quotes"]
    assert qts._query_frequency == config["query_frequency"]


def test_load_empty_config(setup):
    qts = setup
    config = {}
    qts.load_config(config)
    assert qts._columns_keys == QuoteTableState._DEFAULT_COLUMN_KEYS
    assert qts._sort_column_key == QuoteTableState._DEFAULT_COLUMN_KEYS[0]
    assert qts._sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION
    assert qts._quotes_symbols == QuoteTableState._DEFAULT_QUOTES
    assert qts._query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY


def test_load_invalid_columns(setup):
    qts = setup
    config = {
        "columns": ["ticker", "truly_not_a_column", "last"],
    }
    qts.load_config(config)
    assert qts._columns_keys == ["ticker", "last"]


def test_load_invalid_sort_column(setup):
    qts = setup
    config = {
        "columns": ["ticker", "last", "change_percent"],
        "sort_column": "truly_not_a_column",
    }
    qts.load_config(config)
    assert qts._sort_column_key == "ticker"


def test_load_invalid_sort_direction(setup):
    qts = setup
    config = {
        "sort_direction": "AMAZING",
    }
    qts.load_config(config)
    assert qts._sort_direction == QuoteTableState._DEFAULT_SORT_DIRECTION


def test_load_alternate_sort_direction(setup):
    qts = setup
    config = {
        "sort_direction": "DESC",
    }
    qts.load_config(config)
    assert qts._sort_direction == SortDirection.DESCENDING


def test_load_invalid_query_frequency(setup):
    qts = setup
    config = {
        "query_frequency": 0,
    }
    qts.load_config(config)
    assert qts._query_frequency == QuoteTableState._DEFAULT_QUERY_FREQUENCY
