from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, func
from app.models.film import Film
from app.models.character import Character
from app.schemas.film import FilmCreate, FilmUpdate
import logging

logger = logging.getLogger(__name__)


class FilmService:
    """Service for film operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_film(self, film_id: int) -> Optional[Film]:
        """Get film by ID"""
        return self.db.query(Film).options(
            selectinload(Film.characters)
        ).filter(Film.id == film_id).first()
    
    def get_film_by_swapi_id(self, swapi_id: int) -> Optional[Film]:
        """Get film by SWAPI ID"""
        return self.db.query(Film).filter(Film.swapi_id == swapi_id).first()
    
    def get_films(self, skip: int = 0, limit: int = 20) -> tuple[List[Film], int]:
        """Get paginated list of films"""
        query = self.db.query(Film).options(selectinload(Film.characters))
        total = query.count()
        films = query.order_by(Film.votes.desc(), Film.title).offset(skip).limit(limit).all()
        return films, total
    
    def search_films(self, title: str, skip: int = 0, limit: int = 20) -> tuple[List[Film], int]:
        """Search films by title"""
        query = self.db.query(Film).options(selectinload(Film.characters)).filter(
            Film.title.ilike(f"%{title}%")
        )
        total = query.count()
        films = query.order_by(Film.votes.desc(), Film.title).offset(skip).limit(limit).all()
        return films, total
    
    def create_film(self, film_data: FilmCreate) -> Film:
        """Create a new film"""
        db_film = Film(**film_data.model_dump())
        self.db.add(db_film)
        self.db.commit()
        self.db.refresh(db_film)
        logger.info(f"Created film: {db_film.title}")
        return db_film
    
    def update_film(self, film_id: int, film_data: FilmUpdate) -> Optional[Film]:
        """Update an existing film"""
        db_film = self.get_film(film_id)
        if not db_film:
            return None
        
        update_data = film_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_film, field, value)
        
        self.db.commit()
        self.db.refresh(db_film)
        logger.info(f"Updated film: {db_film.title}")
        return db_film
    
    def delete_film(self, film_id: int) -> bool:
        """Delete a film"""
        db_film = self.get_film(film_id)
        if not db_film:
            return False
        
        self.db.delete(db_film)
        self.db.commit()
        logger.info(f"Deleted film: {db_film.title}")
        return True
    
    def vote_for_film(self, film_id: int) -> Optional[Film]:
        """Vote for a film (increment vote count)"""
        db_film = self.get_film(film_id)
        if not db_film:
            return None
        
        # Use SQL update to increment votes
        self.db.query(Film).filter(Film.id == film_id).update(
            {Film.votes: Film.votes + 1}
        )
        self.db.commit()
        
        # Get fresh object with updated votes
        updated_film = self.get_film(film_id)
        if updated_film:
            logger.info(f"Voted for film: {updated_film.title} (votes: {updated_film.votes})")
        return updated_film
    
    def get_top_films(self, limit: int = 10) -> List[Film]:
        """Get top voted films"""
        return self.db.query(Film).order_by(
            Film.votes.desc()
        ).limit(limit).all()
    
    def create_or_update_from_swapi(self, swapi_data: dict) -> Film:
        """Create or update film from SWAPI data"""
        swapi_id = swapi_data.get("swapi_id")
        if swapi_id is None:
            raise ValueError("SWAPI ID is required")
            
        existing = self.get_film_by_swapi_id(swapi_id)
        
        film_data = {
            "swapi_id": swapi_id,
            "title": swapi_data.get("title", ""),
            "episode_id": swapi_data.get("episode_id"),
            "opening_crawl": swapi_data.get("opening_crawl"),
            "director": swapi_data.get("director"),
            "producer": swapi_data.get("producer"),
            "release_date": swapi_data.get("release_date"),
            "url": swapi_data.get("url")
        }
        
        if existing:
            # Update existing film
            for field, value in film_data.items():
                if field != "swapi_id":  # Don't update the ID
                    setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new film
            db_film = Film(**film_data)
            self.db.add(db_film)
            self.db.commit()
            self.db.refresh(db_film)
            return db_film
