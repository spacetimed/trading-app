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

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from main import buy_order, deposit, register, sell_order
finally:
    MetaData.create_all = original_create_all

from models import Base, Position, Trade
from schemas import (
    BuyOrderPayload,
    DepositPayload,
    RegisterPayload,
    SellOrderPayload,
)


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class SellOrderTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def create_user_with_position(self):
        user = register(
            RegisterPayload(email="user@example.com", password="testtest"),
            self.db,
        )
        deposit(DepositPayload(amount=Decimal("1000.00")), user, self.db)

        with patch("main.get_quote_price", return_value=Decimal("100.00")):
            buy_order(BuyOrderPayload(symbol="aapl", quantity=2), user, self.db)

        return user

    def test_sell_succeeds_with_enough_shares(self):
        user = self.create_user_with_position()

        with patch("main.get_quote_price", return_value=Decimal("120.00")):
            response = sell_order(
                SellOrderPayload(symbol="aapl", quantity=1),
                user,
                self.db,
            )

        position = self.db.query(Position).first()
        trades = self.db.query(Trade).order_by(Trade.id.asc()).all()

        self.assertEqual(response["symbol"], "AAPL")
        self.assertEqual(response["quantity"], 1)
        self.assertEqual(response["total_proceeds"], Decimal("120.00"))
        self.assertEqual(response["cash_balance"], Decimal("920.00"))
        self.assertEqual(position.quantity, 1)
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[-1].side, "sell")

    def test_sell_fails_without_enough_shares(self):
        user = self.create_user_with_position()

        with patch("main.get_quote_price", return_value=Decimal("120.00")):
            with self.assertRaises(HTTPException) as context:
                sell_order(
                    SellOrderPayload(symbol="aapl", quantity=3),
                    user,
                    self.db,
                )

        position = self.db.query(Position).first()
        trades = self.db.query(Trade).all()

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "not enough shares")
        self.assertEqual(position.quantity, 2)
        self.assertEqual(len(trades), 1)


if __name__ == "__main__":
    unittest.main()
