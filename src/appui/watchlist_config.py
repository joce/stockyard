"""The configuration of the watchlist screen."""

from __future__ import annotations

import logging
from typing import ClassVar, Final

from pydantic import BaseModel, Field, field_validator, model_validator

from ._enums import SortDirection, get_enum_member
from ._quote_column_definitions import ALL_QUOTE_COLUMNS

_LOGGER = logging.getLogger(__name__)


class WatchlistConfig(BaseModel):
    """The Watchlist screen configuration.

    Notes:
        - The `columns` field contains only non-`ticker` columns. The table always
          includes the `ticker` column as the first column via `table_columns`.
        - Validation mirrors the previous manual implementation, with warnings
          logged for invalid or duplicate values.
    """

    # Constants (not part of the model schema)
    _TICKER_COLUMN_NAME: ClassVar[Final[str]] = "ticker"
    _DEFAULT_COLUMN_NAMES: ClassVar[Final[list[str]]] = [
        "last",
        "change_percent",
        "volume",
        "market_cap",
    ]
    _DEFAULT_TICKERS: ClassVar[Final[list[str]]] = [
        "AAPL",
        "F",
        "VT",
        "^DJI",
        "ARKK",
        "GC=F",
        "EURUSD=X",
        "BTC-USD",
    ]
    _DEFAULT_SORT_DIRECTION: ClassVar[Final[SortDirection]] = SortDirection.ASCENDING
    _DEFAULT_QUERY_FREQUENCY: ClassVar[Final[int]] = 60

    # Pydantic model fields
    columns: list[str] = Field(
        default_factory=lambda: WatchlistConfig._DEFAULT_COLUMN_NAMES[:],
        description="Non-ticker columns to display (ticker is always first)",
    )
    sort_column: str = Field(
        default=_TICKER_COLUMN_NAME,
        description="Key of the column to sort by (includes 'ticker')",
    )
    sort_direction: SortDirection = Field(
        default=_DEFAULT_SORT_DIRECTION, description="Sort direction"
    )
    quotes: list[str] = Field(
        default_factory=lambda: WatchlistConfig._DEFAULT_TICKERS[:],
        description="List of quote symbols",
    )
    query_frequency: int = Field(
        default=_DEFAULT_QUERY_FREQUENCY,
        description="Refresh/query frequency in seconds",
        ge=1,
    )

    # -------------------- Validators --------------------
    @field_validator("columns", mode="before")
    @classmethod
    def _normalize_columns(cls, v: list[str] | None) -> list[str]:
        """Normalize and validate the list of non-ticker columns.

        Args:
            v: The provided columns list, excluding `ticker`.

        Returns:
            list[str]: A filtered, de-duplicated list of valid column keys.
        """
        if not v:
            _LOGGER.warning("No columns specified in config; using defaults")
            return cls._DEFAULT_COLUMN_NAMES[:]

        filtered: list[str] = []
        seen: set[str] = set()
        for col in v:
            if col == cls._TICKER_COLUMN_NAME:
                # Always implicit; ignore if provided.
                continue
            if col not in ALL_QUOTE_COLUMNS:
                _LOGGER.warning("Invalid column key '%s' specified in config", col)
                continue
            if col in seen:
                _LOGGER.warning("Duplicate column key '%s' specified in config", col)
                continue
            seen.add(col)
            filtered.append(col)

        if not filtered:
            _LOGGER.warning("All provided columns were invalid; using defaults")
            return cls._DEFAULT_COLUMN_NAMES[:]

        return filtered

    @field_validator("sort_direction", mode="before")
    @classmethod
    def _validate_sort_direction(cls, v: SortDirection | str | None) -> SortDirection:
        """Validate sort direction, accepting enum or string values.

        Args:
            v: The provided sort direction value or string.

        Returns:
            SortDirection: A valid sort direction.
        """
        if isinstance(v, SortDirection):
            return v
        try:
            return get_enum_member(SortDirection, v)
        except ValueError:
            return cls._DEFAULT_SORT_DIRECTION

    @field_validator("quotes", mode="before")
    @classmethod
    def _normalize_quotes(cls, v: list[str] | None) -> list[str]:
        """Normalize quotes: uppercase, remove empties and duplicates.

        Args:
            v: The provided list of quote symbols.

        Returns:
            list[str]: A cleaned list of symbols or defaults if empty.
        """
        if not v:
            _LOGGER.warning("No quotes specified in config; using defaults")
            return cls._DEFAULT_TICKERS[:]

        result: list[str] = []
        seen: set[str] = set()
        for symbol in v:
            if symbol == "":  # noqa: PLC1901
                _LOGGER.warning("Empty quote symbol specified in config")
                continue
            up = symbol.upper()
            if up in seen:
                _LOGGER.warning("Duplicate quote symbol %s specified in config", up)
                continue
            seen.add(up)
            result.append(up)

        if not result:
            _LOGGER.warning("All provided quotes were invalid; using defaults")
            return cls._DEFAULT_TICKERS[:]
        return result

    @field_validator("query_frequency", mode="before")
    @classmethod
    def _validate_query_frequency(cls, v: int | None) -> int:
        """Validate query frequency; fallback to default when invalid.

        Args:
            v: The provided frequency in seconds.

        Returns:
            int: A valid frequency (>= 1), or the default if invalid.
        """
        if v is None or v <= 1:
            _LOGGER.warning(
                "Invalid query frequency specified in config; using default"
            )
            return cls._DEFAULT_QUERY_FREQUENCY
        return v

    @model_validator(mode="after")
    def _finalize(self) -> WatchlistConfig:
        """Finalize cross-field validation for sort column membership.

        Ensures `sort_column` is one of `table_columns`; otherwise defaults to the
        first entry (which is always `ticker`).

        Returns:
            WatchlistConfig: The validated model instance.
        """
        if self.sort_column not in self.columns:
            self.sort_column = self._TICKER_COLUMN_NAME
        return self
