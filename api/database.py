from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from api.config import settings


SQLALCHEMY_DATABASE_URL = f'{settings.DB_CONNECTION}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def session():
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db: Session = Depends(get_db)
    return db