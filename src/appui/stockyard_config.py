"""The configuration of the whole stockyard application."""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field, field_validator

from ._enums import TimeFormat


class StockyardConfig(BaseModel):
    """The Stockyard app configuration."""

    # Pydantic model fields
    title: str = Field(default="Stockyard", description="The title of the app")
    log_level: int = Field(default=logging.INFO, description="The logging level")
    time_format: TimeFormat = Field(
        default=TimeFormat.TWENTY_FOUR_HOUR, description="The time format"
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, v: int | str) -> int:
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

    @field_validator("time_format", mode="before")
    @classmethod
    def _validate_time_format(cls, v: TimeFormat | str) -> TimeFormat:
        """Validate the time format.

        Args:
            v: The time format value to validate.

        Returns:
            TimeFormat: A valid time format.
        """
        if isinstance(v, TimeFormat):
            return v
        # Handle string input
        for time_format in TimeFormat:
            if time_format.value == v:
                return time_format
        # Return default if validation fails
        return TimeFormat.TWENTY_FOUR_HOUR
