import os
import sys
import unittest
from decimal import Decimal

from sqlalchemy.sql.schema import MetaData

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from main import build_stooq_quote_url, format_stooq_symbol, parse_stooq_csv
finally:
    MetaData.create_all = original_create_all


class MarketDataTests(unittest.TestCase):
    def test_format_stooq_symbol(self):
        self.assertEqual(format_stooq_symbol(" AAPL "), "aapl.us")

    def test_build_stooq_quote_url(self):
        self.assertEqual(
            build_stooq_quote_url("AAPL"),
            "https://stooq.com/q/l/?s=aapl.us&f=sd2t2ohlcv&h&e=csv",
        )

    def test_parse_stooq_csv_returns_close_price(self):
        csv_text = (
            "Symbol,Date,Time,Open,High,Low,Close,Volume\n"
            "AAPL.US,2026-05-04,22:00:21,279.655,280.63,274.8601,276.873,46627808\n"
        )

        self.assertEqual(parse_stooq_csv(csv_text), Decimal("276.873"))

    def test_parse_stooq_csv_returns_none_for_missing_price(self):
        csv_text = (
            "Symbol,Date,Time,Open,High,Low,Close,Volume\n"
            "ZZZZ.US,N/D,N/D,N/D,N/D,N/D,N/D,N/D\n"
        )

        self.assertIsNone(parse_stooq_csv(csv_text))


if __name__ == "__main__":
    unittest.main()
