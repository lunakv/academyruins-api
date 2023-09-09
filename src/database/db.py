import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_user = os.environ["DB_USER"]
_pass = os.environ["DB_PASS"]
_host = os.environ["DB_HOST"]
_db = os.environ["DB_DATABASE"]

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{_user}:{_pass}@{_host}/{_db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
