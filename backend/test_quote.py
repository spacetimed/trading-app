import os
import sys
import unittest
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.sql.schema import MetaData

sys.path.insert(0, os.path.dirname(__file__))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from main import get_quote
finally:
    MetaData.create_all = original_create_all


class QuoteTests(unittest.TestCase):
    def test_quote_returns_hardcoded_symbol(self):
        response = get_quote("aapl")

        self.assertEqual(response["symbol"], "AAPL")
        self.assertEqual(response["price"], Decimal("175.00"))

    def test_quote_rejects_unsupported_symbol(self):
        with self.assertRaises(HTTPException) as context:
            get_quote("zzzz")

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "symbol not found")


if __name__ == "__main__":
    unittest.main()
