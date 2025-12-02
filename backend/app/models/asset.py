from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, JSON, ForeignKey
from app.db.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=True, index=True)
    purpose = Column(String(32), nullable=False, index=True)
    path = Column(String(1024), nullable=False)
    meta = Column(JSON, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


__all__ = ["Asset"]
