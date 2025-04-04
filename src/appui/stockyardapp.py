"""The stockyard application."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from textual import work
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.logging import TextualHandler
from textual.widgets import LoadingIndicator

from yfinance import YFinance

from ._footer import Footer
from ._quote_table import QuoteTable
from .stockyardapp_state import StockyardAppState

if TYPE_CHECKING:
    from io import TextIOWrapper

    from textual.binding import BindingType
    from textual.worker import Worker

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

logging.basicConfig(
    level=logging.NOTSET,
    handlers=[TextualHandler()],
)
logging.getLogger("asyncio").setLevel(logging.ERROR)


class StockyardApp(App[None]):
    """A Textual app for the Stockyard application."""

    CSS_PATH = "./stockyardapp.tcss"

    ENABLE_COMMAND_PALETTE = False  # TODO: Consider enabling this

    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "exit", "Exit"),
    ]

    def __init__(self) -> None:
        """Initialize the main application components and state management."""

        super().__init__()

        self.__yfinance: YFinance = YFinance()
        self._state: StockyardAppState = StockyardAppState(self.__yfinance)
        self._priming_worker: Worker[None] | None = None

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

        self._footer.refresh_bindings()

    def action_exit(self) -> None:
        """Handle exit actions."""

        self.exit()

    def load_config(self, path: str) -> None:
        """Load the configuration for the app."""

        logger = logging.getLogger(__name__)
        try:
            f: TextIOWrapper
            with Path(path).open(encoding="utf-8") as f:
                config: dict[str, Any] = json.load(f)
                self._state.load_config(config)
        except FileNotFoundError:
            logger.warning("load_config: Config file not found: %s", path)
        except json.JSONDecodeError as e:
            logger.exception(
                "load_config: error decoding JSON file: %s [%d, %d]: %s",
                path,
                e.lineno,
                e.colno,
                e.msg,
            )

        # TODO once the config is loaded, we need to update the logging level and the
        # clock's time format

        # TODO: asyncio's logging needs to be set as the same level as the app's

    def save_config(self, path: str) -> None:
        """Save the configuration for the app."""

        logger = logging.getLogger(__name__)
        try:
            f: TextIOWrapper
            with Path(path).open("w", encoding="utf-8") as f:
                config: dict[str, Any] = self._state.save_config()
                json.dump(config, f, indent=4)
        except FileNotFoundError:
            logger.exception("save_config: Config file not found: %s", path)
        except PermissionError:
            logger.exception("save_config: Permission denied: %s", path)

    @work(exclusive=True, thread=True)
    def _prime_yfinance(self) -> None:
        """Prime the YFinance client."""

        self.__yfinance.prime()
        if self._priming_worker is not None and not self._priming_worker.is_cancelled:
            self.call_from_thread(self._finish_loading)

    def _finish_loading(self) -> None:
        """Finish loading."""

        logger = logging.getLogger(__name__)
        try:
            indicator: LoadingIndicator = self.query_one(
                "LoadingIndicator", LoadingIndicator
            )
            indicator.remove()
        except NoMatches:
            # No indicator was found
            logger.exception("No loading indicator found")

        qt: QuoteTable = QuoteTable(self._state.quote_table_state)
        self.mount(qt, before="Footer")

        # Set the focus to the quote table
        qt.focus()

        self._priming_worker = None
        self._priming_worker = None
