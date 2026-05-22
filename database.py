import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# ── Database URL ──────────────────────────────────────────────
# Uses SQLite locally by default (zero config, no server needed).
# Switch to MySQL/Postgres by setting DATABASE_URL in your .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./career_ai.db")

# SQLite needs check_same_thread=False; other DBs ignore it
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
