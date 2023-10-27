"""The state of the whole stockyard application."""

import logging
from typing import Any, Optional

from yfinance import YFinance

from ._enums import TimeFormat, get_enum_member
from .quote_table_state import QuoteTableState


class StockyardAppState:
    """The state of the Stockyard app."""

    # Human readable logging levels
    _LOGGING_LEVELS: dict[int, str] = {
        logging.NOTSET: "NOTSET",
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    # Default values
    _DEFAULT_LOG_LEVEL: int = logging.INFO
    _DEFAULT_TIME_FORMAT: TimeFormat = TimeFormat.TWENTY_FOUR_HOUR

    # Config file keys
    _QUOTE_TABLE: str = "quote_table"
    _LOG_LEVEL: str = "log_level"
    _TIME_FORMAT: str = "time_format"

    def __init__(self, yfin: YFinance, *, title: str = "Stockyard") -> None:
        # Transient members
        self._yfin: YFinance = yfin
        self._version: int = 0
        self._title: str = title

        # Persistent members
        self._quote_table_state: QuoteTableState = QuoteTableState(self._yfin)
        self._log_level: int = StockyardAppState._DEFAULT_LOG_LEVEL
        self._time_display: TimeFormat = StockyardAppState._DEFAULT_TIME_FORMAT

    @property
    def title(self) -> str:
        """The title of the app."""

        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self._version += 1

    @property
    def log_level(self) -> int:
        """The logging level."""

        return self._log_level

    @log_level.setter
    def log_level(self, value: int) -> None:
        if value == self._log_level:
            return
        self._log_level = value
        self._version += 1

    @property
    def time_display(self) -> TimeFormat:
        """The time display format."""

        return self._time_display

    @time_display.setter
    def time_display(self, value: TimeFormat) -> None:
        if value == self._time_display:
            return
        self._time_display = value
        self._version += 1

    @property
    def quote_table_state(self) -> QuoteTableState:
        """The state of the quote table."""

        return self._quote_table_state

    def load_config(self, config: dict[str, Any]) -> None:
        """Load the configuration for the app."""

        quote_table_config: dict[str, Any] = (
            config[self._QUOTE_TABLE] if self._QUOTE_TABLE in config else {}
        )
        time_format: Optional[str] = (
            config[StockyardAppState._TIME_FORMAT]
            if StockyardAppState._TIME_FORMAT in config
            else None
        )
        log_level: Optional[str] = (
            config[StockyardAppState._LOG_LEVEL].upper()
            if StockyardAppState._LOG_LEVEL in config
            else None
        )

        if quote_table_config is not None:
            self._quote_table_state.load_config(quote_table_config)

        try:
            self._time_display = get_enum_member(TimeFormat, time_format)
        except ValueError:
            self._time_display = StockyardAppState._DEFAULT_TIME_FORMAT

        if log_level is None or log_level not in logging.__dict__:
            self._log_level = StockyardAppState._DEFAULT_LOG_LEVEL
        else:
            self._log_level = logging.__dict__[log_level]

    def save_config(self, config: dict[str, Any]) -> None:
        """Save the configuration for the app."""

        if len(config) > 0:
            raise ValueError("Configuration dictionary must be empty")

        quote_table_config: dict[str, Any] = {}
        self._quote_table_state.save_config(quote_table_config)
        config[StockyardAppState._QUOTE_TABLE] = quote_table_config
        config[StockyardAppState._TIME_FORMAT] = self._time_display.value

        config[StockyardAppState._LOG_LEVEL] = StockyardAppState._LOGGING_LEVELS[
            self._log_level
        ]
