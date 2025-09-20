"""The configuration of the whole stockyard application."""

from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ._enums import LoggingLevel, TimeFormat, get_enum_member
from .watchlist_config import WatchlistConfig

_ALLOW_STOCKYARD_FALLBACK: ContextVar[bool] = ContextVar(
    "_ALLOW_STOCKYARD_FALLBACK", default=False
)


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


def _coerce_time_format(value: TimeFormat | str | None) -> TimeFormat | None:
    """Convert raw time format values into a supported enum if possible.

    Args:
        value (TimeFormat | str | None): The time format value to coerce.

    Returns:
        TimeFormat | None: The coerced time format, or None if coercion failed.
    """

    if isinstance(value, TimeFormat):
        return value
    if isinstance(value, str):
        try:
            return get_enum_member(TimeFormat, value.lower())
        except ValueError:
            return None
    return None


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

    def __init__(self, **data: Any) -> None:
        token = _ALLOW_STOCKYARD_FALLBACK.set(True)
        try:
            super().__init__(**data)
        finally:
            _ALLOW_STOCKYARD_FALLBACK.reset(token)

    @classmethod
    def model_validate(  # noqa: PLR0913 - Required to match BaseModel signature
        cls,
        obj: Any,  # noqa: ANN401 - Required to match BaseModel signature
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        """Validate ``obj`` into a ``StockyardConfig`` instance.

        Args:
            obj: The object to validate.
            strict: Flag to enable strict validation.
            from_attributes: Whether to pull values from attributes.
            context: Additional validation context.
            by_alias: Whether to look up fields by their aliases.
            by_name: Whether to look up fields by their field names.

        Returns:
            StockyardConfig: The validated configuration instance.
        """

        token = _ALLOW_STOCKYARD_FALLBACK.set(True)
        try:
            return super().model_validate(
                obj,
                strict=strict,
                from_attributes=from_attributes,
                context=context,
                by_alias=by_alias,
                by_name=by_name,
            )
        finally:
            _ALLOW_STOCKYARD_FALLBACK.reset(token)

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
        if _ALLOW_STOCKYARD_FALLBACK.get():
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

        fmt = _coerce_time_format(v)
        if fmt is not None:
            return fmt
        if _ALLOW_STOCKYARD_FALLBACK.get():
            return TimeFormat.TWENTY_FOUR_HOUR
        error_msg = f"Unsupported time format value: {v!r}"
        raise ValueError(error_msg)
