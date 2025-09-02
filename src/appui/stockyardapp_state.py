# """The state of the whole stockyard application."""

# from __future__ import annotations

# import logging
# from typing import TYPE_CHECKING, Any, Final

# from ._enums import TimeFormat, get_enum_member
# from .quote_table_state import QuoteTableState

# if TYPE_CHECKING:
#     from yfinance import YFinance


# class StockyardAppState:
#     """The state of the Stockyard app."""

#     # Human readable logging levels
#     _LOGGING_LEVELS: Final[dict[int, str]] = {
#         logging.NOTSET: "NOTSET",
#         logging.DEBUG: "DEBUG",
#         logging.INFO: "INFO",
#         logging.WARNING: "WARNING",
#         logging.ERROR: "ERROR",
#         logging.CRITICAL: "CRITICAL",
#     }

#     # Default values
#     _DEFAULT_LOG_LEVEL: Final[int] = logging.INFO
#     _DEFAULT_TIME_FORMAT: Final[TimeFormat] = TimeFormat.TWENTY_FOUR_HOUR

#     # Config file keys
#     _QUOTE_TABLE: Final[str] = "quote_table"
#     _LOG_LEVEL: Final[str] = "log_level"
#     _TIME_FORMAT: Final[str] = "time_format"

#     def __init__(self, yfin: YFinance, *, title: str = "Stockyard") -> None:
#         """
#         Initialize the StockyardAppState.

#         Args:
#             yfin: The YFinance object to fetch the data from.
#             title: The title of the app. Defaults to "Stockyard".
#         """

#         # Transient members
#         self._yfin: YFinance = yfin
#         self._version: int = 0
#         self._title: str = title

#         # Persistent members
#         self._quote_table_state: QuoteTableState = QuoteTableState(self._yfin)
#         self._log_level: int = StockyardAppState._DEFAULT_LOG_LEVEL
#         self._time_format: TimeFormat = StockyardAppState._DEFAULT_TIME_FORMAT

#     @property
#     def title(self) -> str:
#         """The title of the app."""

#         return self._title

#     @title.setter
#     def title(self, value: str) -> None:
#         self._title = value
#         self._version += 1

#     @property
#     def log_level(self) -> int:
#         """The logging level."""

#         return self._log_level

#     @log_level.setter
#     def log_level(self, value: int) -> None:
#         if value == self._log_level:
#             return
#         self._log_level = value
#         self._version += 1

#     @property
#     def time_format(self) -> TimeFormat:
#         """The time format."""

#         return self._time_format

#     @time_format.setter
#     def time_format(self, value: TimeFormat) -> None:
#         if value == self._time_format:
#             return
#         self._time_format = value
#         self._version += 1

#     @property
#     def quote_table_state(self) -> QuoteTableState:
#         """The state of the quote table."""

#         return self._quote_table_state

#     def load_config(self, config: dict[str, Any]) -> None:
#         """
#         Load the configuration for the app.

#         Args:
#             config (dict[str, Any]): A dictionary to load the configuration from.
#         """

#         quote_table_config: dict[str, Any] = config.get(self._QUOTE_TABLE, {})
#         time_format: str | None = config.get(StockyardAppState._TIME_FORMAT, None)
#         log_level: str | None = (
#             config[StockyardAppState._LOG_LEVEL].upper()
#             if StockyardAppState._LOG_LEVEL in config
#             else None
#         )

#         self._quote_table_state.load_config(quote_table_config)

#         try:
#             self._time_format = get_enum_member(TimeFormat, time_format)
#         except ValueError:
#             self._time_format = StockyardAppState._DEFAULT_TIME_FORMAT

#         if log_level is None or log_level not in logging.__dict__:
#             self._log_level = StockyardAppState._DEFAULT_LOG_LEVEL
#         else:
#             self._log_level = logging.__dict__[log_level]

#     def save_config(self) -> dict[str, Any]:
#         """
#         Save the configuration for the app.

#         Returns:
#             (dict[str, Any]): A dictionary containing the configuration.
#         """

#         return {
#             StockyardAppState._QUOTE_TABLE: self._quote_table_state.save_config(),
#             StockyardAppState._TIME_FORMAT: self._time_format.value,
#             StockyardAppState._LOG_LEVEL: StockyardAppState._LOGGING_LEVELS[
#                 self._log_level
#             ],
#         }
