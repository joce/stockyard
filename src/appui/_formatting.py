"""
Functions for formatting various data types into strings for the Stockyard application.
"""

_NO_VALUE: str = "N/A"  # TODO Maybe use "" instead?


def as_percent(value: float | None) -> str:
    """
    Converts the given value into a percentage string.

    Args:
        value (float | None): The value to be formatted as a percentage.

    Returns:
        str: The percentage representation of the value. If the value is None, returns
            a placeholder string.
    """

    if value is None:
        return _NO_VALUE
    return f"{value:.2f}%"


def as_float(value: float | None, precision: int = 2) -> str:
    """
    Returns a string representation of the given value as a float with the specified
    precision.

    Args:
        value (float | None): The value to be formatted as a float.
        precision (int): The number of decimal places to include in the formatted
            output.

    Returns:
        str: The float representation of the value with the specified precision. If the
            value is None, returns a placeholder string.
    """

    if value is None:
        return _NO_VALUE
    return f"{value:.{precision}f}"


def as_shrunk_int(value: int | None) -> str:
    """
    Returns a string representation of the given value as a shrunk integer. A "shrunk
    integer" is an integer that is scaled down and represented with a suffix. For
    example, 1500 would be represented as "1.5K".

    Args:
        value (int | None): The value to be formatted as a shrunk integer.

    Returns:
        str: The shrunk integer representation of the value. If the value is None,
            returns a placeholder string.
    """

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
