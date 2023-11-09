"""
Test helpers.
"""

from appui._formatting import _NO_VALUE


def compare_shrunken_ints(a: str, b: str) -> int:
    """
    Compare two shrunk integers, provided as strings.

    Args:
        a (str): first shrunk integer
        b (str): second shrunk integer

    Returns:
        int: -1 if a < b, 1 if a > b, 0 if a == b
    """
    if _NO_VALUE in (a, b):
        return 0 if a == b else 1 if b == _NO_VALUE else -1

    if a[-1].isdigit():
        if b[-1].isdigit():
            a_int = int(a)
            b_int = int(b)
            return -1 if a_int < b_int else 1 if a_int > b_int else 0
        return -1

    if b[-1].isdigit():
        return 1

    if a[-1] == b[-1]:
        a_flt = float(a[:-1])
        b_flt = float(b[:-1])
        return -1 if a_flt < b_flt else 1 if a_flt > b_flt else 0

    abbrevs: list[str] = ["K", "M", "B", "T"]
    return -1 if abbrevs.index(a[-1]) < abbrevs.index(b[-1]) else 1
