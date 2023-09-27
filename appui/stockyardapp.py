import logging

from textual.app import App, ComposeResult
from textual.logging import TextualHandler
from textual.widgets import Footer

from ._quotetable import QuoteTable
from .stockyardappstate import StockyardAppState

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class StockyardApp(App):
    """A Textual app for the Stockyard application."""

    BINDINGS = [("q", "exit", "Exit")]

    def __init__(self, state: StockyardAppState) -> None:
        """Initialize the app."""
        super().__init__()
        self._state: StockyardAppState = state

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield QuoteTable(self._state.quote_table_state())
        yield Footer()

    def on_mount(self) -> None:
        """Handle mount events."""
        self.title = self._state.title

    def action_exit(self) -> None:
        """Handle exit actions."""
        self.exit()
