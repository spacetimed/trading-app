import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
from io import StringIO
from urllib.request import urlopen

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from db import engine, get_db
from models import (
    Base,
    Position,
    Transaction,
    Trade,
    User,
)

from schemas import (
    AccountSummaryResponse,
    BuyOrderPayload,
    BuyOrderResponse,
    DepositPayload,
    DepositResponse,
    LoginPayload,
    PositionResponse,
    RegisterPayload,
    RegisterResponse,
    TokenResponse,
    TradeResponse,
    QuoteResponse,
    SellOrderPayload,
    SellOrderResponse,
    WithdrawPayload,
    WithdrawResponse,
)


# setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    try:
        stooq_price = get_stooq_quote_price(symbol)
    except Exception:
        stooq_price = None

    if stooq_price is not None:
        return stooq_price

    return FAKE_QUOTES.get(symbol)


def format_stooq_symbol(symbol: str) -> str:
    """e.g. f('AAPL') -> 'aapl.us'"""
    return f"{symbol.strip().lower()}.us"


def build_stooq_quote_url(symbol: str) -> str:
    stooq_symbol = format_stooq_symbol(symbol)
    return f"https://stooq.com/q/l/?s={stooq_symbol}&f=sd2t2ohlcv&h&e=csv"


def fetch_stooq_csv(symbol: str) -> str:
    url = build_stooq_quote_url(symbol)
    with urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def parse_stooq_csv(csv_text: str) -> Decimal | None:
    """turn the CSV response into a dictionary and select and return the close price"""
    reader = csv.DictReader(StringIO(csv_text))
    row = next(reader, None)
    if not row:
        return None

    close = row.get("Close", "").strip()
    if not close or close == "N/D":
        return None

    try:
        return Decimal(close)
    except InvalidOperation:
        return None


def get_stooq_quote_price(symbol: str) -> Decimal | None:
    csv_text = fetch_stooq_csv(symbol)
    return parse_stooq_csv(csv_text)


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


@app.post("/orders/buy", response_model=BuyOrderResponse)
def buy_order(
    payload: BuyOrderPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # sanitize
    symbol = payload.symbol.upper()

    # get current price
    price = get_quote_price(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail="symbol not found")

    # check cash
    total_cost = price * payload.quantity
    if total_cost > current_user.cash_balance:
        raise HTTPException(status_code=400, detail="insufficient cash")

    # update cash/records => create/update position
    current_user.cash_balance -= total_cost
    trade = Trade(
        user_id=current_user.id,
        symbol=symbol,
        side="buy",
        quantity=payload.quantity,
        price=price,
    )
    db.add(trade)

    position = db.query(Position).filter(
        Position.user_id == current_user.id,
        Position.symbol == symbol,
    ).first()

    if not position:
        position = Position(
            user_id=current_user.id,
            symbol=symbol,
            quantity=payload.quantity,
            avg_cost=price,
        )
        db.add(position)
    else:
        old_quantity = position.quantity
        new_quantity = old_quantity + payload.quantity

        position.avg_cost = (
            (old_quantity * position.avg_cost) + (payload.quantity * price)
        ) / new_quantity
        position.quantity = new_quantity

    db.commit()
    db.refresh(current_user)

    # return result
    return {
        "symbol": symbol,
        "quantity": payload.quantity,
        "price": price,
        "total_cost": total_cost,
        "cash_balance": current_user.cash_balance,
    }


@app.get("/portfolio", response_model=list[PositionResponse])
def portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    positions = db.query(Position).filter(
        Position.user_id == current_user.id
    ).all()

    portfolio_items = []

    for position in positions:
        current_price = get_quote_price(position.symbol)
        if current_price is None:
            current_price = position.avg_cost

        cost_basis = position.quantity * position.avg_cost
        market_value = position.quantity * current_price
        unrealized_gain_loss = market_value - cost_basis

        if cost_basis == 0:
            unrealized_gain_loss_percent = Decimal("0")
        else:
            unrealized_gain_loss_percent = (
                unrealized_gain_loss / cost_basis
            ) * Decimal("100")

        unrealized_gain_loss_percent = unrealized_gain_loss_percent.quantize(
            Decimal("0.01")
        )

        portfolio_items.append({
            "symbol": position.symbol,
            "quantity": position.quantity,
            "avg_cost": position.avg_cost,
            "current_price": current_price,
            "cost_basis": cost_basis,
            "market_value": market_value,
            "unrealized_gain_loss": unrealized_gain_loss,
            "unrealized_gain_loss_percent": unrealized_gain_loss_percent,
        })

    return portfolio_items


@app.get("/trades", response_model=list[TradeResponse])
def trades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Trade).filter(
        Trade.user_id == current_user.id
    ).order_by(Trade.created_at.asc()).all()


@app.post("/orders/sell", response_model=SellOrderResponse)
def sell_order(
    payload: SellOrderPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    symbol = payload.symbol.upper()

    price = get_quote_price(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail="symbol not found")

    # find position
    position = db.query(Position).filter(
        Position.user_id == current_user.id,
        Position.symbol == symbol,
    ).first()

    if not position:
        raise HTTPException(status_code=400, detail="no shares held")

    if payload.quantity > position.quantity:
        raise HTTPException(status_code=400, detail="not enough shares")

    # update cash/trade
    total_proceeds = price * payload.quantity
    current_user.cash_balance += total_proceeds

    trade = Trade(
        user_id=current_user.id,
        symbol=symbol,
        side="sell",
        quantity=payload.quantity,
        price=price,
    )
    db.add(trade)

    # update|delete position
    position.quantity -= payload.quantity
    if position.quantity == 0:
        db.delete(position)

    db.commit()
    db.refresh(current_user)

    # return SellOrderResponse
    return {
        "symbol": symbol,
        "quantity": payload.quantity,
        "price": price,
        "total_proceeds": total_proceeds,
        "cash_balance": current_user.cash_balance,
    }
