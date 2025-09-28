"""Messages for StockyardApp."""

from textual.message import Message

from ._enums import SortDirection


# App messages
class AppExit(Message):
    """Message to request the app to exit."""


# Widget messages
class TableSortingChanged(Message):
    """Message to indicate that the table sorting has changed."""

    def __init__(self, column_key: str, direction: SortDirection) -> None:
        """Initialize the TableSortingChanged message.

        Args:
            sender (object): The sender of the message.
            column_key (key): The key of the column that is now sorted.
            direction (SortDirection): The direction of the sort.
        """

        super().__init__()
        self.column_key: str = column_key
        self.direction: SortDirection = direction
