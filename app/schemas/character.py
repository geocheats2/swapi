from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CharacterBase(BaseModel):
    """Base character schema"""
    name: str
    height: Optional[str] = None
    mass: Optional[str] = None
    hair_color: Optional[str] = None
    skin_color: Optional[str] = None
    eye_color: Optional[str] = None
    birth_year: Optional[str] = None
    gender: Optional[str] = None
    homeworld: Optional[str] = None


class CharacterCreate(CharacterBase):
    """Schema for creating characters"""
    swapi_id: int
    url: Optional[str] = None


class CharacterUpdate(BaseModel):
    """Schema for updating characters"""
    name: Optional[str] = None
    height: Optional[str] = None
    mass: Optional[str] = None
    hair_color: Optional[str] = None
    skin_color: Optional[str] = None
    eye_color: Optional[str] = None
    birth_year: Optional[str] = None
    gender: Optional[str] = None
    homeworld: Optional[str] = None


class Character(CharacterBase):
    """Schema for character responses"""
    id: int
    swapi_id: int
    url: Optional[str] = None
    votes: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CharacterResponse(Character):
    """Extended character response with films"""
    films: List["FilmBase"] = []

    model_config = ConfigDict(from_attributes=True)


# Forward reference for circular imports
class FilmBase(BaseModel):
    id: int
    title: str
    episode_id: Optional[int] = None
    director: Optional[str] = None
    release_date: Optional[str] = None
    votes: int = 0

    model_config = ConfigDict(from_attributes=True)


# Update forward references
CharacterResponse.model_rebuild()
