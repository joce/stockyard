"""
A very simple and limited widget to display the current time.
"""
from datetime import datetime, timezone

from textual.reactive import reactive
from textual.widgets import Static


class Clock(Static):
    """
    A very simple and limited widget to display the current time.
    """

    dirty: reactive = reactive(1)

    def on_mount(self) -> None:
        """
        Event handler called when widget is added to the app.
        """
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        """
        Method to tick the clock update.
        """
        self.dirty = self.dirty + 1

    def watch_dirty(self, _: bool) -> None:
        """
        Called when the time needs to be updated.
        """
        self.update(
            datetime.strftime(datetime.now(timezone.utc).astimezone(), "%H:%M:%S")
        )
