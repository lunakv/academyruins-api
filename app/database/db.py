import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{os.environ["DB_USER"]}:{os.environ["DB_PASS"]}@{os.environ["DB_HOST"]}/{os.environ["DB_DATABASE"]}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, future=True)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
