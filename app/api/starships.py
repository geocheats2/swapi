from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.starship_service import StarshipService
from app.services.swapi_service import SWAPIService
from app.schemas.starship import Starship, StarshipResponse, StarshipCreate, StarshipUpdate
from app.schemas.common import PaginatedResponse, VoteResponse
import math

router = APIRouter(prefix="/starships", tags=["starships"])


@router.get("/", response_model=PaginatedResponse[Starship])
async def get_starships(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get paginated list of starships"""
    skip = (page - 1) * size
    service = StarshipService(db)
    starships, total = service.get_starships(skip=skip, limit=size)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return PaginatedResponse(
        items=starships,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/search", response_model=PaginatedResponse[Starship])
async def search_starships(
    name: str = Query(..., description="Starship name to search for"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Search starships by name"""
    skip = (page - 1) * size
    service = StarshipService(db)
    starships, total = service.search_starships(name=name, skip=skip, limit=size)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return PaginatedResponse(
        items=starships,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{starship_id}", response_model=StarshipResponse)
async def get_starship(starship_id: int, db: Session = Depends(get_db)):
    """Get starship by ID"""
    service = StarshipService(db)
    starship = service.get_starship(starship_id)
    if not starship:
        raise HTTPException(status_code=404, detail="Starship not found")
    return starship


@router.post("/{starship_id}/vote", response_model=VoteResponse)
async def vote_for_starship(starship_id: int, db: Session = Depends(get_db)):
    """Vote for a starship"""
    service = StarshipService(db)
    starship = service.vote_for_starship(starship_id)
    if not starship:
        raise HTTPException(status_code=404, detail="Starship not found")
    
    return VoteResponse(
        success=True,
        message=f"Successfully voted for {starship.name}",
        votes=starship.votes
    )


@router.post("/sync", response_model=dict)
async def sync_starships_from_swapi(db: Session = Depends(get_db)):
    """Sync starships from SWAPI"""
    try:
        swapi_service = SWAPIService()
        starship_service = StarshipService(db)
        
        # Fetch all starships from SWAPI
        swapi_starships = await swapi_service.fetch_all_starships()
        
        created_count = 0
        updated_count = 0
        
        for starship_data in swapi_starships:
            try:
                existing = starship_service.get_starship_by_swapi_id(starship_data["swapi_id"])
                if existing:
                    starship_service.create_or_update_from_swapi(starship_data)
                    updated_count += 1
                else:
                    starship_service.create_or_update_from_swapi(starship_data)
                    created_count += 1
            except Exception as e:
                print(f"Error processing starship {starship_data.get('name', 'Unknown')}: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Synced starships from SWAPI",
            "created": created_count,
            "updated": updated_count,
            "total": len(swapi_starships)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync starships: {str(e)}")


@router.get("/top/voted", response_model=List[Starship])
async def get_top_voted_starships(
    limit: int = Query(10, ge=1, le=50, description="Number of top starships to return"),
    db: Session = Depends(get_db)
):
    """Get top voted starships"""
    service = StarshipService(db)
    return service.get_top_starships(limit=limit)
