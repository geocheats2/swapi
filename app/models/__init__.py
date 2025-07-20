# Import all models here for easy access
from .character import Character
from .film import Film
from .starship import Starship
from .character_film import character_film_association

__all__ = [
    "Character",
    "Film", 
    "Starship",
    "character_film_association"
]
