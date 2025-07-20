from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.film_service import FilmService
from app.services.swapi_service import SWAPIService
from app.schemas.film import Film, FilmResponse, FilmCreate, FilmUpdate
from app.schemas.common import PaginatedResponse, VoteResponse
import math

router = APIRouter(prefix="/films", tags=["films"])


@router.get("/", response_model=PaginatedResponse[Film])
async def get_films(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get paginated list of films"""
    skip = (page - 1) * size
    service = FilmService(db)
    films, total = service.get_films(skip=skip, limit=size)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return PaginatedResponse(
        items=films,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/search", response_model=PaginatedResponse[Film])
async def search_films(
    title: str = Query(..., description="Film title to search for"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Search films by title"""
    skip = (page - 1) * size
    service = FilmService(db)
    films, total = service.search_films(title=title, skip=skip, limit=size)
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return PaginatedResponse(
        items=films,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{film_id}", response_model=FilmResponse)
async def get_film(film_id: int, db: Session = Depends(get_db)):
    """Get film by ID"""
    service = FilmService(db)
    film = service.get_film(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film


@router.post("/{film_id}/vote", response_model=VoteResponse)
async def vote_for_film(film_id: int, db: Session = Depends(get_db)):
    """Vote for a film"""
    service = FilmService(db)
    film = service.vote_for_film(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    
    return VoteResponse(
        success=True,
        message=f"Successfully voted for {film.title}",
        votes=film.votes
    )


@router.post("/sync", response_model=dict)
async def sync_films_from_swapi(db: Session = Depends(get_db)):
    """Sync films from SWAPI"""
    try:
        swapi_service = SWAPIService()
        film_service = FilmService(db)
        
        # Fetch all films from SWAPI
        swapi_films = await swapi_service.fetch_all_films()
        
        created_count = 0
        updated_count = 0
        
        for film_data in swapi_films:
            try:
                existing = film_service.get_film_by_swapi_id(film_data["swapi_id"])
                if existing:
                    film_service.create_or_update_from_swapi(film_data)
                    updated_count += 1
                else:
                    film_service.create_or_update_from_swapi(film_data)
                    created_count += 1
            except Exception as e:
                print(f"Error processing film {film_data.get('title', 'Unknown')}: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Synced films from SWAPI",
            "created": created_count,
            "updated": updated_count,
            "total": len(swapi_films)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync films: {str(e)}")


@router.get("/top/voted", response_model=List[Film])
async def get_top_voted_films(
    limit: int = Query(10, ge=1, le=50, description="Number of top films to return"),
    db: Session = Depends(get_db)
):
    """Get top voted films"""
    service = FilmService(db)
    return service.get_top_films(limit=limit)
