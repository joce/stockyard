"""The stockyard application"""

import json
import logging
from io import TextIOWrapper
from typing import Any, Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal
from textual.logging import TextualHandler
from textual.widgets import Footer, LoadingIndicator
from textual.worker import Worker

from yfinance import YFinance

from ._clock import Clock
from ._quote_table import QuoteTable
from .stockyardapp_state import StockyardAppState

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class StockyardApp(App):
    """A Textual app for the Stockyard application."""

    CSS_PATH = "./stockyardapp.tcss"

    BINDINGS: list[BindingType] = [
        ("q", "exit", "Exit"),
    ]

    def __init__(self) -> None:
        """Initialize the app."""

        super().__init__()

        self.__yfinance: YFinance = YFinance()
        self._state: StockyardAppState = StockyardAppState(self.__yfinance)
        self._priming_worker: Optional[Worker[None]] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield LoadingIndicator()
        yield Horizontal(Footer(), Clock(), id="clock-footer")

    def on_unmount(self) -> None:
        """Handle unmount events."""

        if self._priming_worker is not None and self._priming_worker.is_running:
            self._priming_worker.cancel()

    def on_mount(self) -> None:
        """Handle mount events."""

        self._priming_worker = self._prime_yfinance()
        self.title = self._state.title

    def action_exit(self) -> None:
        """Handle exit actions."""

        self.exit()

    def load_config(self, path: str) -> None:
        """Load the configuration for the app."""

        try:
            f: TextIOWrapper
            with open(path, "r", encoding="utf-8") as f:
                config: dict[str, Any] = json.load(f)
                self._state.load_config(config)
        except FileNotFoundError:
            logging.error("load_config: Config file not found: %s", path)
        except json.JSONDecodeError as e:
            logging.error(
                "load_config: error decoding JSON file: %s [%d, %d]: %s",
                path,
                e.lineno,
                e.colno,
                e.msg,
            )

    def save_config(self, path: str) -> None:
        """Save the configuration for the app."""

        try:
            f: TextIOWrapper
            with open(path, "w", encoding="utf-8") as f:
                config: dict[str, Any] = self._state.save_config()
                json.dump(config, f, indent=4)
        except FileNotFoundError:
            logging.error("save_config: Config file not found: %s", path)
        except PermissionError:
            logging.error("save_config: Permission denied: %s", path)

    @work(exclusive=True, thread=True)
    def _prime_yfinance(self) -> None:
        """Prime the YFinance client."""

        self.__yfinance.prime()
        if self._priming_worker is not None and not self._priming_worker.is_cancelled:
            self.call_from_thread(self._finish_loading)

    def _finish_loading(self) -> None:
        """Finish loading."""

        indicator: LoadingIndicator = self.query_one(
            "LoadingIndicator", LoadingIndicator
        )
        if indicator is not None:
            indicator.remove()

        qt: QuoteTable = QuoteTable(self._state.quote_table_state)
        self.mount(qt, before="#clock-footer")

        # Set the focus to the quote table
        qt.focus()

        self._priming_worker = None
