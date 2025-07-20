import pytest
from fastapi.testclient import TestClient
from app.models.character import Character
from app.services.character_service import CharacterService
from app.schemas.character import CharacterCreate


class TestCharacterAPI:
    """Test cases for character API endpoints"""

    def test_get_characters_empty(self, client: TestClient):
        """Test getting characters when database is empty"""
        response = client.get("/api/v1/characters/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["size"] == 20

    def test_get_characters_with_pagination(self, client: TestClient, db):
        """Test getting characters with pagination"""
        # Create test characters
        service = CharacterService(db)
        for i in range(25):
            char_data = CharacterCreate(
                swapi_id=i+1,
                name=f"Character {i+1}",
                height="180",
                mass="80"
            )
            service.create_character(char_data)

        # Test first page
        response = client.get("/api/v1/characters/?page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 3

        # Test second page
        response = client.get("/api/v1/characters/?page=2&size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 2

    def test_search_characters(self, client: TestClient, db):
        """Test searching characters by name"""
        # Create test characters
        service = CharacterService(db)
        chars = [
            CharacterCreate(swapi_id=1, name="Luke Skywalker"),
            CharacterCreate(swapi_id=2, name="Darth Vader"),
            CharacterCreate(swapi_id=3, name="Princess Leia"),
        ]
        for char_data in chars:
            service.create_character(char_data)

        # Search for "Luke"
        response = client.get("/api/v1/characters/search?name=Luke")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Luke Skywalker"

        # Search for "a" (should match all since all names contain 'a': Vader, Leia, Skywalker)
        response = client.get("/api/v1/characters/search?name=a")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_get_character_by_id(self, client: TestClient, db):
        """Test getting character by ID"""
        # Create test character
        service = CharacterService(db)
        char_data = CharacterCreate(
            swapi_id=1,
            name="Luke Skywalker",
            height="172"
        )
        character = service.create_character(char_data)

        # Get character by ID
        response = client.get(f"/api/v1/characters/{character.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Luke Skywalker"
        assert data["height"] == "172"

    def test_get_character_not_found(self, client: TestClient):
        """Test getting non-existent character"""
        response = client.get("/api/v1/characters/999")
        assert response.status_code == 404
        assert "Character not found" in response.json()["detail"]

    def test_vote_for_character(self, client: TestClient, db):
        """Test voting for a character"""
        # Create test character
        service = CharacterService(db)
        char_data = CharacterCreate(swapi_id=1, name="Luke Skywalker")
        character = service.create_character(char_data)

        # Vote for character
        response = client.post(f"/api/v1/characters/{character.id}/vote")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["votes"] == 1
        assert "Luke Skywalker" in data["message"]

        # Vote again
        response = client.post(f"/api/v1/characters/{character.id}/vote")
        assert response.status_code == 200
        data = response.json()
        assert data["votes"] == 2

    def test_vote_for_nonexistent_character(self, client: TestClient):
        """Test voting for non-existent character"""
        response = client.post("/api/v1/characters/999/vote")
        assert response.status_code == 404

    def test_get_top_voted_characters(self, client: TestClient, db):
        """Test getting top voted characters"""
        # Create test characters with different vote counts
        service = CharacterService(db)
        chars = [
            CharacterCreate(swapi_id=1, name="Luke Skywalker"),
            CharacterCreate(swapi_id=2, name="Darth Vader"),
            CharacterCreate(swapi_id=3, name="Princess Leia"),
        ]
        
        characters = []
        for char_data in chars:
            characters.append(service.create_character(char_data))

        # Vote for characters (different amounts)
        for _ in range(5):
            service.vote_for_character(characters[0].id)  # Luke: 5 votes
        for _ in range(3):
            service.vote_for_character(characters[1].id)  # Vader: 3 votes
        service.vote_for_character(characters[2].id)     # Leia: 1 vote

        # Get top voted
        response = client.get("/api/v1/characters/top/voted?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Luke Skywalker"
        assert data[0]["votes"] == 5
        assert data[1]["name"] == "Darth Vader"
        assert data[1]["votes"] == 3

    def test_sync_characters_from_swapi(self, client: TestClient):
        """Test syncing characters from SWAPI"""
        # Mock the SWAPI service
        from unittest.mock import patch, AsyncMock
        with patch('app.api.characters.SWAPIService') as mock_swapi:
            mock_instance = mock_swapi.return_value
            mock_instance.fetch_all_characters = AsyncMock(return_value=[
                {
                    "swapi_id": 1,
                    "name": "Luke Skywalker",
                    "height": "172",
                    "url": "https://swapi.dev/api/people/1/"
                }
            ])

            response = client.post("/api/v1/characters/sync")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_sync_characters_from_swapi_with_errors(self, client: TestClient):
        """Test syncing characters from SWAPI with service errors"""
        from unittest.mock import patch, AsyncMock
        with patch('app.api.characters.SWAPIService') as mock_swapi:
            mock_instance = mock_swapi.return_value
            mock_instance.fetch_all_characters = AsyncMock(side_effect=Exception("SWAPI error"))

            response = client.post("/api/v1/characters/sync")
            assert response.status_code == 500
            assert "Failed to sync characters" in response.json()["detail"]

    def test_get_characters_with_pagination_parameters(self, client: TestClient):
        """Test getting characters with additional pagination parameters"""
        response = client.get("/api/v1/characters?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
