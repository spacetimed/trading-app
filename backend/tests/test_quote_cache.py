import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import patch

import redis
from sqlalchemy.sql.schema import MetaData

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from cache import (
        QUOTE_CACHE_TTL_SECONDS,
        build_quote_cache_key,
        get_cached_quote,
        set_cached_quote,
    )
    from main import get_quote_price
finally:
    MetaData.create_all = original_create_all


class QuoteCacheTests(unittest.TestCase):
    def test_build_quote_cache_key_normalizes_symbol(self):
        self.assertEqual(build_quote_cache_key(" aapl "), "quote:AAPL")

    def test_get_quote_price_returns_cached_price(self):
        with (
            patch("main.get_cached_quote", return_value="123.45"),
            patch("main.get_yahoo_quote_price") as yahoo_quote,
            patch("main.get_stooq_quote_price") as stooq_quote,
        ):
            price = get_quote_price("aapl")

        self.assertEqual(price, Decimal("123.45"))
        yahoo_quote.assert_not_called()
        stooq_quote.assert_not_called()

    def test_get_quote_price_caches_provider_price(self):
        with (
            patch("main.get_cached_quote", return_value=None),
            patch("main.get_yahoo_quote_price", return_value=Decimal("234.56")),
            patch("main.set_cached_quote") as cache_set,
        ):
            price = get_quote_price("nvda")

        self.assertEqual(price, Decimal("234.56"))
        cache_set.assert_called_once_with("NVDA", "234.56")

    def test_cache_helpers_ignore_redis_errors(self):
        with patch("cache.get_redis_client") as get_client:
            get_client.return_value.get.side_effect = redis.RedisError("redis down")

            self.assertIsNone(get_cached_quote("AAPL"))

    def test_set_cached_quote_uses_ttl(self):
        with patch("cache.get_redis_client") as get_client:
            set_cached_quote("AAPL", "175.00")

        get_client.return_value.setex.assert_called_once_with(
            "quote:AAPL",
            QUOTE_CACHE_TTL_SECONDS,
            "175.00",
        )


if __name__ == "__main__":
    unittest.main()
