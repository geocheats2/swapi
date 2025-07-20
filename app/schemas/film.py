from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FilmBase(BaseModel):
    """Base film schema"""
    title: str
    episode_id: Optional[int] = None
    opening_crawl: Optional[str] = None
    director: Optional[str] = None
    producer: Optional[str] = None
    release_date: Optional[str] = None


class FilmCreate(FilmBase):
    """Schema for creating films"""
    swapi_id: int
    url: Optional[str] = None


class FilmUpdate(BaseModel):
    """Schema for updating films"""
    title: Optional[str] = None
    episode_id: Optional[int] = None
    opening_crawl: Optional[str] = None
    director: Optional[str] = None
    producer: Optional[str] = None
    release_date: Optional[str] = None


class Film(FilmBase):
    """Schema for film responses"""
    id: int
    swapi_id: int
    url: Optional[str] = None
    votes: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FilmResponse(Film):
    """Extended film response with characters"""
    characters: List["CharacterBase"] = []

    model_config = ConfigDict(from_attributes=True)


# Forward reference for circular imports
class CharacterBase(BaseModel):
    id: int
    name: str
    height: Optional[str] = None
    mass: Optional[str] = None
    gender: Optional[str] = None
    votes: int = 0

    model_config = ConfigDict(from_attributes=True)


# Update forward references
FilmResponse.model_rebuild()
