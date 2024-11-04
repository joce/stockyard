"""
This module contains the QuoteTable class which is a DataTable for displaying quotes.
"""

from __future__ import annotations

import sys
from enum import Enum
from typing import Any, Final

from rich.style import Style
from rich.text import Text
from textual import events
from textual.binding import BindingsMap  # type: ignore
from textual.coordinate import Coordinate
from textual.message import Message
from textual.widgets import DataTable

from ._enums import Justify, SortDirection
from ._quote_table_data import QuoteCell, QuoteColumn, QuoteRow
from .quote_table_state import QuoteTableState

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override


class QuoteTable(DataTable[Text]):
    """A DataTable for displaying quotes."""

    _GAINING_COLOR: Final[str] = "#00DD00"
    _LOSING_COLOR: Final[str] = "#DD0000"

    class BindingsChanged(Message):
        """A message sent when the bindings have changed."""

    class BM(Enum):
        """The binding mode enum for the quote table."""

        DEFAULT = "default"
        WITH_DELETE = "with_delete"
        IN_ORDERING = "in_ordering"

    def __init__(self, state: QuoteTableState) -> None:
        super().__init__()
        self._state: QuoteTableState = state
        self._version: int
        self._column_key_map: dict[str, Any] = {}

        # Bindings
        self._bindings_modes: dict[QuoteTable.BM, BindingsMap] = {
            QuoteTable.BM.DEFAULT: self._bindings.copy(),
            QuoteTable.BM.IN_ORDERING: BindingsMap(),
        }

        self._bindings_modes[QuoteTable.BM.DEFAULT].bind(
            "o", "order_quotes", "Change sort order"
        )
        self._bindings_modes[QuoteTable.BM.DEFAULT].bind(
            "insert", "add_quote", "Add quote", key_display="Ins"
        )

        # For Delete, we want the same bindings as default, plus delete
        self._bindings_modes[QuoteTable.BM.WITH_DELETE] = self._bindings_modes[
            QuoteTable.BM.DEFAULT
        ].copy()
        self._bindings_modes[QuoteTable.BM.WITH_DELETE].bind(
            "delete", "remove_quote", "Remove quote", key_display="Del"
        )

        # For Ordering, we want to drop all default binding. No add / delete, or cursor
        # movement.
        self._bindings_modes[QuoteTable.BM.IN_ORDERING].bind(
            "escape", "exit_ordering", "Done", key_display="Esc"
        )
        self._bindings_modes[QuoteTable.BM.IN_ORDERING].bind(
            "right", "order_move_right", show=False
        )
        self._bindings_modes[QuoteTable.BM.IN_ORDERING].bind(
            "left", "order_move_left", show=False
        )
        self._bindings_modes[QuoteTable.BM.IN_ORDERING].bind(
            "enter", "order_toggle", show=False
        )

        # TODO This maybe should be part of the state... hum...
        self._current_bindings = QuoteTable.BM.DEFAULT
        self._bindings = self._bindings_modes[self._current_bindings]

        # The following (especially the cursor type) need to be set after the binding
        # modes have been created
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.cursor_foreground_priority = "renderable"

    def __del__(self) -> None:
        # Make sure the query thread is stopped
        self._state.query_thread_running = False

    @override
    def on_mount(self) -> None:
        super().on_mount()
        quote_column: QuoteColumn
        for quote_column in self._state.quotes_columns:
            styled_column: Text = self._get_styled_column_title(quote_column)
            key = self.add_column(
                styled_column, width=quote_column.width, key=quote_column.key
            )
            self._column_key_map[quote_column.key] = key

        self.set_interval(0.1, self._update_table)
        self.fixed_columns = 1

        # Force a first update
        self._version = self._state.version - 1
        self._state.query_thread_running = True

    @override
    def _on_unmount(self) -> None:
        self._state.query_thread_running = False
        super()._on_unmount()

    def _switch_bindings(self, mode: "QuoteTable.BM") -> None:
        """Switch the bindings to the given mode."""

        if self._current_bindings == mode:
            return
        self._current_bindings = mode
        self._bindings = self._bindings_modes[self._current_bindings]
        self.post_message(self.BindingsChanged())

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

        if len(quotes) > 0:
            if self._current_bindings == QuoteTable.BM.DEFAULT:
                self._switch_bindings(QuoteTable.BM.WITH_DELETE)
        else:
            if self._current_bindings == QuoteTable.BM.WITH_DELETE:
                self._switch_bindings(QuoteTable.BM.DEFAULT)

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
        for r in range(i, len(self.rows)):
            self.remove_row(row_key=str(r))

        current_row: int = self._state.cursor_row
        if current_row >= 0:
            if self.cursor_type == "none":
                self.cursor_type = "row"
            self.move_cursor(row=current_row)
        else:
            self.cursor_type = "none"

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
            style=(
                QuoteTable._LOSING_COLOR
                if cell.sign == -1
                else QuoteTable._GAINING_COLOR if cell.sign > 0 else ""
            ),
        )  # fmt: skip

    @override
    def watch_hover_coordinate(self, old: Coordinate, value: Coordinate) -> None:
        if self._current_bindings == QuoteTable.BM.IN_ORDERING:
            return

        if value.row == -1:
            self._state.hovered_column = value.column
        else:
            self._state.hovered_column = -1

        super().watch_hover_coordinate(old, value)

    @override
    async def _on_click(self, event: events.Click) -> None:
        # Prevent mouse interaction when in ordering (KB-only) mode
        if self._current_bindings == QuoteTable.BM.IN_ORDERING:
            event.prevent_default()

    @override
    def _on_mouse_move(self, event: events.MouseMove) -> None:
        # Prevent mouse interaction when in ordering (KB-only) mode
        if self._current_bindings == QuoteTable.BM.IN_ORDERING:
            event.prevent_default()

    @override
    def _render_cell(  # pylint: disable=too-many-positional-arguments
        self,
        row_index: int,
        column_index: int,
        base_style: Style,
        width: int,
        cursor: bool = False,
        hover: bool = False,
    ):
        current_show_hover_cursor: bool = self._show_hover_cursor
        if row_index == -1:
            if self._current_bindings == QuoteTable.BM.IN_ORDERING:
                self._show_hover_cursor = True
            hover = self._state.hovered_column == column_index  # Mouse mode

        try:
            return super()._render_cell(
                row_index, column_index, base_style, width, cursor, hover
            )
        finally:
            if row_index == -1:
                if self._current_bindings == QuoteTable.BM.IN_ORDERING:
                    self._show_hover_cursor = current_show_hover_cursor

    @override
    def watch_cursor_coordinate(
        self, old_coordinate: Coordinate, new_coordinate: Coordinate
    ) -> None:
        super().watch_cursor_coordinate(old_coordinate, new_coordinate)
        self._state.cursor_row = new_coordinate.row

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

    def action_add_quote(self) -> None:
        """Add a new quote to the table."""

        self.app.exit()

    def action_remove_quote(self) -> None:
        """Remove the selected quote from the table."""

        self._state.remove_row(self.cursor_row)

    def action_order_quotes(self) -> None:
        """Order the quotes in the table."""

        self._switch_bindings(QuoteTable.BM.IN_ORDERING)
        self._set_hover_cursor(False)
        if self._state.hovered_column == -1:
            self._state.hovered_column = self._state.sort_column_idx
        self._version -= 1  # Force refresh

    def action_exit_ordering(self) -> None:
        """Exit the ordering mode."""

        if len(self._state.quotes_rows) > 0:
            self._switch_bindings(QuoteTable.BM.WITH_DELETE)
        else:
            self._switch_bindings(QuoteTable.BM.DEFAULT)

        self._set_hover_cursor(True)

        # TODO Might want to set to whatever the mouse hover is now
        self._state.hovered_column = -1

    def action_order_move_right(self) -> None:
        """Move the cursor right in order mode."""

        self._state.hovered_column += 1

    def action_order_move_left(self) -> None:
        """Move the cursor left in order mode."""

        # We need the check here cause hovered_column can go to -1 (which signifies
        # the hovered column is inactive)
        # TODO Maybe we should just use a different variable for the hovered state
        # on/off
        if self._state.hovered_column > 0:
            self._state.hovered_column -= 1

    def action_order_toggle(self) -> None:
        """Toggle the order of the current column in order mode."""

        if self._state.hovered_column != self._state.sort_column_idx:
            self._state.sort_column_idx = self._state.hovered_column
        else:
            self._state.sort_direction = (
                SortDirection.ASCENDING
                if self._state.sort_direction == SortDirection.DESCENDING
                else SortDirection.DESCENDING
            )
