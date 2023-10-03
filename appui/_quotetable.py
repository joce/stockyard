from rich.text import Text
from textual.widgets import DataTable

from ._column import Column
from .quotetable_state import QuoteTableState


class QuoteTable(DataTable):
    """
    A DataTable for displaying quotes
    """

    def __init__(self, state: QuoteTableState) -> None:
        super().__init__()
        self._state: QuoteTableState = state
        self._version: int

    def on_mount(self) -> None:
        """
        The event handler called when the widget is added to the app
        """
        super().on_mount()
        column: Column
        for column in self._state.columns:
            # TODO Unsure if we put this here on in the state.
            styled_column: Text = Text(column.name, justify=column.justification.value)
            self.add_column(styled_column, width=column.width, key=column.key)

        self.cursor_type = "row"
        self.zebra_stripes = True
        self.set_interval(1, self._update_table)

        self._version = self._state.version - 1
        self._state.query_thread_running = True

    def _on_unmount(self) -> None:
        self._state.query_thread_running = False
        super()._on_unmount()

    def _update_table(self) -> None:
        if self._version == self._state.version:
            return

        quote: list[str]
        self.clear()  # suboptimal. We need to actually update the table
        for quote in self._state.get_quotes():
            # TODO This is certainly suboptimal to have to zip the quote and the columns together every time.
            stylized_row: list[Text] = [
                Text(cell, justify=column.justification.value)
                for cell, column in zip(quote, self._state.columns)
            ]
            self.add_row(*stylized_row)
