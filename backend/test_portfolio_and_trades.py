import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.schema import MetaData

sys.path.insert(0, os.path.dirname(__file__))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from main import buy_order, deposit, portfolio, register, trades
finally:
    MetaData.create_all = original_create_all

from models import Base
from schemas import BuyOrderPayload, DepositPayload, RegisterPayload


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PortfolioAndTradesTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_portfolio_returns_positions_after_buy(self):
        user = register(
            RegisterPayload(email="user@example.com", password="testtest"),
            self.db,
        )
        deposit(DepositPayload(amount=Decimal("1000.00")), user, self.db)

        with patch("main.get_quote_price", return_value=Decimal("100.00")):
            buy_order(BuyOrderPayload(symbol="aapl", quantity=2), user, self.db)

        positions = portfolio(user, self.db)

        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].symbol, "AAPL")
        self.assertEqual(positions[0].quantity, 2)
        self.assertEqual(positions[0].avg_cost, Decimal("100.00"))

    def test_trades_returns_history_after_buy(self):
        user = register(
            RegisterPayload(email="user@example.com", password="testtest"),
            self.db,
        )
        deposit(DepositPayload(amount=Decimal("1000.00")), user, self.db)

        with patch("main.get_quote_price", return_value=Decimal("100.00")):
            buy_order(BuyOrderPayload(symbol="aapl", quantity=2), user, self.db)

        trade_history = trades(user, self.db)

        self.assertEqual(len(trade_history), 1)
        self.assertEqual(trade_history[0].symbol, "AAPL")
        self.assertEqual(trade_history[0].side, "buy")
        self.assertEqual(trade_history[0].quantity, 2)
        self.assertEqual(trade_history[0].price, Decimal("100.00"))


if __name__ == "__main__":
    unittest.main()
