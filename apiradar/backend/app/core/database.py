"""
Database engine setup and session management using SQLModel + SQLite.
"""
import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leakhub.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def init_db() -> None:
    """Create all tables if they do not already exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Return a new database session. Caller is responsible for closing it."""
    return Session(engine)
