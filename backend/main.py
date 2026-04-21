from fastapi import FastAPI, Depends

from db import engine, get_db
from models import Base

from sqlalchemy.orm import Session

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(): 
    return {"status":"ok"}

@app.get("/db-test")
def db_check(db: Session = Depends(get_db)):
    return {"ok": True}