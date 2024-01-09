"""The stockyard application"""

from __future__ import annotations

import json
import logging
import sys
from io import TextIOWrapper
from typing import Any, ClassVar, Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.css.query import NoMatches
from textual.logging import TextualHandler
from textual.widgets import LoadingIndicator
from textual.worker import Worker

from yfinance import YFinance

from ._footer import Footer
from ._quote_table import QuoteTable
from .stockyardapp_state import StockyardAppState

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class StockyardApp(App[None]):
    """A Textual app for the Stockyard application."""

    CSS_PATH = "./stockyardapp.tcss"

    ENABLE_COMMAND_PALETTE = False  # TODO: Consider enabling this

    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "exit", "Exit"),
    ]

    def __init__(self) -> None:
        """Initialize the app."""

        super().__init__()

        self.__yfinance: YFinance = YFinance()
        self._state: StockyardAppState = StockyardAppState(self.__yfinance)
        self._priming_worker: Optional[Worker[None]] = None

        # Widgets
        self._footer: Footer = Footer()

    @override
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()
        yield self._footer

    def on_unmount(self) -> None:
        """Handle unmount events."""

        if self._priming_worker is not None and self._priming_worker.is_running:
            self._priming_worker.cancel()

    def on_mount(self) -> None:
        """Handle mount events."""

        self._priming_worker = self._prime_yfinance()
        self.title = self._state.title

    def on_quote_table_bindings_changed(self) -> None:
        """Refresh the bindings for the app."""

        # One way of achieving the footer refresh is to just reset the focus to the
        # currently focused widget:
        #
        # focused: Optional[Widget] = self.focused
        # if focused is not None:
        #     self.set_focus(None)
        #     self.set_focus(focused)

        # Another way is to just refresh the footer...
        self._footer.refresh_bindings()

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
        # TODO once the config is loaded, we need to update the logging level and the
        # clock's time format

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

        try:
            indicator: LoadingIndicator = self.query_one(
                "LoadingIndicator", LoadingIndicator
            )
            indicator.remove()
        except NoMatches:
            # No indicator was found
            logging.exception("No loading indicator found")

        qt: QuoteTable = QuoteTable(self._state.quote_table_state)
        self.mount(qt, before="Footer")

        # Set the focus to the quote table
        qt.focus()

        self._priming_worker = None
