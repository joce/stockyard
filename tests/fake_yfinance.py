"""Fake YFinance client that pulls data from a test data file."""

from __future__ import annotations

import json
import os.path
from io import TextIOWrapper
from typing import Any

from yfinance import YFinance, YQuote


class FakeYFinance(YFinance):
    """Fake YFinance client that pulls data from a test data file."""

    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self._quotes: list[YQuote] = []

    def retrieve_quotes(self, symbols: list[str]) -> list[YQuote]:
        """
        Retrieve quotes for the given symbols.

        In this implementation, the quotes are pulled from the test data file.

        Args:
            symbols (list[str]): The symbols to get quotes for.

        Returns:
            list[YQuote]: The quotes for the given symbols.
        """
        if len(self._quotes) <= 0:
            f: TextIOWrapper
            # Get the directory of the path of this file
            test_data_dir = os.path.dirname(os.path.realpath(__file__))
            test_data_file = os.path.join(test_data_dir, "test_data.json")
            with open(test_data_file, "r", encoding="utf-8") as f:
                json_data: dict[str, Any] = json.load(f)
                self._quotes = [
                    YQuote(q)
                    for q in json_data["quoteResponse"]["result"]
                    if q is not None
                ]

        # return the quotes where the symbol is in the list of symbols
        return [q for q in self._quotes if q.symbol in symbols]
