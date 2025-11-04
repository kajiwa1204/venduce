from sqlalchemy import Column, String, DateTime, func
from app.db.database import Base
from ulid import ULID


class User(Base):
    __tablename__ = "users"

    id = Column(String(26), primary_key=True, index=True, default=lambda: str(ULID()))
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


__all__ = ["User"]
