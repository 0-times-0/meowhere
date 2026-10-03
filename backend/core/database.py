from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE reports
                ADD COLUMN IF NOT EXISTS coat_color VARCHAR(80),
                ADD COLUMN IF NOT EXISTS breed VARCHAR(80),
                ADD COLUMN IF NOT EXISTS sex VARCHAR(30);
        """))
        conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()