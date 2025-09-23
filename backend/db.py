from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path


DB_PATH = Path(__file__).with_name("app.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db() -> None:
    from . import models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


