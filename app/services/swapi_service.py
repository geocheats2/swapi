import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
import logging
import ssl

logger = logging.getLogger(__name__)


class SWAPIService:
    """Service for interacting with the Star Wars API"""
    
    def __init__(self):
        self.base_url = settings.SWAPI_BASE_URL
        self.timeout = 30.0
        # Create SSL context that doesn't verify certificates (for development)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def fetch_all_characters(self) -> List[Dict[str, Any]]:
        """Fetch all characters from SWAPI"""
        return await self._fetch_all_pages("people")
    
    async def fetch_all_films(self) -> List[Dict[str, Any]]:
        """Fetch all films from SWAPI"""
        return await self._fetch_all_pages("films")
    
    async def fetch_all_starships(self) -> List[Dict[str, Any]]:
        """Fetch all starships from SWAPI"""
        return await self._fetch_all_pages("starships")
    
    async def _fetch_all_pages(self, endpoint: str) -> List[Dict[str, Any]]:
        """Fetch all pages for a given endpoint"""
        all_items = []
        url = f"{self.base_url}/{endpoint}/"
        
        async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
            while url:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Add items with SWAPI ID extracted from URL
                    for item in data.get("results", []):
                        # Extract ID from URL (e.g., "https://swapi.dev/api/people/1/" -> 1)
                        swapi_id = self._extract_id_from_url(item.get("url", ""))
                        if swapi_id:
                            item["swapi_id"] = swapi_id
                            all_items.append(item)
                    
                    url = data.get("next")  # Get next page URL
                    
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error fetching {endpoint}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error fetching {endpoint}: {e}")
                    break
        
        logger.info(f"Fetched {len(all_items)} {endpoint} from SWAPI")
        return all_items
    
    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """Extract ID from SWAPI URL"""
        try:
            # URL format: "https://swapi.dev/api/people/1/"
            parts = url.rstrip("/").split("/")
            return int(parts[-1])
        except (ValueError, IndexError):
            return None
    
    async def fetch_character_by_id(self, swapi_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific character by SWAPI ID"""
        return await self._fetch_by_id("people", swapi_id)
    
    async def fetch_film_by_id(self, swapi_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific film by SWAPI ID"""
        return await self._fetch_by_id("films", swapi_id)
    
    async def fetch_starship_by_id(self, swapi_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific starship by SWAPI ID"""
        return await self._fetch_by_id("starships", swapi_id)
    
    async def _fetch_by_id(self, endpoint: str, swapi_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific item by ID"""
        url = f"{self.base_url}/{endpoint}/{swapi_id}/"
        
        async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                data = response.json()
                data["swapi_id"] = swapi_id
                return data
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching {endpoint}/{swapi_id}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error fetching {endpoint}/{swapi_id}: {e}")
                return None
