from rich.text import Text
from textual.widgets import DataTable

from ._column import Column
from .quotetable_state import QuoteTableState


class QuoteTable(DataTable):
    def __init__(self, state: QuoteTableState) -> None:
        super().__init__()
        self._state: QuoteTableState = state

    def on_mount(self) -> None:
        column: Column
        for column in self._state.columns:
            # TODO Unsure if we put this here on in the state.
            styled_column: Text = Text(column.name, justify=column.justification.value)
            self.add_column(styled_column, width=column.width, key=column.key)

        quote: list[str]
        for quote in self._state.get_quotes():
            # TODO This is certainly suboptimal to have to zip the quote and the columns together every time.
            stylized_row: list[Text] = [
                Text(cell, justify=column.justification.value)
                for cell, column in zip(quote, self._state.columns)
            ]
            self.add_row(*stylized_row)
        self.cursor_type = "row"
        self.zebra_stripes = True
