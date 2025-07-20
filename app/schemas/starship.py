from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class StarshipBase(BaseModel):
    """Base starship schema"""
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    cost_in_credits: Optional[str] = None
    length: Optional[str] = None
    max_atmosphering_speed: Optional[str] = None
    crew: Optional[str] = None
    passengers: Optional[str] = None
    cargo_capacity: Optional[str] = None
    consumables: Optional[str] = None
    hyperdrive_rating: Optional[str] = None
    mglt: Optional[str] = None
    starship_class: Optional[str] = None


class StarshipCreate(StarshipBase):
    """Schema for creating starships"""
    swapi_id: int
    url: Optional[str] = None


class StarshipUpdate(BaseModel):
    """Schema for updating starships"""
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    cost_in_credits: Optional[str] = None
    length: Optional[str] = None
    max_atmosphering_speed: Optional[str] = None
    crew: Optional[str] = None
    passengers: Optional[str] = None
    cargo_capacity: Optional[str] = None
    consumables: Optional[str] = None
    hyperdrive_rating: Optional[str] = None
    mglt: Optional[str] = None
    starship_class: Optional[str] = None


class Starship(StarshipBase):
    """Schema for starship responses"""
    id: int
    swapi_id: int
    url: Optional[str] = None
    votes: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StarshipResponse(Starship):
    """Extended starship response"""
    pass
