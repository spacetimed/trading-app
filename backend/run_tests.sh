#!/bin/bash
venv/bin/python -m unittest -v \
  ./test_register_and_login.py \
  ./test_deposit_withdraw_summary.py \
  ./test_quote.py \
  ./test_market_data.py \
  ./test_buy_order.py
