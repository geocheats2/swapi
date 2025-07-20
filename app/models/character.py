from sqlalchemy import Column, Integer, String, Text, DateTime, Float, func
from sqlalchemy.orm import relationship
from app.database import Base
from .character_film import character_film_association


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    swapi_id = Column(Integer, unique=True, index=True)  # ID from SWAPI
    name = Column(String(100), index=True, nullable=False)
    height = Column(String(20))
    mass = Column(String(20))
    hair_color = Column(String(50))
    skin_color = Column(String(50))
    eye_color = Column(String(50))
    birth_year = Column(String(20))
    gender = Column(String(20))
    homeworld = Column(String(100))
    url = Column(String(255))
    votes = Column(Integer, default=0)
    rating = Column(Float, default=0.0)  # Average rating out of 5.0
    rating_count = Column(Integer, default=0)  # Number of ratings
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Many-to-many relationship with films
    films = relationship(
        "Film",
        secondary=character_film_association,
        back_populates="characters"
    )

    def __repr__(self):
        return f"<Character(name='{self.name}', votes={self.votes})>"
