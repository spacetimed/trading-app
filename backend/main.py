from fastapi import FastAPI, Depends, HTTPException
from db import engine, get_db

from models import Base, User
from schemas import RegisterPayload, RegisterResponse, \
                    LoginPayload, LoginResponse

from sqlalchemy.orm import Session

import hashlib

app = FastAPI()

Base.metadata.create_all(bind=engine)

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

@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    # check if credentials match
    hashed_password = hash_password(payload.password)
    valid_user = db.query(User).filter(
        User.email == payload.email,
        User.password == hashed_password
    ).first()

    if not valid_user:
        raise HTTPException(status_code=401, detail="incorrect email or password")

    # craft response
    return {
        "id": valid_user.id,
        "email": valid_user.email,
        "message": "login successful",
    }


# helpers
def hash_password(password: str) -> str:
    """return a hashed sha256-representation of the plaintext password"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
