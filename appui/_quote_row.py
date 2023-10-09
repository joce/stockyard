from ._enums import Justify


class QuoteRow:
    """Definition of column for the quote table."""

    def __init__(self, key: str, values: list[tuple[str, Justify]]) -> None:
        self.key = key
        self.values = values
