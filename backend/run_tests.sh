#!/bin/bash
venv/bin/python -m unittest -v \
  ./tests/test_register_and_login.py \
  ./tests/test_deposit_withdraw_summary.py \
  ./tests/test_quote.py \
  ./tests/test_quote_cache.py \
  ./tests/test_market_data.py \
  ./tests/test_buy_order.py \
  ./tests/test_portfolio_and_trades.py \
  ./tests/test_sell_order.py
