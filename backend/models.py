from sqlalchemy import Column, Integer, String
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    url = Column(String, nullable=False)

    prediction = Column(String, nullable=False)

    # Probability (0–1)
    confidence = Column(Float, nullable=False)

    # Risk score (0–100)
    risk_score = Column(Float, nullable=False)

    scanned_at = Column(DateTime(timezone=True), server_default=func.now())