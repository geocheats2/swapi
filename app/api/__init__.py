from .characters import router as characters_router
from .films import router as films_router  
from .starships import router as starships_router

__all__ = [
    "characters_router",
    "films_router", 
    "starships_router"
]
