import logging
from typing import Any

from rich.text import Text
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from ._enums import Justify, SortDirection
from ._quote_column import QuoteColumn
from ._quote_row import QuoteRow
from .quote_table_state import QuoteTableState


class QuoteTable(DataTable):
    """A DataTable for displaying quotes."""

    def __init__(self, state: QuoteTableState) -> None:
        super().__init__()
        self._state: QuoteTableState = state
        self._version: int
        self._column_key_map: dict[str, Any] = {}

    def on_mount(self) -> None:
        """The event handler called when the widget is added to the app."""

        # TODO: Consider having the first column be the symbols, always, and fixed.
        super().on_mount()
        quote_column: QuoteColumn
        for quote_column in self._state.columns:
            styled_column: Text = self._get_styled_column_title(quote_column)
            key = self.add_column(
                styled_column, width=quote_column.width, key=quote_column.key
            )
            self._column_key_map[quote_column.key] = key

        self.cursor_type = "row"
        self.zebra_stripes = True
        self.cursor_foreground_priority = "renderable"
        self.set_interval(0.1, self._update_table)

        # Force a first update
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

        # TODO make this a function
        quote_column: QuoteColumn
        for quote_column in self._state.columns:
            styled_column: Text = self._get_styled_column_title(quote_column)

            self.columns[self._column_key_map[quote_column.key]].label = styled_column

        quotes: list[QuoteRow] = self._state.get_quotes()
        i: int = 0
        quote: QuoteRow
        for i, quote in enumerate(quotes):
            quote_key: str = str(i)
            if quote_key in self.rows:
                for j, cell in enumerate(quote.values):
                    self.update_cell(
                        quote_key,
                        self._state.columns[j].key,
                        # TODO Create a quote cell class and make this a function
                        Text(
                            cell[0],
                            justify=cell[2].value,
                            style="#DD0000"
                            if cell[1] == -1
                            else "#00DD00"
                            if cell[1] > 0
                            else "",
                        ),
                    )
            else:
                stylized_row: list[Text] = [
                    Text(
                        cell[0],
                        justify=cell[2].value,
                        style="#DD0000"
                        if cell[1] == -1
                        else "#00DD00"
                        if cell[1] > 0
                        else "",
                    )
                    for cell in quote.values
                ]
                self.add_row(*stylized_row, key=quote_key)

        # remove extra rows
        for i in range(i + 1, len(self.rows)):
            self.remove_row(row_key=str(i))

        self._version = self._state.version

    def _get_styled_column_title(self, quote_column: QuoteColumn) -> Text:
        """
        Generate a styled column title based on the quote column and the current state.

        If the quote column key matches the sort column key in the current state, an arrow
        indicating the sort direction is added to the column title. The position of the arrow
        depends on the justification of the column: if the column is left-justified, the arrow
        is added at the end of the title; if the column is right-justified, the arrow is added
        at the beginning of the title.

        Args:
            quote_column (QuoteColumn): The quote column for which to generate a styled title.

        Returns:
            Text: The styled column title.
        """
        column_title: str = quote_column.name
        if quote_column.key == self._state.sort_column_key:
            if quote_column.justification == Justify.LEFT:
                if self._state.sort_direction == SortDirection.ASCENDING:
                    column_title = column_title[: quote_column.width - 2] + " ▼"
                else:
                    column_title = column_title[: quote_column.width - 2] + " ▲"
            else:
                if self._state.sort_direction == SortDirection.ASCENDING:
                    column_title = "▼ " + column_title[: quote_column.width - 2]
                else:
                    column_title = "▲ " + column_title[: quote_column.width - 2]

        return Text(column_title, justify=quote_column.justification.value)

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

    def on_data_table_header_selected(self, evt: DataTable.HeaderSelected) -> None:
        """Event handler called when the header is clicked."""

        # TODO We probably need to send an event to the app instead.
        selected_column_key: str = (
            evt.column_key.value if evt.column_key.value is not None else ""
        )

        if selected_column_key != self._state.sort_column_key:
            # TODO Add a function that can set both the sort column and the sort direction at once
            self._state.sort_column_key = selected_column_key
            self._state.sort_direction = SortDirection.ASCENDING
        else:
            self._state.sort_direction = (
                SortDirection.ASCENDING
                if self._state.sort_direction == SortDirection.DESCENDING
                else SortDirection.DESCENDING
            )
