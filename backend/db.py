from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()




# Load environment variables from .env


# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")

"""
_db_url = os.getenv("DATABASE_URL")
if _db_url:
    engine = create_engine(_db_url, echo=False)
else:
    DB_PATH = Path(__file__).with_name("app.db")
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    
"""

def init_db() -> None:
    import models  # noqa: F401
    SQLModel.metadata.create_all(engine)
    # Minimal migration: ensure waiverUrl column exists (Postgres)
    try:
        with engine.begin() as conn:
            conn.execute(text('ALTER TABLE "entry" ADD COLUMN IF NOT EXISTS "waiverUrl" TEXT'))
            conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "verified" BOOLEAN DEFAULT FALSE'))
    except Exception:
        # Safe to ignore if DB is not Postgres or lacks privileges
        pass


def get_session():
    with Session(engine) as session:
        yield session

