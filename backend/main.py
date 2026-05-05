from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from db import engine, get_db
from models import Base, Transaction, User
from schemas import (
    AccountSummaryResponse,
    DepositPayload,
    DepositResponse,
    LoginPayload,
    RegisterPayload,
    RegisterResponse,
    TokenResponse,
    QuoteResponse,
    WithdrawPayload,
    WithdrawResponse,
)


# setup
app = FastAPI()
Base.metadata.create_all(bind=engine)
security = HTTPBearer()


# constants
SECRET_KEY = "dev-key-i-will-change-this-later-lol"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINS = 30

FAKE_QUOTES = {
    "AAPL": Decimal("175.00"),
    "MSFT": Decimal("425.00"),
}


# helpers
def hash_password(password: str) -> str:
    """return a hashed sha256-representation of the plaintext password"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_access_token(data: dict) -> str:
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINS)
    data = data.copy()
    data.update({"exp": expire_time})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """return a logged in user model from a token"""
    token = credentials.credentials

    # check token basic validity
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")

    # check email key exists
    if not email:
        raise HTTPException(status_code=401, detail="invalid token")

    # check valid user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="invalid token")

    return user


def get_quote_price(symbol: str) -> Decimal | None:
    return FAKE_QUOTES.get(symbol)


# endpoints
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
def db_check(db: Session = Depends(get_db)):
    return {"ok": True}


@app.post("/auth/register", response_model=RegisterResponse)
def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    # check for duplicate users
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="email already exists")

    # create/save User (model) with hashed password
    # craft response
    hashed_password = hash_password(payload.password)
    user = User(
        email=payload.email,
        password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # return the created user
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    # check if credentials match
    hashed_password = hash_password(payload.password)
    valid_user = db.query(User).filter(
        User.email == payload.email,
        User.password == hashed_password
    ).first()

    if not valid_user:
        raise HTTPException(status_code=401, detail="incorrect email or password")

    access_token = create_access_token({"sub": valid_user.email})
    return {
        "token": access_token,
        "token_type": "bearer",
    }


@app.get("/auth/me", response_model=RegisterResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/account/deposit", response_model=DepositResponse)
def deposit(
    payload: DepositPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.cash_balance += payload.amount

    txn = Transaction(
        user_id=current_user.id,
        type="deposit",
        amount=payload.amount,
    )

    db.add(txn)
    db.commit()
    db.refresh(current_user)

    return {"cash_balance": current_user.cash_balance}


@app.post("/account/withdraw", response_model=WithdrawResponse)
def withdraw(
    payload: WithdrawPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.amount > current_user.cash_balance:
        raise HTTPException(status_code=400, detail="insufficient cash")

    current_user.cash_balance -= payload.amount

    txn = Transaction(
        user_id=current_user.id,
        type="withdraw",
        amount=payload.amount,
    )

    db.add(txn)
    db.commit()
    db.refresh(current_user)

    return {"cash_balance": current_user.cash_balance}


@app.get("/account/summary", response_model=AccountSummaryResponse)
def account_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    total_deposits = sum(
        (txn.amount for txn in transactions if txn.type == "deposit"),
        Decimal("0.00")
    )
    total_withdrawals = sum(
        (txn.amount for txn in transactions if txn.type == "withdraw"),
        Decimal("0.00")
    )

    return {
        "cash_balance": current_user.cash_balance,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "transaction_count": len(transactions),
    }


@app.get("/market/quote/{symbol}", response_model=QuoteResponse)
def get_quote(symbol: str):
    symbol = symbol.upper()
    price = get_quote_price(symbol)

    if price is None:
        raise HTTPException(status_code=404, detail="symbol not found")

    return {
        "symbol": symbol,
        "price": price,
    }
