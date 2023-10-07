from ._enums import Justify


class QuoteRow:
    """Definition of column for the quote table."""

    def __init__(self, key: str, quotes: list[tuple[str, Justify]]) -> None:
        self.key = key
        self.quotes = quotes
