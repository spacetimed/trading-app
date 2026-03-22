from sqlalchemy import create_engine

DATABASE_URL = "postgresql://0x@localhost:5432/trading_app"
engine = create_engine(DATABASE_URL)