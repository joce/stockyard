import logging

from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.logging import TextualHandler
from textual.widgets import Footer

from ._quotetable import QuoteTable
from .stockyardapp_state import StockyardAppState

# import threading
# import time


logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class StockyardApp(App):
    """A Textual app for the Stockyard application."""

    BINDINGS: list[BindingType] = [("q", "exit", "Exit")]

    def __init__(self, state: StockyardAppState) -> None:
        """Initialize the app."""
        super().__init__()
        self._state: StockyardAppState = state

        # self._counter: int = 0
        # self._run_counter: bool = True
        # self._count_thread: threading.Thread = threading.Thread(
        #     target=self.increment_counter
        # )

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield QuoteTable(self._state.quote_table_state())
        yield Footer()

    def on_mount(self) -> None:
        """Handle mount events."""
        self.title = self._state.title
        # self._count_thread.start()

    # def increment_counter(self) -> None:
    #     while self._run_counter:
    #         self._counter += 1
    #         lbl: Label = self.query_one("#counter", Label)
    #         self.call_from_thread(lbl.update, str(self._counter))
    #         time.sleep(1)

    def action_exit(self) -> None:
        """Handle exit actions."""
        # self._run_counter = False
        # self._count_thread.join()
        self.exit()
