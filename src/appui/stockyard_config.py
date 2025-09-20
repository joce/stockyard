"""The configuration of the whole stockyard application."""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ._enums import LoggingLevel, TimeFormat, get_enum_member
from .watchlist_config import WatchlistConfig


class StockyardConfig(BaseModel):
    """The Stockyard app configuration."""

    model_config = ConfigDict(validate_assignment=True)

    # Pydantic model fields
    title: str = Field(default="Stockyard", description="The title of the app")
    log_level: LoggingLevel = Field(
        default=LoggingLevel.INFO, description="The logging level"
    )
    time_format: TimeFormat = Field(
        default=TimeFormat.TWENTY_FOUR_HOUR, description="The time format"
    )
    watchlist: WatchlistConfig = Field(
        default_factory=WatchlistConfig,
        description="Watchlist screen configuration",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, v: LoggingLevel | str | None) -> LoggingLevel:
        """Validate the log level.

        Args:
            v: The log level value to validate.

        Returns:
            LoggingLevel: A valid logging level.
        """
        if isinstance(v, LoggingLevel):
            return v

        # Handle string input
        try:
            level: int = logging.getLevelNamesMapping()[
                v.upper() if isinstance(v, str) else ""
            ]
            return get_enum_member(LoggingLevel, level)
        except (ValueError, KeyError):
            return LoggingLevel.ERROR

    @field_serializer("log_level")
    @classmethod
    def _serialize_log_level(cls, v: LoggingLevel) -> str:
        """Serialize the log level as a lowercase string.

        Args:
            v: The log level value to serialize.

        Returns:
            str: The lowercase log level name if known, otherwise the numeric string.
        """
        level_name: str = logging.getLevelName(int(v))
        if not level_name.startswith("Level "):
            return level_name.lower()
        return str(int(v))

    @field_validator("time_format", mode="before")
    @classmethod
    def _validate_time_format(cls, v: TimeFormat | str | None) -> TimeFormat:
        """Validate the time format.

        Args:
            v: The time format value to validate.

        Returns:
            TimeFormat: A valid time format.
        """
        if isinstance(v, TimeFormat):
            return v

        # Handle string input
        try:
            return get_enum_member(TimeFormat, v.lower() if isinstance(v, str) else v)
        except ValueError:
            return TimeFormat.TWENTY_FOUR_HOUR
