from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    teamId = Column(Integer, ForeignKey("teams.id"), nullable=False)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    fullName = Column(String, nullable=True)
    dateOfBirth = Column(Date, nullable=True)  # e.g., 2005-01-15
    birthYearBE = Column(Integer, nullable=True)  # Calculated from dateOfBirth
    eligibilityStatus = Column(String, default="unknown")  # eligible | over_age | unknown
    eligibilityNote = Column(String, nullable=True)
    sourceFilename = Column(String, nullable=True)
    ocrText = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending | verified | rejected
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verifiedAt = Column(DateTime, nullable=True)

    team = relationship("Team", back_populates="players")
