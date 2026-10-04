from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    """Bazowa klasa dla modeli SQLAlchemy."""


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Ważne: zaimportowanie modeli rejestruje ich tabele w Base.metadata,
# zanim wywołamy create_all().
from models import MunicipalUser, Report, User  # noqa: E402, F401


def init_db() -> None:
    """Włącza PostGIS i tworzy brakujące tabele."""

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Udostępnia sesję bazy dla endpointów FastAPI."""

    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()