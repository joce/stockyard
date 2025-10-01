"""Define data structures for managing and displaying quote tables in the app's UI.

Contains the core classes QuoteCell, QuoteRow, and QuoteColumn that together form the
building blocks of a quote table's structure and behavior.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import Any, Callable

from rich.text import Text

from ._enums import Justify

# @dataclass(frozen=True)
# class QuoteCell:
#     """Definition of a cell for the quote table."""

#     value: str
#     """The value to display."""

#     sign: int
#     """The sign of the value, i.e. negative (-1), positive (1) or neutral (0)."""

#     justify: Justify
#     """The justification of the text in the cell."""


@dataclass(frozen=True)
class QuoteRow:
    """Definition of row for the quote table."""

    key: str
    """The key of the row."""

    values: list[Text]
    """The values of the row."""


@dataclass(frozen=True)
class QuoteColumn:
    """Represents a quote table column and defines its display properties and behaviors.

    Contains settings for the column's appearance (label, width, justification) and
    behavior (formatting, sorting, and sign indication).
    """

    label: str
    """The label of the column."""

    _: KW_ONLY

    width: int = 10
    """The width of the column."""

    key: str = None  # pyright: ignore[reportAssignmentType]
    """The key of the column, defaults to the label if omitted."""

    justification: Justify = Justify.RIGHT
    """Text justification for the column."""

    format_func: Callable[[Any], Text] = lambda _: Text()
    """The function used to format the column."""

    sort_key_func: Callable[[Any], Any] = lambda _: 0
    """The function used to provide the sort key for the column."""

    def __post_init__(self) -> None:
        """Ensure the column key defaults to the label when omitted."""

        object.__setattr__(
            self,
            "key",
            (
                self.label
                if self.key is None  # pyright: ignore[reportUnnecessaryComparison]
                else self.key
            ),
        )
