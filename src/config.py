from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

DATABASE_URL = 'sqlite:///./book_giveaway.db'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Settings(BaseSettings):
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str

    class Config:
        env_file = '.env'

SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind=engine)
Base = declarative_base()