"""Tests for quote table factories."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.text import Text

from appui._enums import Justify
from appui._quote_table import quote_column, quote_table
from appui.enhanced_data_table import EnhancedColumn, EnhancedDataTable

if TYPE_CHECKING:
    from yfinance import YQuote


def test_quote_column_factory_uses_default_behavior() -> None:
    """Factory returns EnhancedColumn with sensible defaults."""

    column = quote_column("Label")

    assert isinstance(column, EnhancedColumn)
    assert column.label == "Label"
    assert column.key == "Label"


def test_quote_column_factory_applies_overrides() -> None:
    """Factory respects keyword overrides."""

    def formatter(q: YQuote) -> Text:
        return Text(str(q))

    def sorter(q: YQuote) -> str:
        return q.exchange

    test_width = 8

    column = quote_column(
        "Ticker",
        width=test_width,
        key="ticker",
        justification=Justify.LEFT,
        cell_format_func=formatter,
        sort_key_func=sorter,
    )

    assert column.width == test_width
    assert column.key == "ticker"
    assert column.justification is Justify.LEFT
    assert column.cell_format_func is formatter
    assert column.sort_key_func is sorter


def test_quote_table_factory_returns_enhanced_data_table() -> None:
    """Factory instantiates EnhancedDataTable specialized for quotes."""

    table = quote_table()

    assert isinstance(table, EnhancedDataTable)
