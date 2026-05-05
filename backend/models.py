from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    cash_balance = Column(Numeric(12, 2), nullable=False, default=0)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # deposit / withdraw
    amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=utc_now)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)  # buy / sell
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=utc_now)


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    avg_cost = Column(Numeric(12, 2), nullable=False)
