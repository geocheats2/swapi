#!/usr/bin/env python3
"""
Script to populate the database with data from SWAPI
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.swapi_service import SWAPIService
from app.services.character_service import CharacterService
from app.services.film_service import FilmService
from app.services.starship_service import StarshipService


async def populate_characters():
    """Populate characters from SWAPI"""
    print("Fetching characters from SWAPI...")
    swapi_service = SWAPIService()
    
    with SessionLocal() as db:
        character_service = CharacterService(db)
        characters_data = await swapi_service.fetch_all_characters()
        
        print(f"Found {len(characters_data)} characters")
        
        for char_data in characters_data:
            try:
                character = character_service.create_or_update_from_swapi(char_data)
                print(f"✓ {character.name}")
            except Exception as e:
                print(f"✗ Error processing {char_data.get('name', 'Unknown')}: {e}")


async def populate_films():
    """Populate films from SWAPI"""
    print("\nFetching films from SWAPI...")
    swapi_service = SWAPIService()
    
    with SessionLocal() as db:
        film_service = FilmService(db)
        films_data = await swapi_service.fetch_all_films()
        
        print(f"Found {len(films_data)} films")
        
        for film_data in films_data:
            try:
                film = film_service.create_or_update_from_swapi(film_data)
                print(f"✓ {film.title}")
            except Exception as e:
                print(f"✗ Error processing {film_data.get('title', 'Unknown')}: {e}")


async def populate_starships():
    """Populate starships from SWAPI"""
    print("\nFetching starships from SWAPI...")
    swapi_service = SWAPIService()
    
    with SessionLocal() as db:
        starship_service = StarshipService(db)
        starships_data = await swapi_service.fetch_all_starships()
        
        print(f"Found {len(starships_data)} starships")
        
        for starship_data in starships_data:
            try:
                starship = starship_service.create_or_update_from_swapi(starship_data)
                print(f"✓ {starship.name}")
            except Exception as e:
                print(f"✗ Error processing {starship_data.get('name', 'Unknown')}: {e}")


async def main():
    """Main function to populate all data"""
    try:
        print("🌟 Starting Star Wars data population...")
        
        await populate_characters()
        await populate_films()
        await populate_starships()
        
        print("\n🎉 Data population completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during data population: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
