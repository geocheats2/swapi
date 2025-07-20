import pytest
from app.models.film import Film
from app.services.film_service import FilmService
from app.schemas.film import FilmCreate, FilmUpdate


class TestFilmService:
    """Test cases for film service"""

    def test_create_film(self, db):
        """Test creating a film"""
        service = FilmService(db)
        film_data = FilmCreate(
            swapi_id=1,
            title="A New Hope",
            episode_id=4,
            opening_crawl="It is a period of civil war...",
            director="George Lucas",
            producer="Gary Kurtz",
            release_date="1977-05-25"
        )
        
        film = service.create_film(film_data)
        
        assert film.id is not None
        assert film.title == "A New Hope"
        assert film.swapi_id == 1
        assert film.episode_id == 4
        assert film.votes == 0

    def test_get_film_by_id(self, db):
        """Test getting film by ID"""
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=1, title="A New Hope", episode_id=4)
        created_film = service.create_film(film_data)
        
        retrieved_film = service.get_film(created_film.id)
        
        assert retrieved_film is not None
        assert retrieved_film.id == created_film.id
        assert retrieved_film.title == "A New Hope"

    def test_get_film_by_swapi_id(self, db):
        """Test getting film by SWAPI ID"""
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=42, title="Test Film", episode_id=7)
        service.create_film(film_data)
        
        film = service.get_film_by_swapi_id(42)
        
        assert film is not None
        assert film.swapi_id == 42
        assert film.title == "Test Film"

    def test_get_films_with_pagination(self, db):
        """Test getting films with pagination"""
        service = FilmService(db)
        
        # Create multiple films
        for i in range(8):
            film_data = FilmCreate(swapi_id=i+1, title=f"Film {i+1}", episode_id=i+1)
            service.create_film(film_data)
        
        # Test pagination
        films, total = service.get_films(skip=0, limit=5)
        assert len(films) == 5
        assert total == 8
        
        films, total = service.get_films(skip=5, limit=5)
        assert len(films) == 3
        assert total == 8

    def test_search_films(self, db):
        """Test searching films by title"""
        service = FilmService(db)
        
        # Create test films
        films = [
            FilmCreate(swapi_id=1, title="A New Hope", episode_id=4),
            FilmCreate(swapi_id=2, title="The Empire Strikes Back", episode_id=5),
            FilmCreate(swapi_id=3, title="Return of the Jedi", episode_id=6),
            FilmCreate(swapi_id=4, title="The Phantom Menace", episode_id=1),
        ]
        
        for film_data in films:
            service.create_film(film_data)
        
        # Search for "hope"
        films, total = service.search_films("Hope")
        assert total == 1
        assert films[0].title == "A New Hope"
        
        # Search for "the"
        films, total = service.search_films("The")
        assert total == 3
        
        # Search for non-existent
        films, total = service.search_films("nonexistent")
        assert total == 0

    def test_update_film(self, db):
        """Test updating a film"""
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=1, title="A New Hope", director="George Lucas")
        film = service.create_film(film_data)
        
        # Update film
        update_data = FilmUpdate(director="George Lucas Jr.", producer="New Producer")
        updated_film = service.update_film(film.id, update_data)
        
        assert updated_film is not None
        assert updated_film.director == "George Lucas Jr."
        assert updated_film.producer == "New Producer"
        assert updated_film.title == "A New Hope"  # Unchanged

    def test_delete_film(self, db):
        """Test deleting a film"""
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=1, title="A New Hope")
        film = service.create_film(film_data)
        
        # Delete film
        result = service.delete_film(film.id)
        assert result is True
        
        # Verify deletion
        deleted_film = service.get_film(film.id)
        assert deleted_film is None
        
        # Try to delete non-existent film
        result = service.delete_film(999)
        assert result is False

    def test_vote_for_film(self, db):
        """Test voting for a film"""
        service = FilmService(db)
        film_data = FilmCreate(swapi_id=1, title="A New Hope")
        film = service.create_film(film_data)
        
        # Initial votes should be 0
        assert film.votes == 0
        
        # Vote for film
        voted_film = service.vote_for_film(film.id)
        assert voted_film is not None
        assert voted_film.votes == 1
        
        # Vote again
        voted_film = service.vote_for_film(film.id)
        assert voted_film.votes == 2
        
        # Try to vote for non-existent film
        result = service.vote_for_film(999)
        assert result is None

    def test_get_top_films(self, db):
        """Test getting top voted films"""
        service = FilmService(db)
        
        # Create films
        films = [
            FilmCreate(swapi_id=1, title="A New Hope"),
            FilmCreate(swapi_id=2, title="Empire Strikes Back"),
            FilmCreate(swapi_id=3, title="Return of the Jedi"),
        ]
        
        created_films = []
        for film_data in films:
            created_films.append(service.create_film(film_data))
        
        # Vote for films (different amounts)
        for _ in range(5):
            service.vote_for_film(created_films[0].id)  # New Hope: 5 votes
        for _ in range(3):
            service.vote_for_film(created_films[1].id)  # Empire: 3 votes
        service.vote_for_film(created_films[2].id)     # Jedi: 1 vote
        
        # Get top films
        top_films = service.get_top_films(limit=2)
        assert len(top_films) == 2
        assert top_films[0].title == "A New Hope"
        assert top_films[0].votes == 5
        assert top_films[1].title == "Empire Strikes Back"
        assert top_films[1].votes == 3

    def test_create_or_update_from_swapi(self, db):
        """Test creating or updating film from SWAPI data"""
        service = FilmService(db)
        
        # Test creating new film
        swapi_data = {
            "swapi_id": 1,
            "title": "A New Hope",
            "episode_id": 4,
            "opening_crawl": "It is a period of civil war...",
            "director": "George Lucas",
            "producer": "Gary Kurtz",
            "release_date": "1977-05-25",
            "url": "https://swapi.dev/api/films/1/"
        }
        
        film = service.create_or_update_from_swapi(swapi_data)
        assert film.title == "A New Hope"
        assert film.swapi_id == 1
        
        # Test updating existing film
        updated_swapi_data = {
            "swapi_id": 1,
            "title": "A New Hope",
            "episode_id": 4,
            "opening_crawl": "Updated opening crawl...",  # Changed
            "director": "George Lucas",
            "producer": "Updated Producer",  # Changed
            "release_date": "1977-05-25",
            "url": "https://swapi.dev/api/films/1/"
        }
        
        updated_film = service.create_or_update_from_swapi(updated_swapi_data)
        assert updated_film.id == film.id  # Same film
        assert updated_film.opening_crawl == "Updated opening crawl..."  # Updated
        assert updated_film.producer == "Updated Producer"  # Updated

    def test_create_or_update_from_swapi_missing_id(self, db):
        """Test error handling when SWAPI ID is missing"""
        service = FilmService(db)
        
        swapi_data = {
            "title": "A New Hope",
            "episode_id": 4
            # Missing swapi_id
        }
        
        with pytest.raises(ValueError, match="SWAPI ID is required"):
            service.create_or_update_from_swapi(swapi_data)
