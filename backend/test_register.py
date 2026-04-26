import os
import sys
import unittest

from fastapi import HTTPException
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
    from main import register
finally:
    MetaData.create_all = original_create_all

from models import Base
from schemas import RegisterPayload


# use an in-memory sqlite db for tests
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RegisterTests(unittest.TestCase):
    def setUp(self):
        # reset tables before each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_register_rejects_duplicate_email(self):
        # first register works, second one fails
        payload = RegisterPayload(email="user@example.com", password="testtest")

        user = register(payload, self.db)

        self.assertEqual(user.email, "user@example.com")
        with self.assertRaises(HTTPException) as context:
            register(payload, self.db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "email already exists")

    def test_register_rejects_short_password(self):
        # pydantic catches this before register runs
        with self.assertRaises(ValidationError):
            RegisterPayload(email="user@example.com", password="short")


if __name__ == "__main__":
    unittest.main()
