from ._enums import Justify


class QuoteRow:
    """Definition of column for the quote table."""

    def __init__(self, key: str, values: list[tuple[str, int, Justify]]) -> None:
        """
        Definition of a row for the quote table.

        Args:
            key (str): The key of the row.
            values (list[tuple[str, int, Justify]]): The values of the row. They are, in order:
                - The value to display.
                - The sign of the value, i.e. negative (-1), positive (1) or neutral (0).
                - The display justification of the value.
        """
        self.key = key
        self.values = values
