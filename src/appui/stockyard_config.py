"""The configuration of the whole stockyard application."""

from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ._enums import LoggingLevel, TimeFormat
from ._lenient_assignment_mixin import LenientAssignmentMixin, coerce_enum_member
from .watchlist_config import WatchlistConfig


def _coerce_log_level(value: LoggingLevel | int | str | None) -> LoggingLevel | None:
    """Convert raw log level values into a supported enum if possible.

    Args:
        value (LoggingLevel | int | str | None): The log level value to coerce.

    Returns:
        LoggingLevel | None: The coerced log level, or None if coercion failed.
    """

    if isinstance(value, LoggingLevel):
        return value
    if isinstance(value, int):
        try:
            return LoggingLevel(value)
        except ValueError:
            return None
    if isinstance(value, str):
        mapped_level = logging.getLevelNamesMapping().get(value.upper())
        if mapped_level is not None:
            try:
                return LoggingLevel(mapped_level)
            except ValueError:
                return None
    return None


class StockyardConfig(LenientAssignmentMixin, BaseModel):
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
    def _validate_log_level(cls, v: LoggingLevel | int | str | None) -> LoggingLevel:
        """Validate the log level.

        Args:
            v: The log level value to validate.

        Returns:
            LoggingLevel: A valid logging level.

        Raises:
            ValueError: If the log level value is unsupported and fallback not allowed.
        """

        level = _coerce_log_level(v)
        if level is not None:
            return level
        if cls._fallback_enabled():
            return LoggingLevel.ERROR
        error_msg = f"Unsupported log level value: {v!r}"
        raise ValueError(error_msg)

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

        Raises:
            ValueError: If the time format value is unsupported and fallback not
            allowed.
        """

        fmt = coerce_enum_member(TimeFormat, v)
        if fmt is not None:
            return fmt
        if cls._fallback_enabled():
            return TimeFormat.TWENTY_FOUR_HOUR
        error_msg = f"Unsupported time format value: {v!r}"
        raise ValueError(error_msg)
