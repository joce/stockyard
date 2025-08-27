"""The symbol selector screen."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from textual.binding import BindingsMap
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList

from ._footer import Footer

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Mount

    from .stockyardapp_state import StockyardAppState

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class SelectorScreen(ModalScreen[None]):
    """The symbol selector screen with an input field for testing autocomplete."""

    def __init__(self, state: StockyardAppState) -> None:
        """Initialize the selector screen."""

        super().__init__()

        self._state: StockyardAppState = state
        self._bindings: BindingsMap = BindingsMap()

        # Widgets
        self._footer: Footer = Footer(self._state.time_format)
        self._input: Input = Input(
            placeholder="Type symbol (e.g., AAPL, MSFT)...", classes="symbol-input"
        )
        self._option_list: OptionList = OptionList(classes="autocomplete-options")

        # Bindings
        self._bindings.bind("escape", "exit", "Exit", key_display="Esc")

        self._bindings.bind("up", "navigate_up", show=False)
        self._bindings.bind("down", "navigate_down", show=False)
        self._bindings.bind("pageup", "navigate_pageup", show=False)
        self._bindings.bind("pagedown", "navigate_pagedown", show=False)

    @override
    def _on_mount(self, event: Mount) -> None:

        super()._on_mount(event)
        # Focus the input field when the screen is shown
        self._input.focus()

    @override
    def compose(self) -> ComposeResult:

        yield self._input
        yield self._option_list
        yield self._footer

    def _update_option_list(self, text: str) -> None:
        """Update the option list with substrings of the input text."""

        if not text:
            self._option_list.clear_options()
            return

        # Generate substrings: "Cursor" -> ["C", "Cu", "Cur", "Curs", "Curso", "Cursor"]
        substrings = [text[: i + 1] for i in range(len(text))]

        # Remember current selection before clearing
        current_selection = self._option_list.highlighted

        self._option_list.clear_options()
        self._option_list.add_options(substrings)

        # Restore selection if it was valid, otherwise select first item
        if current_selection is not None and current_selection < len(substrings):
            self._option_list.highlighted = current_selection

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handle input changes to update the option list.

        Args:
            event: The input changed event.
        """

        self._update_option_list(event.value)

    def on_input_submitted(self) -> None:
        """Handle enter key press."""

        self._option_list.action_select()

    def action_exit(self) -> None:
        """Handle exit action - pop the screen and return to watchlist."""

        self.app.pop_screen()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """
        Handle option list selection.

        Args:
            event: The option list selection event.
        """

        self.app.pop_screen()

    def action_navigate_up(self) -> None:
        """Navigate up in the option list."""

        self._option_list.action_cursor_up()

    def action_navigate_down(self) -> None:
        """Navigate down in the option list."""

        self._option_list.action_cursor_down()

    def action_navigate_pageup(self) -> None:
        """Navigate page up in the option list."""

        self._option_list.action_page_up()

    def action_navigate_pagedown(self) -> None:
        """Navigate page down in the option list."""

        self._option_list.action_page_down()
