"""The stock watchlist screen."""

from __future__ import annotations

import sys
from enum import Enum
from typing import TYPE_CHECKING

from textual.binding import BindingsMap
from textual.message import Message
from textual.screen import Screen

from ._footer import Footer
from ._quote_table import QuoteTable

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from .stockyardapp_state import StockyardAppState

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class Watchlist(Screen[None]):
    """The watchlist screen."""

    class BindingsChanged(Message):
        """A message sent when the bindings have changed."""

    class BM(Enum):
        """The binding mode enum for the quote table."""

        DEFAULT = "default"
        WITH_DELETE = "with_delete"
        IN_ORDERING = "in_ordering"

    def __init__(self, state: StockyardAppState) -> None:
        """Initialize the watchlist screen."""

        super().__init__()

        # TODO Maybe have a different state for the watchlist?
        self._state: StockyardAppState = state
        self._bindings: BindingsMap = BindingsMap()

        # Widgets
        self._footer: Footer = Footer(self._state.time_format)
        self._quote_table: QuoteTable = QuoteTable(self._state.quote_table_state)

    @override
    def compose(self) -> ComposeResult:
        yield self._quote_table
        yield self._footer

    def on_quote_table_bindings_changed(self) -> None:
        """Refresh the bindings for the app."""

        self._footer.refresh_bindings()
