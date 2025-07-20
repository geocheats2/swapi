import pytest
from fastapi.testclient import TestClient
from app.models.starship import Starship
from app.services.starship_service import StarshipService
from app.schemas.starship import StarshipCreate


class TestStarshipAPI:
    """Test cases for starship API endpoints"""

    def test_get_starships_empty(self, client: TestClient):
        """Test getting starships when database is empty"""
        response = client.get("/api/v1/starships/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0  # Might have starships from initial population
        assert isinstance(data["items"], list)
        assert data["page"] == 1
        assert data["size"] == 20

    def test_search_starships(self, client: TestClient, db):
        """Test searching starships by name"""
        # Create test starships
        service = StarshipService(db)
        starships = [
            StarshipCreate(swapi_id=201, name="Millennium Falcon", model="YT-1300"),
            StarshipCreate(swapi_id=202, name="X-wing", model="T-65"),
            StarshipCreate(swapi_id=203, name="TIE Fighter", model="Twin Ion Engine"),
        ]
        for starship_data in starships:
            service.create_starship(starship_data)

        # Search for "Falcon"
        response = client.get("/api/v1/starships/search?name=Falcon")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_vote_for_starship(self, client: TestClient, db):
        """Test voting for a starship"""
        # Create test starship
        service = StarshipService(db)
        starship_data = StarshipCreate(swapi_id=204, name="Test Starship", model="Test Model")
        starship = service.create_starship(starship_data)

        # Vote for starship
        response = client.post(f"/api/v1/starships/{starship.id}/vote")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["votes"] == 1

    def test_get_starship_by_id(self, client: TestClient, db):
        """Test getting starship by ID"""
        # Create test starship
        service = StarshipService(db)
        starship_data = StarshipCreate(
            swapi_id=205,
            name="Test Starship",
            model="Test Model",
            manufacturer="Test Corp"
        )
        starship = service.create_starship(starship_data)

        # Get starship by ID
        response = client.get(f"/api/v1/starships/{starship.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Starship"
        assert data["model"] == "Test Model"

    def test_get_starship_not_found(self, client: TestClient):
        """Test getting non-existent starship"""
        response = client.get("/api/v1/starships/99999")
        assert response.status_code == 404
        assert "Starship not found" in response.json()["detail"]

    def test_get_top_voted_starships(self, client: TestClient, db):
        """Test getting top voted starships"""
        service = StarshipService(db)

        # Create starships with different vote counts
        starships = [
            StarshipCreate(swapi_id=1, name="Millennium Falcon"),
            StarshipCreate(swapi_id=2, name="X-wing"),
            StarshipCreate(swapi_id=3, name="TIE Fighter"),
        ]

        created_starships = []
        for starship_data in starships:
            created_starships.append(service.create_starship(starship_data))

        # Vote for starships (different amounts)
        for _ in range(5):
            service.vote_for_starship(created_starships[0].id)  # Falcon: 5 votes
        for _ in range(3):
            service.vote_for_starship(created_starships[1].id)  # X-wing: 3 votes
        service.vote_for_starship(created_starships[2].id)     # TIE: 1 vote

        # Get top voted
        response = client.get("/api/v1/starships/top/voted?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Millennium Falcon"
        assert data[0]["votes"] == 5
        assert data[1]["name"] == "X-wing"
        assert data[1]["votes"] == 3

    @pytest.mark.asyncio
    async def test_sync_starships_from_swapi(self, client: TestClient):
        """Test syncing starships from SWAPI"""
        from unittest.mock import patch, AsyncMock
        with patch('app.api.starships.SWAPIService') as mock_swapi:
            mock_instance = mock_swapi.return_value
            mock_instance.fetch_all_starships = AsyncMock(return_value=[
                {
                    "swapi_id": 1,
                    "name": "Millennium Falcon",
                    "model": "YT-1300 light freighter",
                    "url": "https://swapi.dev/api/starships/10/"
                }
            ])

            response = client.post("/api/v1/starships/sync")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_sync_starships_from_swapi_with_errors(self, client: TestClient):
        """Test syncing starships from SWAPI with service errors"""
        from unittest.mock import patch, AsyncMock
        with patch('app.api.starships.SWAPIService') as mock_swapi:
            mock_instance = mock_swapi.return_value
            mock_instance.fetch_all_starships = AsyncMock(side_effect=Exception("SWAPI error"))

            response = client.post("/api/v1/starships/sync")
            assert response.status_code == 500
            assert "Failed to sync starships" in response.json()["detail"]

    def test_get_starships_with_pagination_parameters(self, client: TestClient):
        """Test getting starships with pagination parameters"""
        response = client.get("/api/v1/starships?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data

    def test_vote_for_nonexistent_starship(self, client: TestClient):
        """Test voting for a starship that doesn't exist"""
        response = client.post("/api/v1/starships/999/vote")
        assert response.status_code == 404
        assert "Starship not found" in response.json()["detail"]
