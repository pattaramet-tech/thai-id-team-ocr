from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    ageGroup = Column(String, nullable=False)  # e.g., U18, U16, U14
    gender = Column(String, nullable=False)  # e.g., Male, Female, Mixed
    division = Column(String, nullable=True)  # Optional division name
    competitionYearBE = Column(Integer, default=2569)  # Buddhist Era year
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")
