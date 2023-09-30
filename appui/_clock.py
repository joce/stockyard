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

    time = reactive(datetime.now(timezone.utc).astimezone())

    def on_mount(self) -> None:
        """
        Event handler called when widget is added to the app.
        """
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        """
        Method to update the time to the current time.
        """
        self.time = datetime.now(timezone.utc).astimezone()

    def watch_time(self, time: datetime) -> None:
        """
        Called when the time attribute changes.
        """
        self.update(datetime.strftime(time, "%H:%M:%S %z"))
