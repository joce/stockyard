"""A very simple and limited widget to display the current time."""

from datetime import datetime

from textual.widgets import Static


class Clock(Static):
    """A very simple and limited widget to display the current time."""

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""

        # TODO Make the time display configurable through the config file (24h v. AM/PM)
        self.set_interval(
            1, lambda: self.update(datetime.now().time().strftime("%H:%M:%S"))
        )
