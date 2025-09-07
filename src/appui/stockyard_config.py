"""The configuration of the whole stockyard application."""

from __future__ import annotations

import logging
from typing import Any, Final

from ._enums import TimeFormat, get_enum_member

# from .quote_table_state import QuoteTableState


class StockyardConfig:
    """The Stockyard app configuration."""

    # Human readable logging levels
    _LOGGING_LEVELS: Final[dict[int, str]] = {
        logging.NOTSET: "NOTSET",
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    # Default values
    _DEFAULT_LOG_LEVEL: Final[int] = logging.INFO
    _DEFAULT_TIME_FORMAT: Final[TimeFormat] = TimeFormat.TWENTY_FOUR_HOUR

    # Config file keys
    _QUOTE_TABLE: Final[str] = "quote_table"
    _LOG_LEVEL: Final[str] = "log_level"
    _TIME_FORMAT: Final[str] = "time_format"

    def __init__(self) -> None:
        """Initialize the StockyardAppState."""

        # Persistent members
        #        self._quote_table_state: QuoteTableState = QuoteTableState(self._yfin)
        self._log_level: int = StockyardConfig._DEFAULT_LOG_LEVEL
        self._time_format: TimeFormat = StockyardConfig._DEFAULT_TIME_FORMAT
        self._title: str = "Stockyard"

    @property
    def title(self) -> str:
        """The title of the app."""

        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def log_level(self) -> int:
        """The logging level."""

        return self._log_level

    @log_level.setter
    def log_level(self, value: int) -> None:
        self._log_level = value

    @property
    def time_format(self) -> TimeFormat:
        """The time format."""

        return self._time_format

    @time_format.setter
    def time_format(self, value: TimeFormat) -> None:
        self._time_format = value

    # @property
    # def quote_table_state(self) -> QuoteTableState:
    #     """The state of the quote table."""

    #     return self._quote_table_state

    def load_config(self, config: dict[str, Any]) -> None:
        """Load the configuration for the app.

        Args:
            config (dict[str, Any]): A dictionary to load the configuration from.
        """

        #        quote_table_config: dict[str, Any] = config.get(self._QUOTE_TABLE, {})
        time_format: str | None = config.get(StockyardConfig._TIME_FORMAT, None)
        log_level: str | None = (
            config[StockyardConfig._LOG_LEVEL].upper()
            if StockyardConfig._LOG_LEVEL in config
            else None
        )

        #        self._quote_table_state.load_config(quote_table_config)

        try:
            self._time_format = get_enum_member(TimeFormat, time_format)
        except ValueError:
            self._time_format = StockyardConfig._DEFAULT_TIME_FORMAT

        if log_level is None or log_level not in logging.__dict__:
            self._log_level = StockyardConfig._DEFAULT_LOG_LEVEL
        else:
            self._log_level = logging.__dict__[log_level]

    def save_config(self) -> dict[str, Any]:
        """Save the configuration for the app.

        Returns:
            (dict[str, Any]): A dictionary containing the configuration.
        """

        return {
            # StockyardAppConfig._QUOTE_TABLE: self._quote_table_state.save_config(),
            StockyardConfig._TIME_FORMAT: self._time_format.value,
            StockyardConfig._LOG_LEVEL: StockyardConfig._LOGGING_LEVELS[
                self._log_level
            ],
        }
