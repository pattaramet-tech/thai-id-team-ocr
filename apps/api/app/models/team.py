from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ageGroup = Column(String)
    gender = Column(String)
    createdAt = Column(DateTime, default=datetime.utcnow)

    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")
