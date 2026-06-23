from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    teamId = Column(Integer, ForeignKey("teams.id"))
    firstName = Column(String)
    lastName = Column(String)
    fullName = Column(String)
    sourceFilename = Column(String)
    ocrText = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending | verified | rejected
    createdAt = Column(DateTime, default=datetime.utcnow)
    verifiedAt = Column(DateTime, nullable=True)

    team = relationship("Team", back_populates="players")
