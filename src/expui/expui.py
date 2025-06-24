"""The stockyard experimental application."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, ClassVar

from textual.app import App, ComposeResult
from textual.logging import TextualHandler
from textual.widgets import Footer

from .button_screen import ButtonScreen

if TYPE_CHECKING:
    from textual.binding import BindingType

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

logging.basicConfig(
    level=logging.NOTSET,
    handlers=[TextualHandler()],
)
logging.getLogger("asyncio").setLevel(logging.ERROR)


class ExpUI(App[None]):
    """An experimental Textual app for the Stockyard application."""

    CSS_PATH = "./expui.tcss"

    ENABLE_COMMAND_PALETTE = False  # TODO: Consider enabling this

    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "exit", "Exit"),
        ("b", "button_screen", "Button Screen"),
    ]

    def __init__(self) -> None:
        """Initialize the main application components and state management."""

        super().__init__()

        # Widgets
        self._footer: Footer = Footer()

    def on_mount(self) -> None:
        """Mount the application components."""
        self.install_screen(ButtonScreen(), name="button_screen")  # type: ignore[no-untyped-call]

    @override
    def compose(self) -> ComposeResult:
        yield self._footer

    def action_exit(self) -> None:
        """Handle exit actions."""

        self.exit()

    def action_button_screen(self) -> None:
        """Handle button screen actions."""
        self.push_screen("button_screen")
