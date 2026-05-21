import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env variables
load_dotenv()

# -------- DATABASE CONFIG ---------

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:O-S-N-312@localhost/careerbridge")

# Connect to database with SQLite fallback if MySQL connection fails
try:
    if DATABASE_URL.startswith("mysql"):
        # Quick check if MySQL connection is working (timeout in 2 seconds)
        temp_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 2})
        with temp_engine.connect() as conn:
            pass
        logger.info("Successfully connected to MySQL database.")
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    else:
        engine = create_engine(DATABASE_URL)
except Exception as e:
    logger.warning(f"Failed to connect to MySQL database ({e}). Falling back to local SQLite database.")
    DATABASE_URL = "sqlite:///./career_ai.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# Create session maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# -------- Dependency for FastAPI ---------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

