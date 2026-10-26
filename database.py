
from sqlalchemy import create_engine # type: ignore
import sqlalchemy.orm

DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sqlalchemy.orm.sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = sqlalchemy.orm.declarative_base()
