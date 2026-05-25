#!/bin/bash
export DATABASE_URL="postgresql://test:test@localhost:5432/test"
export REDIS_URL="redis://localhost:6379/15"
export SECRET_KEY="test-secret-key-with-at-least-32-bytes"

venv/bin/python -m unittest -v \
  ./tests/test_register_and_login.py \
  ./tests/test_deposit_withdraw_summary.py \
  ./tests/test_quote.py \
  ./tests/test_quote_cache.py \
  ./tests/test_market_data.py \
  ./tests/test_buy_order.py \
  ./tests/test_portfolio_and_trades.py \
  ./tests/test_sell_order.py
