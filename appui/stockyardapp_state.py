"""The state of the whole stockyard application."""

from typing import Any

from yfinance import YFinance

from .quote_table_state import QuoteTableState


class StockyardAppState:
    """The state of the Stockyard app."""

    _TABLE_CONFIG_KEY: str = "quote_table"

    def __init__(self, yfin: YFinance, *, title: str = "Stockyard") -> None:
        self._title: str = title
        self._yfin: YFinance = yfin
        self._quote_table_state: QuoteTableState = QuoteTableState(self._yfin)
        self._version: int = 0

    @property
    def title(self) -> str:
        """The title of the app."""

        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self._version += 1

    def quote_table_state(self) -> QuoteTableState:
        """The state of the quote table."""

        return self._quote_table_state

    def load_config(self, config: dict[str, Any]) -> None:
        """Load the configuration for the app."""

        quote_table_config: dict[str, Any] = (
            config[self._TABLE_CONFIG_KEY] if self._TABLE_CONFIG_KEY in config else {}
        )
        self._quote_table_state.load_config(quote_table_config)

    def save_config(self, config: dict[str, Any]) -> None:
        """Save the configuration for the app."""

        quote_table_config: dict[str, Any] = {}
        self._quote_table_state.save_config(quote_table_config)
        config[self._TABLE_CONFIG_KEY] = quote_table_config
