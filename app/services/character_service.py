from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, func
from app.models.character import Character
from app.models.film import Film
from app.schemas.character import CharacterCreate, CharacterUpdate
import logging

logger = logging.getLogger(__name__)


class CharacterService:
    """Service for character operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_character(self, character_id: int) -> Optional[Character]:
        """Get character by ID"""
        return self.db.query(Character).options(
            selectinload(Character.films)
        ).filter(Character.id == character_id).first()
    
    def get_character_by_swapi_id(self, swapi_id: int) -> Optional[Character]:
        """Get character by SWAPI ID"""
        return self.db.query(Character).filter(Character.swapi_id == swapi_id).first()
    
    def get_characters(self, skip: int = 0, limit: int = 20) -> tuple[List[Character], int]:
        """Get paginated list of characters"""
        query = self.db.query(Character).options(selectinload(Character.films))
        total = query.count()
        characters = query.order_by(Character.votes.desc(), Character.name).offset(skip).limit(limit).all()
        return characters, total
    
    def search_characters(self, name: str, skip: int = 0, limit: int = 20) -> tuple[List[Character], int]:
        """Search characters by name"""
        query = self.db.query(Character).options(selectinload(Character.films)).filter(
            Character.name.ilike(f"%{name}%")
        )
        total = query.count()
        characters = query.order_by(Character.votes.desc(), Character.name).offset(skip).limit(limit).all()
        return characters, total
    
    def create_character(self, character_data: CharacterCreate) -> Character:
        """Create a new character"""
        db_character = Character(**character_data.model_dump())
        self.db.add(db_character)
        self.db.commit()
        self.db.refresh(db_character)
        logger.info(f"Created character: {db_character.name}")
        return db_character
    
    def update_character(self, character_id: int, character_data: CharacterUpdate) -> Optional[Character]:
        """Update an existing character"""
        db_character = self.get_character(character_id)
        if not db_character:
            return None
        
        update_data = character_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_character, field, value)
        
        self.db.commit()
        self.db.refresh(db_character)
        logger.info(f"Updated character: {db_character.name}")
        return db_character
    
    def delete_character(self, character_id: int) -> bool:
        """Delete a character"""
        db_character = self.get_character(character_id)
        if not db_character:
            return False
        
        self.db.delete(db_character)
        self.db.commit()
        logger.info(f"Deleted character: {db_character.name}")
        return True
    
    def vote_for_character(self, character_id: int) -> Optional[Character]:
        """Vote for a character (increment vote count)"""
        db_character = self.get_character(character_id)
        if not db_character:
            return None
        
        # Use SQL update to increment votes
        self.db.query(Character).filter(Character.id == character_id).update(
            {Character.votes: Character.votes + 1}
        )
        self.db.commit()
        
        # Get fresh object with updated votes
        updated_character = self.get_character(character_id)
        if updated_character:
            logger.info(f"Voted for character: {updated_character.name} (votes: {updated_character.votes})")
        return updated_character
    
    def get_top_characters(self, limit: int = 10) -> List[Character]:
        """Get top voted characters"""
        return self.db.query(Character).order_by(
            Character.votes.desc()
        ).limit(limit).all()
    
    def create_or_update_from_swapi(self, swapi_data: dict) -> Character:
        """Create or update character from SWAPI data"""
        swapi_id = swapi_data.get("swapi_id")
        if swapi_id is None:
            raise ValueError("SWAPI ID is required")
            
        existing = self.get_character_by_swapi_id(swapi_id)
        
        character_data = {
            "swapi_id": swapi_id,
            "name": swapi_data.get("name", ""),
            "height": swapi_data.get("height"),
            "mass": swapi_data.get("mass"),
            "hair_color": swapi_data.get("hair_color"),
            "skin_color": swapi_data.get("skin_color"),
            "eye_color": swapi_data.get("eye_color"),
            "birth_year": swapi_data.get("birth_year"),
            "gender": swapi_data.get("gender"),
            "homeworld": swapi_data.get("homeworld"),
            "url": swapi_data.get("url")
        }
        
        if existing:
            # Update existing character
            for field, value in character_data.items():
                if field != "swapi_id":  # Don't update the ID
                    setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new character
            db_character = Character(**character_data)
            self.db.add(db_character)
            self.db.commit()
            self.db.refresh(db_character)
            return db_character
