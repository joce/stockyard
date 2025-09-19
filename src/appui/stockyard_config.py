"""The configuration of the whole stockyard application."""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field, field_serializer, field_validator

from ._enums import TimeFormat, get_enum_member
from .watchlist_config import WatchlistConfig


class StockyardConfig(BaseModel):
    """The Stockyard app configuration."""

    # Pydantic model fields
    title: str = Field(default="Stockyard", description="The title of the app")
    log_level: int = Field(default=logging.INFO, description="The logging level")
    time_format: TimeFormat = Field(
        default=TimeFormat.TWENTY_FOUR_HOUR, description="The time format"
    )
    watchlist: WatchlistConfig = Field(
        default_factory=WatchlistConfig,
        description="Watchlist screen configuration",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, v: int | str | None) -> int:
        """Validate the log level.

        Args:
            v: The log level value to validate.

        Returns:
            int: A valid logging level.
        """
        if isinstance(v, int) and logging.getLevelName(v) != f"Level {v}":
            return v
        if isinstance(v, str):
            level: int | None = logging.getLevelNamesMapping().get(v.upper())
            if level is not None:
                return level
        # Return default if validation fails
        return logging.ERROR

    @field_serializer("log_level")
    @classmethod
    def _serialize_log_level(cls, v: int) -> str:
        """Serialize the log level as a lowercase string.

        Args:
            v: The log level value to serialize.

        Returns:
            str: The lowercase log level name if known, otherwise the numeric string.
        """
        level_name: str = logging.getLevelName(v)
        if not level_name.startswith("Level "):
            return level_name.lower()
        return str(v)

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
