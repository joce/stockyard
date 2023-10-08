import unittest

from appui._enums import SortDirection
from appui.quote_table_state import QuoteTableState
from yfinance import YFinance

# pylint: disable=protected-access


class TestQuoteTableState(unittest.TestCase):
    def setUp(self):
        self.yfin = YFinance()
        self.qts = QuoteTableState(self.yfin)

    def test_load_regular_config(self):
        config = {
            "columns": ["ticker", "last", "change_percent"],
            "sort_column": "last",
            "sort_direction": "ASCENDING",
            "quotes": ["AAPL", "F", "VT"],
            "query_frequency": 15,
        }
        self.qts.load_config(config)
        self.assertEqual(self.qts._columns_keys, config["columns"])
        self.assertEqual(self.qts._sort_column_key, config["sort_column"])
        self.assertEqual(self.qts._sort_direction.name, config["sort_direction"])
        self.assertEqual(self.qts._quotes_symbols, config["quotes"])
        self.assertEqual(self.qts._query_frequency, config["query_frequency"])

    def test_load_empty_config(self):
        config = {}
        self.qts.load_config(config)
        self.assertEqual(self.qts._columns_keys, QuoteTableState._DEFAULT_COLUMN_KEYS)
        self.assertEqual(
            self.qts._sort_column_key, QuoteTableState._DEFAULT_COLUMN_KEYS[0]
        )
        self.assertEqual(
            self.qts._sort_direction, QuoteTableState._DEFAULT_SORT_DIRECTION
        )
        self.assertEqual(self.qts._quotes_symbols, QuoteTableState._DEFAULT_QUOTES)
        self.assertEqual(
            self.qts._query_frequency, QuoteTableState._DEFAULT_QUERY_FREQUENCY
        )

    def test_load_invalid_columns(self):
        config = {
            "columns": ["ticker", "truly_not_a_column", "last"],
        }
        self.qts.load_config(config)
        self.assertEqual(self.qts._columns_keys, ["ticker", "last"])

    def test_load_invalid_sort_column(self):
        config = {
            "columns": ["ticker", "last", "change_percent"],
            "sort_column": "truly_not_a_column",
        }
        self.qts.load_config(config)
        self.assertEqual(self.qts._sort_column_key, "ticker")

    def test_load_invalid_sort_direction(self):
        config = {
            "sort_direction": "AMAZING",
        }
        self.qts.load_config(config)
        self.assertEqual(
            self.qts._sort_direction, QuoteTableState._DEFAULT_SORT_DIRECTION
        )

    def test_load_alternate_sort_direction(self):
        config = {
            "sort_direction": "DESC",
        }
        self.qts.load_config(config)
        self.assertEqual(self.qts._sort_direction, SortDirection.DESCENDING)

    def test_load_invalid_query_frequency(self):
        config = {
            "query_frequency": 0,
        }
        self.qts.load_config(config)
        self.assertEqual(
            self.qts._query_frequency, QuoteTableState._DEFAULT_QUERY_FREQUENCY
        )
