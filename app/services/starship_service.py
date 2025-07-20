from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.starship import Starship
from app.schemas.starship import StarshipCreate, StarshipUpdate
import logging

logger = logging.getLogger(__name__)


class StarshipService:
    """Service for starship operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_starship(self, starship_id: int) -> Optional[Starship]:
        """Get starship by ID"""
        return self.db.query(Starship).filter(Starship.id == starship_id).first()
    
    def get_starship_by_swapi_id(self, swapi_id: int) -> Optional[Starship]:
        """Get starship by SWAPI ID"""
        return self.db.query(Starship).filter(Starship.swapi_id == swapi_id).first()
    
    def get_starships(self, skip: int = 0, limit: int = 20) -> tuple[List[Starship], int]:
        """Get paginated list of starships"""
        query = self.db.query(Starship)
        total = query.count()
        starships = query.order_by(Starship.votes.desc(), Starship.name).offset(skip).limit(limit).all()
        return starships, total
    
    def search_starships(self, name: str, skip: int = 0, limit: int = 20) -> tuple[List[Starship], int]:
        """Search starships by name"""
        query = self.db.query(Starship).filter(
            Starship.name.ilike(f"%{name}%")
        )
        total = query.count()
        starships = query.order_by(Starship.votes.desc(), Starship.name).offset(skip).limit(limit).all()
        return starships, total
    
    def create_starship(self, starship_data: StarshipCreate) -> Starship:
        """Create a new starship"""
        db_starship = Starship(**starship_data.model_dump())
        self.db.add(db_starship)
        self.db.commit()
        self.db.refresh(db_starship)
        logger.info(f"Created starship: {db_starship.name}")
        return db_starship
    
    def update_starship(self, starship_id: int, starship_data: StarshipUpdate) -> Optional[Starship]:
        """Update an existing starship"""
        db_starship = self.get_starship(starship_id)
        if not db_starship:
            return None
        
        update_data = starship_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_starship, field, value)
        
        self.db.commit()
        self.db.refresh(db_starship)
        logger.info(f"Updated starship: {db_starship.name}")
        return db_starship
    
    def delete_starship(self, starship_id: int) -> bool:
        """Delete a starship"""
        db_starship = self.get_starship(starship_id)
        if not db_starship:
            return False
        
        self.db.delete(db_starship)
        self.db.commit()
        logger.info(f"Deleted starship: {db_starship.name}")
        return True
    
    def vote_for_starship(self, starship_id: int) -> Optional[Starship]:
        """Vote for a starship (increment vote count)"""
        db_starship = self.get_starship(starship_id)
        if not db_starship:
            return None
        
        # Use SQL update to increment votes
        self.db.query(Starship).filter(Starship.id == starship_id).update(
            {Starship.votes: Starship.votes + 1}
        )
        self.db.commit()
        
        # Get fresh object with updated votes
        updated_starship = self.get_starship(starship_id)
        if updated_starship:
            logger.info(f"Voted for starship: {updated_starship.name} (votes: {updated_starship.votes})")
        return updated_starship
    
    def get_top_starships(self, limit: int = 10) -> List[Starship]:
        """Get top voted starships"""
        return self.db.query(Starship).order_by(
            Starship.votes.desc()
        ).limit(limit).all()
    
    def create_or_update_from_swapi(self, swapi_data: dict) -> Starship:
        """Create or update starship from SWAPI data"""
        swapi_id = swapi_data.get("swapi_id")
        if swapi_id is None:
            raise ValueError("SWAPI ID is required")
            
        existing = self.get_starship_by_swapi_id(swapi_id)
        
        starship_data = {
            "swapi_id": swapi_id,
            "name": swapi_data.get("name", ""),
            "model": swapi_data.get("model"),
            "manufacturer": swapi_data.get("manufacturer"),
            "cost_in_credits": swapi_data.get("cost_in_credits"),
            "length": swapi_data.get("length"),
            "max_atmosphering_speed": swapi_data.get("max_atmosphering_speed"),
            "crew": swapi_data.get("crew"),
            "passengers": swapi_data.get("passengers"),
            "cargo_capacity": swapi_data.get("cargo_capacity"),
            "consumables": swapi_data.get("consumables"),
            "hyperdrive_rating": swapi_data.get("hyperdrive_rating"),
            "mglt": swapi_data.get("MGLT"),
            "starship_class": swapi_data.get("starship_class"),
            "url": swapi_data.get("url")
        }
        
        if existing:
            # Update existing starship
            for field, value in starship_data.items():
                if field != "swapi_id":  # Don't update the ID
                    setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new starship
            db_starship = Starship(**starship_data)
            self.db.add(db_starship)
            self.db.commit()
            self.db.refresh(db_starship)
            return db_starship
