from fastapi import FastAPI, Depends, HTTPException
from db import engine, get_db

from models import Base, User, Transaction
from schemas import RegisterPayload, RegisterResponse, \
                    LoginPayload, LoginResponse, \
                    DepositPayload, DepositResponse, \
                    TokenResponse

from sqlalchemy.orm import Session

import hashlib

from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

Base.metadata.create_all(bind=engine)

# helpers

def hash_password(password: str) -> str:
    """return a hashed sha256-representation of the plaintext password"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


SECRET_KEY = "dev-key-i-will-change-this-later-lol"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINS = 30

def create_access_token(data: dict) -> str:
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINS)
    data = data.copy()
    data.update({"exp": expire_time})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()

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

# end helpers 


# endpoints

@app.get("/health")
def health(): 
    return {"status":"ok"}


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
        password=hashed_password
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
        "token_type": "bearer"
    }


@app.get("/auth/me", response_model=RegisterResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/account/deposit", response_model=DepositResponse)
def deposit(
    payload: DepositPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.cash_balance += payload.amount

    txn = Transaction(
        user_id=current_user.id,
        type="deposit",
        amount=payload.amount
    )

    db.add(txn)
    db.commit()
    db.refresh(current_user)

    return {"cash_balance": current_user.cash_balance}

# end endpoints
