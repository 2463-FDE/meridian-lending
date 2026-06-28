"""SQLAlchemy engine/session (lazy).

Added during the in-house "let's use an ORM" push. Only the newer read paths
(application listing + detail) went through SQLAlchemy; the older write paths in
intake.py / decision.py still use raw psycopg2 (db.py). Partial migration — never finished.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL

_engine = None
_Session = None


def _init():
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        _Session = sessionmaker(bind=_engine, autoflush=False, future=True)


def get_session():
    """Yield a session (FastAPI dependency). Engine is created on first use only."""
    _init()
    session = _Session()
    try:
        yield session
    finally:
        session.close()
