"""Database engine and session factory."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def normalize_database_url(url: str) -> str:
    """Normalize common hosted PostgreSQL URLs for psycopg 3."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def build_engine(url: str):
    url = normalize_database_url(url)
    if url.startswith("sqlite:"):
        Path("data").mkdir(exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


_engine = None
_SessionLocal = None


def configure_database(url: str):
    global _engine, _SessionLocal
    _engine = build_engine(url)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(_engine)
    return _engine


def get_session_factory():
    if _SessionLocal is None:
        raise RuntimeError("Database is not configured")
    return _SessionLocal
