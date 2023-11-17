"""
This module contains the QuoteTable class which is a DataTable for displaying quotes.
"""

from typing import Any, Final, override

from rich.style import Style
from rich.text import Text
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from ._enums import Justify, SortDirection
from ._quote_table_data import QuoteCell, QuoteColumn, QuoteRow
from .quote_table_state import QuoteTableState


class QuoteTable(DataTable[Text]):
    """A DataTable for displaying quotes."""

    _GAINING_COLOR: Final[str] = "#00DD00"
    _LOSING_COLOR: Final[str] = "#DD0000"

    def __init__(self, state: QuoteTableState) -> None:
        super().__init__()
        self._state: QuoteTableState = state
        self._version: int
        self._column_key_map: dict[str, Any] = {}
        self._current_hover_column: int = -1

        self.cursor_type = "row"
        self.zebra_stripes = True
        self.cursor_foreground_priority = "renderable"

    def __del__(self) -> None:
        # Make sure the query thread is stopped
        self._state.query_thread_running = False

    @override
    def on_mount(self) -> None:
        """The event handler called when the widget is added to the app."""

        super().on_mount()
        quote_column: QuoteColumn
        for quote_column in self._state.quotes_columns:
            styled_column: Text = self._get_styled_column_title(quote_column)
            key = self.add_column(
                styled_column, width=quote_column.width, key=quote_column.key
            )
            self._column_key_map[quote_column.key] = key

        self.set_interval(0.01, self._update_table)
        self.fixed_columns = 1

        # Force a first update
        self._version = self._state.version - 1
        self._state.query_thread_running = True

    @override
    def _on_unmount(self) -> None:
        """
        The event handler called when the widget is removed from the app.

        Required to stop the query thread.
        """

        self._state.query_thread_running = False
        super()._on_unmount()

    def _update_table(self) -> None:
        """Update the table with the latest quotes (if any)"""

        if self._version == self._state.version:
            return

        # Set the column titles, including the sort arrow if needed
        quote_column: QuoteColumn
        for quote_column in self._state.quotes_columns:
            styled_column: Text = self._get_styled_column_title(quote_column)
            self.columns[self._column_key_map[quote_column.key]].label = styled_column

        quotes: list[QuoteRow] = self._state.quotes_rows
        i: int = 0
        quote: QuoteRow
        for i, quote in enumerate(quotes):
            # We only use the index as the row key, so we can update and reorder the
            # rows as needed
            quote_key: str = str(i)
            # Update existing rows
            if quote_key in self.rows:  # pyright: ignore [reportUnnecessaryContains]
                for j, cell in enumerate(quote.values):
                    self.update_cell(
                        quote_key,
                        self._state.quotes_columns[j].key,
                        self._get_styled_cell(cell),
                    )
            else:
                # Add new rows, if any
                stylized_row: list[Text] = [
                    self._get_styled_cell(cell) for cell in quote.values
                ]
                self.add_row(*stylized_row, key=quote_key)

        # Remove extra rows, if any
        for i in range(i + 1, len(self.rows)):
            self.remove_row(row_key=str(i))

        current_row: int = self._state.current_row
        if current_row >= 0:
            self.move_cursor(row=current_row)

        self._version = self._state.version

    def _get_styled_column_title(self, quote_column: QuoteColumn) -> Text:
        """
        Generate a styled column title based on the quote column and the current state.

        If the quote column key matches the sort column key in the current state, an
        arrow indicating the sort direction is added to the column title. The position
        of the arrow depends on the justification of the column: if the column is
        left-justified, the arrow is added at the end of the title; if the column is
        right-justified, the arrow is added at the beginning of the title.

        Args:
            quote_column (QuoteColumn): The quote column for which to generate a styled
                title.

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

    def _get_styled_cell(self, cell: QuoteCell) -> Text:
        """
        Generate the styled text for a cell based on the quote cell data.

        Args:
            cell (QuoteCell): The quote cell for which to generate a styled cell.

        Returns:
            Text: The styled cell.
        """

        return Text(
            cell.value,
            justify=cell.justify.value,
            style=QuoteTable._LOSING_COLOR
            if cell.sign == -1
            else QuoteTable._GAINING_COLOR
            if cell.sign > 0
            else "",
        )

    @override
    def watch_hover_coordinate(self, old: Coordinate, value: Coordinate) -> None:
        """
        Watch the hover coordinate and update the cursor type accordingly.

        Args:
            old (Coordinate): The old hover coordinate.
            value (Coordinate): The current hover coordinate.
        """

        if value.row == -1:
            self._current_hover_column = value.column
        else:
            self._current_hover_column = -1

        super().watch_hover_coordinate(old, value)

    @override
    def _render_cell(
        self,
        row_index: int,
        column_index: int,
        base_style: Style,
        width: int,
        cursor: bool = False,
        hover: bool = False,
    ):
        """
        Override the default _render_cell method to allow for hover on the header.
        """

        if row_index == -1:
            hover = self._current_hover_column == column_index

        return super()._render_cell(
            row_index, column_index, base_style, width, cursor, hover
        )

    @override
    def watch_cursor_coordinate(
        self, old_coordinate: Coordinate, new_coordinate: Coordinate
    ) -> None:
        """
        Watch the cursor coordinate and update the current row accordingly.

        Args:
            old_coordinate (Coordinate): The old coordinate. Unused.
            new_coordinate (Coordinate): The current cursor coordinate.
        """

        super().watch_cursor_coordinate(old_coordinate, new_coordinate)
        self._state.current_row = new_coordinate.row

    def on_data_table_header_selected(self, evt: DataTable.HeaderSelected) -> None:
        """Event handler called when the header is clicked."""

        # TODO We probably need to send an event to the app instead.
        selected_column_key: str = (
            evt.column_key.value if evt.column_key.value is not None else ""
        )

        if selected_column_key != self._state.sort_column_key:
            # TODO Add a function that can set both the sort column and the sort
            # direction at once
            self._state.sort_column_key = selected_column_key
            self._state.sort_direction = SortDirection.ASCENDING
        else:
            self._state.sort_direction = (
                SortDirection.ASCENDING
                if self._state.sort_direction == SortDirection.DESCENDING
                else SortDirection.DESCENDING
            )
