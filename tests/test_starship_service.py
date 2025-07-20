import pytest
from app.models.starship import Starship
from app.services.starship_service import StarshipService
from app.schemas.starship import StarshipCreate, StarshipUpdate


class TestStarshipService:
    """Test cases for starship service"""

    def test_create_starship(self, db):
        """Test creating a starship"""
        service = StarshipService(db)
        starship_data = StarshipCreate(
            swapi_id=1,
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            manufacturer="Corellian Engineering Corporation",
            cost_in_credits="100000",
            length="34.37",
            crew="4",
            passengers="6",
            starship_class="Light freighter"
        )
        
        starship = service.create_starship(starship_data)
        
        assert starship.id is not None
        assert starship.name == "Millennium Falcon"
        assert starship.swapi_id == 1
        assert starship.model == "YT-1300 light freighter"
        assert starship.votes == 0

    def test_get_starship_by_id(self, db):
        """Test getting starship by ID"""
        service = StarshipService(db)
        starship_data = StarshipCreate(swapi_id=1, name="Millennium Falcon")
        created_starship = service.create_starship(starship_data)
        
        retrieved_starship = service.get_starship(created_starship.id)
        
        assert retrieved_starship is not None
        assert retrieved_starship.id == created_starship.id
        assert retrieved_starship.name == "Millennium Falcon"

    def test_get_starship_by_swapi_id(self, db):
        """Test getting starship by SWAPI ID"""
        service = StarshipService(db)
        starship_data = StarshipCreate(swapi_id=42, name="Test Starship")
        service.create_starship(starship_data)
        
        starship = service.get_starship_by_swapi_id(42)
        
        assert starship is not None
        assert starship.swapi_id == 42
        assert starship.name == "Test Starship"

    def test_get_starships_with_pagination(self, db):
        """Test getting starships with pagination"""
        service = StarshipService(db)
        
        # Create multiple starships
        for i in range(12):
            starship_data = StarshipCreate(swapi_id=i+1, name=f"Starship {i+1}")
            service.create_starship(starship_data)
        
        # Test pagination
        starships, total = service.get_starships(skip=0, limit=5)
        assert len(starships) == 5
        assert total == 12
        
        starships, total = service.get_starships(skip=5, limit=10)
        assert len(starships) == 7
        assert total == 12

    def test_search_starships(self, db):
        """Test searching starships by name"""
        service = StarshipService(db)
        
        # Create test starships
        starships = [
            StarshipCreate(swapi_id=1, name="Millennium Falcon"),
            StarshipCreate(swapi_id=2, name="X-wing"),
            StarshipCreate(swapi_id=3, name="TIE Fighter"),
            StarshipCreate(swapi_id=4, name="Star Destroyer"),
        ]
        
        for starship_data in starships:
            service.create_starship(starship_data)
        
        # Search for "falcon"
        starships, total = service.search_starships("Falcon")
        assert total == 1
        assert starships[0].name == "Millennium Falcon"
        
        # Search for "star" (should match Star Destroyer)
        starships, total = service.search_starships("Star")
        assert total == 1
        assert starships[0].name == "Star Destroyer"
        
        # Search for non-existent
        starships, total = service.search_starships("nonexistent")
        assert total == 0

    def test_update_starship(self, db):
        """Test updating a starship"""
        service = StarshipService(db)
        starship_data = StarshipCreate(swapi_id=1, name="Millennium Falcon", crew="4")
        starship = service.create_starship(starship_data)
        
        # Update starship
        update_data = StarshipUpdate(crew="6", passengers="8")
        updated_starship = service.update_starship(starship.id, update_data)
        
        assert updated_starship is not None
        assert updated_starship.crew == "6"
        assert updated_starship.passengers == "8"
        assert updated_starship.name == "Millennium Falcon"  # Unchanged

    def test_delete_starship(self, db):
        """Test deleting a starship"""
        service = StarshipService(db)
        starship_data = StarshipCreate(swapi_id=1, name="Millennium Falcon")
        starship = service.create_starship(starship_data)
        
        # Delete starship
        result = service.delete_starship(starship.id)
        assert result is True
        
        # Verify deletion
        deleted_starship = service.get_starship(starship.id)
        assert deleted_starship is None
        
        # Try to delete non-existent starship
        result = service.delete_starship(999)
        assert result is False

    def test_vote_for_starship(self, db):
        """Test voting for a starship"""
        service = StarshipService(db)
        starship_data = StarshipCreate(swapi_id=1, name="Millennium Falcon")
        starship = service.create_starship(starship_data)
        
        # Initial votes should be 0
        assert starship.votes == 0
        
        # Vote for starship
        voted_starship = service.vote_for_starship(starship.id)
        assert voted_starship is not None
        assert voted_starship.votes == 1
        
        # Vote again
        voted_starship = service.vote_for_starship(starship.id)
        assert voted_starship.votes == 2
        
        # Try to vote for non-existent starship
        result = service.vote_for_starship(999)
        assert result is None

    def test_get_top_starships(self, db):
        """Test getting top voted starships"""
        service = StarshipService(db)
        
        # Create starships
        starships = [
            StarshipCreate(swapi_id=1, name="Millennium Falcon"),
            StarshipCreate(swapi_id=2, name="X-wing"),
            StarshipCreate(swapi_id=3, name="TIE Fighter"),
        ]
        
        created_starships = []
        for starship_data in starships:
            created_starships.append(service.create_starship(starship_data))
        
        # Vote for starships (different amounts)
        for _ in range(7):
            service.vote_for_starship(created_starships[0].id)  # Falcon: 7 votes
        for _ in range(4):
            service.vote_for_starship(created_starships[1].id)  # X-wing: 4 votes
        service.vote_for_starship(created_starships[2].id)     # TIE: 1 vote
        
        # Get top starships
        top_starships = service.get_top_starships(limit=2)
        assert len(top_starships) == 2
        assert top_starships[0].name == "Millennium Falcon"
        assert top_starships[0].votes == 7
        assert top_starships[1].name == "X-wing"
        assert top_starships[1].votes == 4

    def test_create_or_update_from_swapi(self, db):
        """Test creating or updating starship from SWAPI data"""
        service = StarshipService(db)
        
        # Test creating new starship
        swapi_data = {
            "swapi_id": 1,
            "name": "Millennium Falcon",
            "model": "YT-1300 light freighter",
            "manufacturer": "Corellian Engineering Corporation",
            "cost_in_credits": "100000",
            "length": "34.37",
            "crew": "4",
            "passengers": "6",
            "cargo_capacity": "100000",
            "consumables": "2 months",
            "hyperdrive_rating": "0.5",
            "MGLT": "75",
            "starship_class": "Light freighter",
            "url": "https://swapi.dev/api/starships/10/"
        }
        
        starship = service.create_or_update_from_swapi(swapi_data)
        assert starship.name == "Millennium Falcon"
        assert starship.swapi_id == 1
        
        # Test updating existing starship
        updated_swapi_data = {
            "swapi_id": 1,
            "name": "Millennium Falcon",
            "model": "YT-1300 light freighter",
            "manufacturer": "Corellian Engineering Corporation",
            "cost_in_credits": "150000",  # Changed
            "length": "34.37",
            "crew": "6",  # Changed
            "passengers": "6",
            "cargo_capacity": "100000",
            "consumables": "2 months",
            "hyperdrive_rating": "0.5",
            "MGLT": "75",
            "starship_class": "Light freighter",
            "url": "https://swapi.dev/api/starships/10/"
        }
        
        updated_starship = service.create_or_update_from_swapi(updated_swapi_data)
        assert updated_starship.id == starship.id  # Same starship
        assert updated_starship.cost_in_credits == "150000"  # Updated
        assert updated_starship.crew == "6"  # Updated

    def test_create_or_update_from_swapi_missing_id(self, db):
        """Test error handling when SWAPI ID is missing"""
        service = StarshipService(db)
        
        swapi_data = {
            "name": "Millennium Falcon",
            "model": "YT-1300 light freighter"
            # Missing swapi_id
        }
        
        with pytest.raises(ValueError, match="SWAPI ID is required"):
            service.create_or_update_from_swapi(swapi_data)
