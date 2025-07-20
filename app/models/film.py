from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from .character_film import character_film_association


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    swapi_id = Column(Integer, unique=True, index=True)  # ID from SWAPI
    title = Column(String(200), index=True, nullable=False)
    episode_id = Column(Integer)
    opening_crawl = Column(Text)
    director = Column(String(100))
    producer = Column(String(200))
    release_date = Column(String(20))
    url = Column(String(255))
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Many-to-many relationship with characters
    characters = relationship(
        "Character",
        secondary=character_film_association,
        back_populates="films"
    )

    def __repr__(self):
        return f"<Film(title='{self.title}', episode_id={self.episode_id}, votes={self.votes})>"
