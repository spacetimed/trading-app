import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.schema import MetaData

sys.path.insert(0, os.path.dirname(__file__))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from main import buy_order, deposit, register
finally:
    MetaData.create_all = original_create_all

from models import Base, Position, Trade
from schemas import BuyOrderPayload, DepositPayload, RegisterPayload


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class BuyOrderTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_buy_succeeds_with_enough_cash(self):
        user = register(
            RegisterPayload(email="user@example.com", password="testtest"),
            self.db,
        )
        deposit(DepositPayload(amount=Decimal("1000.00")), user, self.db)

        with patch("main.get_quote_price", return_value=Decimal("100.00")):
            response = buy_order(
                BuyOrderPayload(symbol="aapl", quantity=2),
                user,
                self.db,
            )

        trade = self.db.query(Trade).first()
        position = self.db.query(Position).first()

        self.assertEqual(response["symbol"], "AAPL")
        self.assertEqual(response["quantity"], 2)
        self.assertEqual(response["total_cost"], Decimal("200.00"))
        self.assertEqual(response["cash_balance"], Decimal("800.00"))
        self.assertEqual(trade.symbol, "AAPL")
        self.assertEqual(trade.side, "buy")
        self.assertEqual(position.symbol, "AAPL")
        self.assertEqual(position.quantity, 2)
        self.assertEqual(position.avg_cost, Decimal("100.00"))

    def test_buy_fails_without_enough_cash(self):
        user = register(
            RegisterPayload(email="user@example.com", password="testtest"),
            self.db,
        )

        with patch("main.get_quote_price", return_value=Decimal("100.00")):
            with self.assertRaises(HTTPException) as context:
                buy_order(
                    BuyOrderPayload(symbol="aapl", quantity=2),
                    user,
                    self.db,
                )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "insufficient cash")
        self.assertIsNone(self.db.query(Trade).first())
        self.assertIsNone(self.db.query(Position).first())


if __name__ == "__main__":
    unittest.main()
