import logging

from rich.text import Text
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from ._enums import SortDirection
from ._quote_column import QuoteColumn
from .quote_table_state import QuoteTableState


class QuoteTable(DataTable):
    """A DataTable for displaying quotes."""

    def __init__(self, state: QuoteTableState) -> None:
        super().__init__()
        self._state: QuoteTableState = state
        self._version: int

    def on_mount(self) -> None:
        """The event handler called when the widget is added to the app."""

        super().on_mount()
        column: QuoteColumn
        for column in self._state.columns:
            column_title: str = column.name
            if column.key == self._state.sort_column_key:
                if self._state.sort_direction == SortDirection.ASCENDING:
                    column_title = column_title[: column.width - 2] + " ▼"
                else:
                    column_title = column_title[: column.width - 2] + " ▲"

            styled_column: Text = Text(column_title, justify=column.justification.value)
            self.add_column(styled_column, width=column.width, key=column.key)

        self.cursor_type = "row"
        self.zebra_stripes = True
        self.set_interval(1, self._update_table)

        self._version = self._state.version - 1
        self._state.query_thread_running = True

    def _on_unmount(self) -> None:
        """
        The event handler called when the widget is added to the app.

        Required to stop the query thread.
        """

        self._state.query_thread_running = False
        super()._on_unmount()

    def _update_table(self) -> None:
        """Update the table with the latest quotes (if any)"""

        if self._version == self._state.version:
            return

        existing_rows: list[str] = [r.value if r.value else "" for r in self.rows]

        for quote in self._state.get_quotes():
            # update existing rows,
            if quote.key in self.rows:
                for i, cell in enumerate(quote.quotes):
                    self.update_cell(
                        quote.key,
                        self._state.columns[i].key,
                        Text(cell[0], justify=cell[1].value),
                    )
                existing_rows.remove(quote.key)
            # add new rows, if any
            else:
                stylized_row: list[Text] = [
                    Text(cell[0], justify=cell[1].value) for cell in quote.quotes
                ]
                self.add_row(*stylized_row, key=quote.key)

        # remove rows that no longer exist, if any
        for row in existing_rows:
            self.remove_row(row)

        self._version = self._state.version

    def watch_hover_coordinate(self, _: Coordinate, value: Coordinate) -> None:
        """
        Watch the hover coordinate and update the cursor type accordingly.

        Args:
            _ (Coordinate): The old coordinate. Unused.
            value (Coordinate): The current hover coordinate.
        """

        if value.row == -1 and self.cursor_type != "column":
            self.cursor_type = "column"
        elif value.row >= 0 and self.cursor_type != "row":
            self.cursor_type = "row"

        if self.cursor_type == "column":
            self.move_cursor(column=value.column)

        logging.debug(value)