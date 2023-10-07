"""Provides functions for formatting values as strings for Stockyard."""

_NO_VALUE: str = "N/A"  ## TODO... Maybe use "" instead?


def as_percent(value: float | None) -> str:
    """Returns a string representation of the given value as a percentage."""

    if value is None:
        return _NO_VALUE
    return f"{value:.2f}%"


def as_float(value: float | None, precision: int = 2) -> str:
    """Returns a string representation of the given value as a price."""

    if value is None:
        return _NO_VALUE
    return f"{value:.{precision}f}"


def as_shrunk_int(value: int | None) -> str:
    """Returns a string representation of the given value as a shrunk integer."""

    if value is None:
        return _NO_VALUE
    if value < 1000:
        return str(value)
    if value < 1000000:
        return f"{value / 1000:.2f}K"
    if value < 1000000000:
        return f"{value / 1000000:.2f}M"
    if value < 1000000000000:
        return f"{value / 1000000000:.2f}B"

    return f"{value / 1000000000000:.2f}T"
