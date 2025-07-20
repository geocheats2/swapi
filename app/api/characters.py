from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.character_service import CharacterService
from app.services.swapi_service import SWAPIService
from app.schemas.character import Character, CharacterResponse, CharacterCreate, CharacterUpdate
from app.schemas.common import PaginatedResponse, VoteResponse
import math

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/", response_model=PaginatedResponse[Character])
async def get_characters(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get paginated list of characters"""
    skip = (page - 1) * size
    service = CharacterService(db)
    characters, total = service.get_characters(skip=skip, limit=size)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return PaginatedResponse(
        items=characters,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/search", response_model=PaginatedResponse[Character])
async def search_characters(
    name: str = Query(..., description="Character name to search for"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Search characters by name"""
    skip = (page - 1) * size
    service = CharacterService(db)
    characters, total = service.search_characters(name=name, skip=skip, limit=size)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return PaginatedResponse(
        items=characters,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get character by ID"""
    service = CharacterService(db)
    character = service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/{character_id}/vote", response_model=VoteResponse)
async def vote_for_character(character_id: int, db: Session = Depends(get_db)):
    """Vote for a character"""
    service = CharacterService(db)
    character = service.vote_for_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return VoteResponse(
        success=True,
        message=f"Successfully voted for {character.name}",
        votes=character.votes
    )


@router.post("/sync", response_model=dict)
async def sync_characters_from_swapi(db: Session = Depends(get_db)):
    """Sync characters from SWAPI"""
    try:
        swapi_service = SWAPIService()
        character_service = CharacterService(db)
        
        # Fetch all characters from SWAPI
        swapi_characters = await swapi_service.fetch_all_characters()
        
        created_count = 0
        updated_count = 0
        
        for char_data in swapi_characters:
            try:
                existing = character_service.get_character_by_swapi_id(char_data["swapi_id"])
                if existing:
                    character_service.create_or_update_from_swapi(char_data)
                    updated_count += 1
                else:
                    character_service.create_or_update_from_swapi(char_data)
                    created_count += 1
            except Exception as e:
                print(f"Error processing character {char_data.get('name', 'Unknown')}: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Synced characters from SWAPI",
            "created": created_count,
            "updated": updated_count,
            "total": len(swapi_characters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync characters: {str(e)}")


@router.get("/top/voted", response_model=List[Character])
async def get_top_voted_characters(
    limit: int = Query(10, ge=1, le=50, description="Number of top characters to return"),
    db: Session = Depends(get_db)
):
    """Get top voted characters"""
    service = CharacterService(db)
    return service.get_top_characters(limit=limit)
