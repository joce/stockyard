from yfin import YFin

from .quotetablestate import QuoteTableState


class StockyardAppState:
    """The state of the Stockyard app."""

    def __init__(self, yfin: YFin, *, title: str = "Stockyard"):
        self._title: str = title
        self._yfin: YFin = yfin
        self._quote_table_state: QuoteTableState = QuoteTableState(self._yfin)
        # TODO: add a dirty flag and an indicator of what has been dirtied

    @property
    def title(self):
        """The title of the app."""
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def quote_table_state(self):
        """The state of the quote table."""
        return self._quote_table_state
