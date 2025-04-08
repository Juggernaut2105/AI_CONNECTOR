# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/taskdb" # Default fallback
    api_auth_token: str = "default_token"
    openai_api_key_file: str = "./openai_api_key.txt" # Default path

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()

# Create the SQLAlchemy engine
# connect_args is needed for SQLite, but usually not for PostgreSQL
# For PostgreSQL:
engine = create_engine(settings.database_url)
# For SQLite (if you wanted to test without Postgres):
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


# Each instance of the SessionLocal class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from
Base = declarative_base()

# Simple function to create tables (run this once manually or integrate into startup)
def create_db_tables():
    print("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating tables: {e}")

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()