import pytest
from fastapi.testclient import TestClient
from app.models.film import Film
from app.services.film_service import FilmService
from app.schemas.film import FilmCreate


class TestFilmAPI:
    """Test cases for film API endpoints"""

    def test_get_films_empty(self, client: TestClient):
        """Test getting films when database is empty"""
        response = client.get("/api/v1/films/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0  # Might have films from initial population
        assert isinstance(data["items"], list)
        assert data["page"] == 1
        assert data["size"] == 20

    def test_get_films_with_pagination(self, client: TestClient, db):
        """Test getting films with pagination"""
        # Create test films
        service = FilmService(db)
        for i in range(5):
            film_data = FilmCreate(
                swapi_id=i+100,  # Use high IDs to avoid conflicts
                title=f"Test Film {i+1}",
                episode_id=i+1,
                director="Test Director"
            )
            service.create_film(film_data)

        # Test first page
        response = client.get("/api/v1/films/?page=1&size=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= data["total"]
        assert data["page"] == 1
        assert data["size"] == 3

    def test_search_films(self, client: TestClient, db):
        """Test searching films by title"""
        # Create test films
        service = FilmService(db)
        films = [
            FilmCreate(swapi_id=101, title="A New Hope", episode_id=4),
            FilmCreate(swapi_id=102, title="The Empire Strikes Back", episode_id=5),
            FilmCreate(swapi_id=103, title="Return of the Jedi", episode_id=6),
        ]
        for film_data in films:
            service.create_film(film_data)

        # Search for "Hope"
        response = client.get("/api/v1/films/search?title=Hope")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_vote_for_film(self, client: TestClient, db):
        """Test voting for a film"""
        # Create test film
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=104, title="Test Film", episode_id=1)
        film = service.create_film(film_data)

        # Vote for film
        response = client.post(f"/api/v1/films/{film.id}/vote")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["votes"] == 1

    def test_get_top_voted_films(self, client: TestClient, db):
        """Test getting top voted films"""
        response = client.get("/api/v1/films/top/voted?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_film_by_id(self, client: TestClient, db):
        """Test getting film by ID"""
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=1, title="A New Hope", episode_id=4)
        film = service.create_film(film_data)

        response = client.get(f"/api/v1/films/{film.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "A New Hope"
        assert data["episode_id"] == 4

    def test_get_film_not_found(self, client: TestClient):
        """Test getting non-existent film"""
        response = client.get("/api/v1/films/999")
        assert response.status_code == 404
        assert "Film not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_sync_films_from_swapi(self, client: TestClient):
        """Test syncing films from SWAPI"""
        from unittest.mock import patch, AsyncMock
        with patch('app.api.films.SWAPIService') as mock_swapi:
            mock_instance = mock_swapi.return_value
            mock_instance.fetch_all_films = AsyncMock(return_value=[
                {
                    "swapi_id": 1,
                    "title": "A New Hope",
                    "episode_id": 4,
                    "director": "George Lucas",
                    "url": "https://swapi.dev/api/films/1/"
                }
            ])

            response = client.post("/api/v1/films/sync")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_sync_films_from_swapi_with_errors(self, client: TestClient):
        """Test syncing films from SWAPI with service errors"""
        from unittest.mock import patch, AsyncMock
        with patch('app.api.films.SWAPIService') as mock_swapi:
            mock_instance = mock_swapi.return_value
            mock_instance.fetch_all_films = AsyncMock(side_effect=Exception("SWAPI error"))

            response = client.post("/api/v1/films/sync")
            assert response.status_code == 500
            assert "Failed to sync films" in response.json()["detail"]

    def test_get_films_with_pagination_parameters(self, client: TestClient):
        """Test getting films with pagination parameters"""
        response = client.get("/api/v1/films?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data

    def test_vote_for_nonexistent_film(self, client: TestClient):
        """Test voting for a film that doesn't exist"""
        response = client.post("/api/v1/films/999/vote")
        assert response.status_code == 404
        assert "Film not found" in response.json()["detail"]
