# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=protected-access

# pyright: reportPrivateUsage=none

from __future__ import annotations

import logging
from typing import Any

import pytest

from appui.quote_table_state import QuoteTableState
from appui.stockyardapp_state import StockyardAppState
from yfinance import YFinance


@pytest.fixture(name="stockyard_app_state")
def fixture_sas() -> StockyardAppState:
    yfin = YFinance()
    sas = StockyardAppState(yfin)
    return sas


def test_load_regular_config(stockyard_app_state: StockyardAppState):
    config: dict[str, Any] = {
        StockyardAppState._QUOTE_TABLE: {
            QuoteTableState._COLUMNS: ["ticker", "last", "change_percent"],
            QuoteTableState._SORT_COLUMN: "last",
            QuoteTableState._SORT_DIRECTION: "asc",
            QuoteTableState._QUOTES: ["AAPL", "F", "VT"],
            QuoteTableState._QUERY_FREQUENCY: 15,
        },
        StockyardAppState._TIME_FORMAT: "12h",
        StockyardAppState._LOG_LEVEL: "warning",
    }
    stockyard_app_state.load_config(config)

    assert (
        stockyard_app_state.quote_table_state.column_keys
        == config[StockyardAppState._QUOTE_TABLE][QuoteTableState._COLUMNS]
    )
    assert (
        stockyard_app_state.quote_table_state.sort_column_key
        == config[StockyardAppState._QUOTE_TABLE][QuoteTableState._SORT_COLUMN]
    )
    assert (
        stockyard_app_state.quote_table_state.sort_direction.value
        == config[StockyardAppState._QUOTE_TABLE][QuoteTableState._SORT_DIRECTION]
    )
    assert (
        stockyard_app_state.quote_table_state._quotes_symbols
        == config[StockyardAppState._QUOTE_TABLE][QuoteTableState._QUOTES]
    )
    assert (
        stockyard_app_state.quote_table_state.query_frequency
        == config[StockyardAppState._QUOTE_TABLE][QuoteTableState._QUERY_FREQUENCY]
    )
    assert (
        stockyard_app_state._time_display.value
        == config[StockyardAppState._TIME_FORMAT]
    )
    assert (
        stockyard_app_state._log_level
        == logging.__dict__[config[StockyardAppState._LOG_LEVEL].upper()]
    )


def test_load_empty_config(stockyard_app_state: StockyardAppState):
    config: dict[str, Any] = {}
    stockyard_app_state.load_config(config)
    assert (
        stockyard_app_state.quote_table_state.column_keys
        == [QuoteTableState._TICKER_COLUMN_KEY] + QuoteTableState._DEFAULT_COLUMN_KEYS
    )
    assert (
        stockyard_app_state.quote_table_state.sort_column_key
        == QuoteTableState._TICKER_COLUMN_KEY
    )
    assert (
        stockyard_app_state.quote_table_state.sort_direction
        == QuoteTableState._DEFAULT_SORT_DIRECTION
    )
    assert (
        stockyard_app_state.quote_table_state._quotes_symbols
        == QuoteTableState._DEFAULT_QUOTES
    )
    assert (
        stockyard_app_state.quote_table_state.query_frequency
        == QuoteTableState._DEFAULT_QUERY_FREQUENCY
    )
    assert stockyard_app_state._time_display == StockyardAppState._DEFAULT_TIME_FORMAT
    assert stockyard_app_state._log_level == StockyardAppState._DEFAULT_LOG_LEVEL


def test_load_config_invalid_time_display(stockyard_app_state: StockyardAppState):
    config: dict[str, Any] = {
        StockyardAppState._TIME_FORMAT: "1000000h",
    }
    stockyard_app_state.load_config(config)
    assert stockyard_app_state._time_display == StockyardAppState._DEFAULT_TIME_FORMAT


def test_load_config_invalid_lof_level(stockyard_app_state: StockyardAppState):
    config: dict[str, Any] = {
        StockyardAppState._LOG_LEVEL: "fishy",
    }
    stockyard_app_state.load_config(config)
    assert stockyard_app_state._log_level == StockyardAppState._DEFAULT_LOG_LEVEL


def test_save_config(stockyard_app_state: StockyardAppState):
    config: dict[str, Any] = stockyard_app_state.save_config()
    assert [QuoteTableState._TICKER_COLUMN_KEY] + config[
        StockyardAppState._QUOTE_TABLE
    ][QuoteTableState._COLUMNS] == stockyard_app_state.quote_table_state.column_keys
    assert (
        config[StockyardAppState._QUOTE_TABLE][QuoteTableState._SORT_COLUMN]
        == stockyard_app_state.quote_table_state.sort_column_key
    )
    assert (
        config[StockyardAppState._QUOTE_TABLE][QuoteTableState._SORT_DIRECTION]
        == stockyard_app_state.quote_table_state.sort_direction.value
    )
    assert (
        config[StockyardAppState._QUOTE_TABLE][QuoteTableState._QUOTES]
        == stockyard_app_state.quote_table_state._quotes_symbols
    )
    assert (
        config[StockyardAppState._QUOTE_TABLE][QuoteTableState._QUERY_FREQUENCY]
        == stockyard_app_state.quote_table_state.query_frequency
    )
    assert (
        config[StockyardAppState._TIME_FORMAT]
        == stockyard_app_state._time_display.value
    )
    assert (
        logging.__dict__[config[StockyardAppState._LOG_LEVEL]]
        == stockyard_app_state._log_level
    )


def test_round_trip_config(stockyard_app_state: StockyardAppState):
    config: dict[str, Any] = stockyard_app_state.save_config()
    assert (
        config[StockyardAppState._TIME_FORMAT]
        == stockyard_app_state._time_display.value
    )
    assert (
        logging.__dict__[config[StockyardAppState._LOG_LEVEL]]
        == stockyard_app_state._log_level
    )

    config.clear()
    config[StockyardAppState._TIME_FORMAT] = "12h"
    config[StockyardAppState._LOG_LEVEL] = "critical"

    stockyard_app_state.load_config(config)
    assert (
        stockyard_app_state._time_display.value
        == config[StockyardAppState._TIME_FORMAT]
    )
    assert (
        stockyard_app_state._log_level
        == logging.__dict__[config[StockyardAppState._LOG_LEVEL].upper()]
    )
