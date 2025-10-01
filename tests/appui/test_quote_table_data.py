"""Tests for quote table data structures."""

from __future__ import annotations

from appui.enhanced_data_table import EnhancedColumn


def test_quote_column_defaults_key_to_label() -> None:
    """QuoteColumn uses the label as key when none is provided."""

    column = EnhancedColumn[int]("Label")

    assert column.key == "Label"


def test_quote_column_keeps_explicit_key() -> None:
    """QuoteColumn keeps an explicitly provided key."""

    column = EnhancedColumn[int]("Label", key="custom")

    assert column.key == "custom"
