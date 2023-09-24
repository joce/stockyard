"""
A Python interface to the Yahoo! Finance API.
"""

import logging
from typing import Any

from ._yclient import YClient
from .yquote import YQuote


class YFin:
    """
    A Python interface to the Yahoo! Finance API.
    """

    _QUOTE_API: str = "/v7/finance/quote"

    def __init__(self) -> None:
        self._yclient = YClient()

    def get_quotes(self, symbols: list[str]) -> list[YQuote]:
        """
        Retrieve quotes for the given symbols.

        Args:
            symbols (list[str]): The symbols to get quotes for.

        Raises:
            ValueError: If no symbols are provided.

        Returns:
            list[YQuote]: The quotes for the given symbols.
        """
        if symbols is None or len(symbols) == 0:
            logging.error("No symbols provided")
            raise ValueError("No symbols provided")

        # call YClient.call with symbols stripped of whitespace
        json_data: dict[str, Any] = self._yclient.call(
            self._QUOTE_API, {"symbols": ",".join([s.strip() for s in symbols])}
        )

        if json_data is None or "quoteResponse" not in json_data:
            logging.error("No quote response from Yahoo!")
            return []

        if (
            "error" in json_data["quoteResponse"]
            and json_data["quoteResponse"]["error"] is not None
        ):
            logging.error(
                "Error getting response data from Yahoo!: %s",
                json_data["quoteResponse"]["error"]["description"],
            )
            return []

        return [
            YQuote(q) for q in json_data["quoteResponse"]["result"] if q is not None
        ]
