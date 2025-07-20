from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# Association table for many-to-many relationship between characters and films
character_film_association = Table(
    'character_films',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('film_id', Integer, ForeignKey('films.id'), primary_key=True)
)
