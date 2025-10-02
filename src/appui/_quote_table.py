"""A data table widget to display and manipulate financial quotes."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable

from yfinance import YQuote

from .enhanced_data_table import EnhancedColumn, EnhancedDataTable

if TYPE_CHECKING:
    from rich.text import Text

    from ._enums import Justify

if sys.version_info >= (3, 12):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

QuoteColumn: TypeAlias = EnhancedColumn[YQuote]
QuoteTable: TypeAlias = EnhancedDataTable[YQuote]


def quote_table() -> QuoteTable:
    """Create a QuoteTable.

    Returns:
        QuoteTable: An EnhancedDataTable specialized for YQuote.
    """

    return EnhancedDataTable[YQuote]()


def quote_column(  # noqa: PLR0913
    # pylint: disable=unused-argument
    label: str,
    *,
    key: str | None = None,
    width: int | None = None,
    justification: Justify | None = None,
    cell_format_func: Callable[[YQuote], Text] | None = None,
    sort_key_func: Callable[[YQuote], object] | None = None,
    # pylint: enable=unused-argument
) -> QuoteColumn:
    """Create a QuoteColumn.

    Args:
        label (str): The display label for the column.
        key (str | None): The key to access the attribute in YQuote.
            Defaults to None, which uses the label as the key.
        width (int | None): The width of the column.
        justification (Justify | None): The text justification for the column.
        cell_format_func (Callable[[YQuote], Text] | None): A custom function
            to format the cell content.
        sort_key_func (Callable[[YQuote], object] | None): A custom function
            to determine the sort key for the column.

    Returns:
        QuoteColumn: An EnhancedColumn specialized for YQuote.
    """

    params = locals().copy()
    params.pop("label")
    return EnhancedColumn[YQuote](label, **params)
