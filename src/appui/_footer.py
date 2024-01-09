"""A simple footer with a clock, that can also have its bindings refreshed."""

from textual.app import ComposeResult
from textual.widgets import Footer as TextualFooter

from ._clock import Clock


class Footer(TextualFooter):
    """
    The footer for the stockyard app.

    This is required to be able to call the `refresh_bindings` method without
    triggering pyright errors.
    """

    def __init__(self) -> None:
        super().__init__()
        self._clock: Clock = Clock()

    def compose(self) -> ComposeResult:
        yield self._clock

    def refresh_bindings(self) -> None:
        """Expose the binding refresh for the footer."""

        self._bindings_changed(None)
