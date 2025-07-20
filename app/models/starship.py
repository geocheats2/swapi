from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Starship(Base):
    __tablename__ = "starships"

    id = Column(Integer, primary_key=True, index=True)
    swapi_id = Column(Integer, unique=True, index=True)  # ID from SWAPI
    name = Column(String(100), index=True, nullable=False)
    model = Column(String(100))
    manufacturer = Column(String(200))
    cost_in_credits = Column(String(50))
    length = Column(String(50))
    max_atmosphering_speed = Column(String(50))
    crew = Column(String(50))
    passengers = Column(String(50))
    cargo_capacity = Column(String(50))
    consumables = Column(String(50))
    hyperdrive_rating = Column(String(50))
    mglt = Column(String(50))
    starship_class = Column(String(100))
    url = Column(String(255))
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Starship(name='{self.name}', model='{self.model}', votes={self.votes})>"
