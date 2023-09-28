from .enums import Justify


class Column:
    """Definition of column for the quote table."""

    def __init__(
        self, name: str, width: int, key: str, justify: Justify = Justify.RIGHT
    ) -> None:
        self.name = name
        self.width = width
        self.key = key
        self.justification = justify
