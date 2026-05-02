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
    from main import ALGORITHM, SECRET_KEY, get_current_user, login, me, register
finally:
    MetaData.create_all = original_create_all

import jwt

from models import Base
from schemas import LoginPayload, RegisterPayload


class TestCredentials:
    def __init__(self, token):
        self.credentials = token


# use an in-memory sqlite db for tests
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RegisterAndLoginTests(unittest.TestCase):
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

    def test_login_succeeds_after_register(self):
        register_payload = RegisterPayload(
            email="user@example.com",
            password="testtest",
        )
        login_payload = LoginPayload(
            email="user@example.com",
            password="testtest",
        )

        register(register_payload, self.db)
        response = login(login_payload, self.db)
        token_payload = jwt.decode(
            response["token"],
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        self.assertIn("token", response)
        self.assertEqual(response["token_type"], "bearer")
        self.assertEqual(token_payload["sub"], "user@example.com")

    def test_login_rejects_missing_email(self):
        # no user has been registered in this fresh db
        payload = LoginPayload(email="missing@example.com", password="testtest")

        with self.assertRaises(HTTPException) as context:
            login(payload, self.db)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "incorrect email or password")

    def test_login_rejects_wrong_password(self):
        # register first, then try the wrong password
        register_payload = RegisterPayload(
            email="user@example.com",
            password="testtest",
        )
        login_payload = LoginPayload(
            email="user@example.com",
            password="wrongpassword",
        )

        register(register_payload, self.db)
        with self.assertRaises(HTTPException) as context:
            login(login_payload, self.db)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "incorrect email or password")

    def test_me_returns_current_user_from_token(self):
        register_payload = RegisterPayload(
            email="user@example.com",
            password="testtest",
        )
        login_payload = LoginPayload(
            email="user@example.com",
            password="testtest",
        )

        user = register(register_payload, self.db)
        login_response = login(login_payload, self.db)
        credentials = TestCredentials(login_response["token"])
        current_user = get_current_user(credentials, self.db)
        response = me(current_user)

        self.assertEqual(response.id, user.id)
        self.assertEqual(response.email, "user@example.com")



if __name__ == "__main__":
    unittest.main()
