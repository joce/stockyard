"""A data table widget to display and manipulate financial quotes."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Final

from rich.text import Text
from textual.binding import BindingsMap
from textual.reactive import Reactive, reactive
from textual.widgets import DataTable
from textual.widgets._data_table import ColumnKey  # noqa: PLC2701
from typing_extensions import Self

from ._enums import Justify, SortDirection
from ._messages import TableSortingChanged

if TYPE_CHECKING:
    from rich.style import Style
    from textual import events
    from textual._types import SegmentLines
    from textual.coordinate import Coordinate

    from ._quote_table_data import QuoteColumn

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class QuoteTable(DataTable[Text]):
    """A DataTable for displaying quotes."""

    _GAINING_COLOR: Final[str] = "#00DD00"
    _LOSING_COLOR: Final[str] = "#DD0000"

    _hovered_column: Reactive[int] = reactive(-1)

    def __init__(self) -> None:
        super().__init__()
        self._quote_columns: list[QuoteColumn] = []
        self._is_ordering: bool = False

        self._cursor_row: int = -1

        self._sort_column_key: str = ""
        self._sort_direction: SortDirection = SortDirection.ASCENDING

        # Bindings
        self._ordering_bindings: BindingsMap = BindingsMap()
        self._default_bindings: BindingsMap = BindingsMap()

        self._ordering_bindings.bind("right", "order_move_right", show=False)
        self._ordering_bindings.bind("left", "order_move_left", show=False)
        self._ordering_bindings.bind("enter", "order_select", show=False)

        # The following (especially the cursor type) need to be set after the binding
        # modes have been created
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.cursor_foreground_priority = "renderable"
        self.fixed_columns = 1

        #     @override
        #     def _on_unmount(self) -> None:
        #         self._state.query_thread_running = False
        #         super()._on_unmount()

        #     def _update_table(self) -> None:
        #         """Update the table with the latest quotes (if any)."""

        #         if self._version == self._state.version:
        #             return

        #         # Set the column titles, including the sort arrow if needed
        #         quote_column: QuoteColumn
        #         for quote_column in self._state.quotes_columns:
        #             styled_column: Text = self._get_styled_column_title(quote_column)
        #             self.columns[self._column_key_map[quote_column.key]].label = styled_column

        #         quote_rows: list[QuoteRow] = self._state.quotes_rows

        #         i: int = 0
        #         quote: QuoteRow
        #         for quote in quote_rows:
        #             # We only use the index as the row key, so we can update and reorder the
        #             # rows as needed
        #             quote_key: RowKey = RowKey(str(i))
        #             i += 1
        #             # Update existing rows
        #             if quote_key in self.rows:
        #                 for j, cell in enumerate(quote.values):
        #                     self.update_cell(
        #                         quote_key,
        #                         self._state.quotes_columns[j].key,
        #                         QuoteTable._get_styled_cell(cell),
        #                     )
        #             else:
        #                 # Add new rows, if any
        #                 stylized_row: list[Text] = [
        #                     QuoteTable._get_styled_cell(cell) for cell in quote.values
        #                 ]
        #                 self.add_row(*stylized_row, key=quote_key.value)

        #         # Remove extra rows, if any
        #         for r in range(i, len(self.rows)):
        #             self.remove_row(row_key=str(r))

        #         current_row: int = self._state.cursor_row
        #         if current_row >= 0:
        #             if self.cursor_type == "none":
        #                 self.cursor_type = "row"
        #             self.move_cursor(row=current_row)
        #         else:
        #             self.cursor_type = "none"

        #         self._version = self._state.version

    def _update_column_label(self, quote_column_key: str) -> None:
        """Update the label of a column based on its key.

        Args:
            quote_column_key (str): The key of the column to update.
        """

        label = self._get_styled_column_label(quote_column_key)
        self.columns[ColumnKey(quote_column_key)].label = label
        self._update_count += 1
        self.refresh()

    def _get_styled_column_label(self, quote_column_key: str) -> Text:
        """Generate a styled column title based on the column and the current state.

        If the quote column key matches the sort column key in the current state, an
        arrow indicating the sort direction is added to the column title. The position
        of the arrow depends on the justification of the column: if the column is
        left-justified, the arrow is added at the end of the title; if the column is
        right-justified, the arrow is added at the beginning of the title.

        Args:
            quote_column_key (str): The key of the  column for which to generate a
                styled title.

        Returns:
            Text: The styled column title.
        """

        quote_column: QuoteColumn = next(
            col for col in self._quote_columns if col.key == quote_column_key
        )
        column_title: str = quote_column.label
        if quote_column.key == self._sort_column_key:
            if quote_column.justification == Justify.LEFT:
                if self._sort_direction == SortDirection.ASCENDING:
                    column_title = column_title[: quote_column.width - 2] + " ▼"
                else:
                    column_title = column_title[: quote_column.width - 2] + " ▲"
            else:  # noqa: PLR5501
                if self._sort_direction == SortDirection.ASCENDING:
                    column_title = "▼ " + column_title[: quote_column.width - 2]
                else:
                    column_title = "▲ " + column_title[: quote_column.width - 2]

        return Text(column_title, justify=quote_column.justification.value)

        #     @classmethod
        #     def _get_styled_cell(cls, cell: QuoteCell) -> Text:
        #         """
        #         Generate the styled text for a cell based on the quote cell data.

        #         Args:
        #             cell (QuoteCell): The quote cell for which to generate a styled cell.

        #         Returns:
        #             Text: The styled cell.
        #         """

        #         return Text(
        #             cell.value,
        #             justify=cell.justify.value,
        #             style=(
        #                 QuoteTable._LOSING_COLOR
        #                 if cell.sign == -1
        #                 else QuoteTable._GAINING_COLOR if cell.sign > 0 else ""
        #             ),
        #         )  # fmt: skip

    # Overrides

    @override
    def clear(self, columns: bool = False) -> Self:
        self._quote_columns.clear()
        return super().clear(columns)

    @override
    def watch_hover_coordinate(self, old: Coordinate, value: Coordinate) -> None:
        if self.is_ordering:
            return

        if value.row == -1:
            self._hovered_column = value.column
        else:
            self._hovered_column = -1

        super().watch_hover_coordinate(old, value)

    @override
    def watch_cursor_coordinate(
        self, old_coordinate: Coordinate, new_coordinate: Coordinate
    ) -> None:

        super().watch_cursor_coordinate(old_coordinate, new_coordinate)
        self._cursor_row = new_coordinate.row

    @override
    async def _on_click(self, event: events.Click) -> None:
        # Prevent mouse interaction when in ordering (KB-only) mode
        if self.is_ordering:
            event.prevent_default()

    @override
    def _on_mouse_move(self, event: events.MouseMove) -> None:
        # Prevent mouse interaction when in ordering (KB-only) mode
        if self.is_ordering:
            event.prevent_default()

    @override
    def _render_cell(
        self,
        row_index: int,
        column_index: int,
        base_style: Style,
        width: int,
        cursor: bool = False,
        hover: bool = False,
    ) -> SegmentLines:
        current_show_hover_cursor: bool = self._show_hover_cursor
        if row_index == -1:
            if self.is_ordering:
                self._show_hover_cursor = True
            hover = self._hovered_column == column_index  # Mouse mode

        try:
            return super()._render_cell(
                row_index, column_index, base_style, width, cursor, hover
            )
        finally:
            if row_index == -1 and self.is_ordering:
                self._show_hover_cursor = current_show_hover_cursor

    # public API

    def add_quote_column(
        self,
        quote_column: QuoteColumn,
    ) -> None:
        """Add a quote column to the table.

        Args:
            quote_column (QuoteColumn): The quote column to add.
        """
        self._quote_columns.append(quote_column)
        super().add_column(
            self._get_styled_column_label(quote_column.key),
            width=quote_column.width,
            key=quote_column.key,
        )

    @property
    def is_ordering(self) -> bool:
        """Whether the table is in ordering mode."""

        return self._is_ordering

    @is_ordering.setter
    def is_ordering(self, value: bool) -> None:
        if value == self._is_ordering:
            return

        self._set_hover_cursor(active=not value)
        if value:
            if self._hovered_column == -1:
                self._hovered_column = self._sort_column_idx
            self._bindings = self._ordering_bindings
        else:
            self._hovered_column = -1
            self._bindings = self._default_bindings
        self._is_ordering = value

    @property
    def sort_column_key(self) -> str:
        """The key of the column currently used for sorting.

        Raises:
            ValueError: If the provided key is not a valid column key.
        """  # noqa: DOC502

        return self._sort_column_key

    @sort_column_key.setter
    def sort_column_key(self, value: str) -> None:

        if value not in [column.key for column in self._quote_columns]:
            error_text = f"Invalid sort column key: {value}"
            raise ValueError(error_text)
        if value != self._sort_column_key:
            prev_key = self._sort_column_key
            self._sort_column_key = value
            if prev_key:
                self._update_column_label(prev_key)
            self._update_column_label(self._sort_column_key)

    @property
    def sort_direction(self) -> SortDirection:
        """The current sort direction."""

        return self._sort_direction

    @sort_direction.setter
    def sort_direction(self, value: SortDirection) -> None:
        if value != self._sort_direction:
            self._sort_direction = value
            self._update_column_label(self._sort_column_key)

    # Keyboard actions for ordering mode

    def action_order_move_right(self) -> None:
        """Move the cursor right in order mode."""

        if self._hovered_column < len(self.columns) - 1:
            self._hovered_column += 1

    def action_order_move_left(self) -> None:
        """Move the cursor left in order mode."""

        # We need the check here cause hovered_column can go to -1 (which signifies
        # the hovered column is inactive)
        # TODO Maybe we should just use a different variable for the hovered state
        # on/off
        if self._hovered_column > 0:
            self._hovered_column -= 1

    def action_order_select(self) -> None:
        """Handle the selecting of the current column in order mode."""

        self._select_column(self._hovered_column)

    # Event handlers

    def on_data_table_header_selected(self, evt: DataTable.HeaderSelected) -> None:
        """Event handler called when the header is clicked.

        Args:
            evt (DataTable.HeaderSelected): The event object.
        """

        self._select_column(evt.column_index)

    # Watchers

    def watch__hovered_column(self, _old: int, _value: int) -> None:
        """Watcher for the hovered column."""

        # Force a re-render of the header row
        self._update_count += 1

    # Helpers

    @property
    def _sort_column_idx(self) -> int:
        """Helper to get the index of the current sort column."""

        try:
            # return the index of the current sort column. It's found by its key
            return self._quote_columns.index(
                next(
                    col
                    for col in self._quote_columns
                    if col.key == self._sort_column_key
                )
            )
        except ValueError:
            return 0

    def _select_column(self, index: int) -> None:
        """Select the column at the given index.

        Args:
            index (int): The index of the column to select.
        """

        if index != self._sort_column_idx:
            self.sort_column_key = self._quote_columns[index].key
        else:
            self.sort_direction = (
                SortDirection.ASCENDING
                if self.sort_direction == SortDirection.DESCENDING
                else SortDirection.DESCENDING
            )

        self.post_message(
            TableSortingChanged(self.sort_column_key, self.sort_direction)
        )
