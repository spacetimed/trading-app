import os
import sys
import unittest
from decimal import Decimal

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.schema import MetaData

sys.path.insert(0, os.path.dirname(__file__))

# skip postgres table creation when importing the app
original_create_all = MetaData.create_all
MetaData.create_all = lambda self, bind=None, tables=None, checkfirst=True: None
try:
    from main import deposit, register
finally:
    MetaData.create_all = original_create_all

from models import Base, Transaction
from schemas import DepositPayload, RegisterPayload


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DepositTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_deposit_increases_cash_and_creates_transaction(self):
        user = register(
            RegisterPayload(email="user@example.com", password="testtest"),
            self.db,
        )

        response = deposit(
            DepositPayload(amount=Decimal("100.00")),
            user,
            self.db,
        )
        transaction = self.db.query(Transaction).first()

        self.assertEqual(response["cash_balance"], Decimal("100.00"))
        self.assertEqual(user.cash_balance, Decimal("100.00"))
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.type, "deposit")
        self.assertEqual(transaction.amount, Decimal("100.00"))

    def test_deposit_rejects_negative_amount(self):
        with self.assertRaises(ValidationError):
            DepositPayload(amount=Decimal("-1.00"))


if __name__ == "__main__":
    unittest.main()
