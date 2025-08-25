"""The stock watchlist screen."""

from __future__ import annotations

import sys
from enum import Enum
from typing import TYPE_CHECKING

from textual.binding import BindingsMap
from textual.screen import Screen

from ._footer import Footer
from ._quote_table import QuoteTable
from ._selector_screen import SelectorScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Mount

    from .stockyardapp_state import StockyardAppState

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class WatchlistScreen(Screen[None]):
    """The watchlist screen."""

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
        self._current_bindings: WatchlistScreen.BM = WatchlistScreen.BM.IN_ORDERING

        # Widgets
        self._footer: Footer = Footer(self._state.time_format)
        self._quote_table: QuoteTable = QuoteTable(self._state.quote_table_state)

        # Bindings
        self._bindings_modes: dict[WatchlistScreen.BM, BindingsMap] = {
            WatchlistScreen.BM.DEFAULT: BindingsMap(),
            WatchlistScreen.BM.IN_ORDERING: BindingsMap(),
        }

        self._bindings_modes[WatchlistScreen.BM.DEFAULT].bind("q", "exit", "Exit")
        self._bindings_modes[WatchlistScreen.BM.DEFAULT].bind(
            "o", "order_quotes", "Change sort order"
        )
        self._bindings_modes[WatchlistScreen.BM.DEFAULT].bind(
            "insert", "add_quote", "Add quote", key_display="ins"
        )

        # For Delete, we want the same bindings as default, plus delete
        self._bindings_modes[WatchlistScreen.BM.WITH_DELETE] = self._bindings_modes[
            WatchlistScreen.BM.DEFAULT
        ].copy()
        self._bindings_modes[WatchlistScreen.BM.WITH_DELETE].bind(
            "delete", "remove_quote", "Remove quote", key_display="del"
        )

        # For Ordering, we want to drop all default binding. No add / delete, or cursor
        # movement.
        self._bindings_modes[WatchlistScreen.BM.IN_ORDERING].bind(
            "escape", "exit_ordering", "Done", key_display="Esc"
        )

        self._switch_bindings(WatchlistScreen.BM.DEFAULT)

    @override
    def _on_mount(self, event: Mount) -> None:
        super()._on_mount(event)

        self._switch_bindings(WatchlistScreen.BM.DEFAULT)

        self._bindings = self._bindings_modes[self._current_bindings]

    @override
    def compose(self) -> ComposeResult:
        yield self._quote_table
        yield self._footer

    def _switch_bindings(self, mode: WatchlistScreen.BM) -> None:
        """
        Switch the bindings to the given mode.

        Args:
            mode (Watchlist.BM): The mode to switch to.
        """

        if (
            mode == WatchlistScreen.BM.DEFAULT
            and len(self._state.quote_table_state.quotes_symbols) > 0
        ):
            mode = WatchlistScreen.BM.WITH_DELETE

        if self._current_bindings == mode:
            return
        self._current_bindings = mode
        self._bindings = self._bindings_modes[self._current_bindings]
        self._footer.refresh_bindings()

    def action_add_quote(self) -> None:
        """Add a new quote to the table."""

        self.app.push_screen(SelectorScreen(self._state))

    def action_remove_quote(self) -> None:
        """Remove the selected quote from the table."""

        self._quote_table.remove_quote(-1)
        self._switch_bindings(WatchlistScreen.BM.DEFAULT)

    def action_order_quotes(self) -> None:
        """Order the quotes in the table."""

        self._quote_table.is_ordering = True
        self._switch_bindings(WatchlistScreen.BM.IN_ORDERING)

    def action_exit_ordering(self) -> None:
        """Exit the ordering mode."""

        self._quote_table.is_ordering = False
        self._switch_bindings(WatchlistScreen.BM.DEFAULT)

    def action_exit(self) -> None:
        """Handle exit actions."""

        self.app.exit()
