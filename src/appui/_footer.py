"""A simple footer with a clock, that can also have its bindings refreshed."""

from textual.app import ComposeResult
from textual.widgets import Footer as TextualFooter

from ._clock import Clock


class Footer(TextualFooter):
    """The footer for the stockyard app."""

    def __init__(self) -> None:
        """
        Initialize the footer.

        This initializes the footer with a clock.
        """

        super().__init__()
        self._clock: Clock = Clock()

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield self._clock
