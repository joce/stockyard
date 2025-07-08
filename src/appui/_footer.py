"""A simple footer with a clock."""

from textual.app import ComposeResult
from textual.widgets import Footer as TextualFooter

from ._clock import Clock
from ._enums import TimeFormat


class Footer(TextualFooter):
    """The footer for the stockyard app."""

    def __init__(self, time_format: TimeFormat) -> None:
        """
        Initialize the footer.

        This initializes the footer with a clock.
        """

        super().__init__()
        self._clock: Clock = Clock(time_format)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield self._clock
