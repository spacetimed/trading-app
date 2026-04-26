from fastapi import FastAPI, Depends, HTTPException
from db import engine, get_db

from models import Base, User
from schemas import RegisterPayload, RegisterResponse

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
    hashed_password = hashlib.sha256(payload.password.encode('utf-8')).hexdigest()
    user = User(
        email=payload.email,
        password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # return the created user
    return user