"""A very simple and limited widget to display the current time."""

from datetime import datetime, timezone
from time import time

from textual.widgets import Static


class Clock(Static):
    """A very simple and limited widget to display the current time."""

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""

        # TODO Make the time display configurable through the config file (24h v. AM/PM)
        self._show_time()
        self._schedule_next_update()

    def _schedule_next_update(self) -> None:
        """Schedule the next update to occur at the next second boundary."""

        # Calculate time until next second boundary
        now = time()
        next_second = int(now) + 1
        delay = next_second - now

        # Schedule the update
        self.set_timer(delay, self._show_time_and_reschedule)

    def _show_time_and_reschedule(self) -> None:
        """Update the time and schedule the next update."""

        self._show_time()
        self._schedule_next_update()

    def _show_time(self) -> None:
        """Update the time displayed by the widget."""

        self.update(datetime.now(timezone.utc).astimezone().time().strftime("%H:%M:%S"))
