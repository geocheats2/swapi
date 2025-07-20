import pytest
from app.models.character import Character
from app.services.character_service import CharacterService
from app.schemas.character import CharacterCreate, CharacterUpdate
from app.models.film import Film


class TestCharacterService:
    """Test cases for character service"""

    def test_create_character(self, db):
        """Test creating a character"""
        service = CharacterService(db)
        char_data = CharacterCreate(
            swapi_id=1,
            name="Luke Skywalker",
            height="172",
            mass="77",
            hair_color="blond",
            skin_color="fair",
            eye_color="blue",
            birth_year="19BBY",
            gender="male",
            homeworld="Tatooine"
        )
        
        character = service.create_character(char_data)
        
        assert character.id is not None
        assert character.name == "Luke Skywalker"
        assert character.swapi_id == 1
        assert character.height == "172"
        assert character.votes == 0

    def test_get_character_by_id(self, db):
        """Test getting character by ID"""
        service = CharacterService(db)
        char_data = CharacterCreate(swapi_id=1, name="Luke Skywalker")
        created_character = service.create_character(char_data)
        
        retrieved_character = service.get_character(created_character.id)
        
        assert retrieved_character is not None
        assert retrieved_character.id == created_character.id
        assert retrieved_character.name == "Luke Skywalker"

    def test_get_character_by_swapi_id(self, db):
        """Test getting character by SWAPI ID"""
        service = CharacterService(db)
        char_data = CharacterCreate(swapi_id=42, name="Test Character")
        service.create_character(char_data)
        
        character = service.get_character_by_swapi_id(42)
        
        assert character is not None
        assert character.swapi_id == 42
        assert character.name == "Test Character"

    def test_get_characters_with_pagination(self, db):
        """Test getting characters with pagination"""
        service = CharacterService(db)
        
        # Create multiple characters
        for i in range(15):
            char_data = CharacterCreate(swapi_id=i+1, name=f"Character {i+1}")
            service.create_character(char_data)
        
        # Test pagination
        characters, total = service.get_characters(skip=0, limit=10)
        assert len(characters) == 10
        assert total == 15
        
        characters, total = service.get_characters(skip=10, limit=10)
        assert len(characters) == 5
        assert total == 15

    def test_search_characters(self, db):
        """Test searching characters by name"""
        service = CharacterService(db)
        
        # Create test characters
        chars = [
            CharacterCreate(swapi_id=1, name="Luke Skywalker"),
            CharacterCreate(swapi_id=2, name="Darth Vader"),
            CharacterCreate(swapi_id=3, name="Princess Leia"),
            CharacterCreate(swapi_id=4, name="Han Solo"),
        ]
        
        for char_data in chars:
            service.create_character(char_data)
        
        # Search for "luke"
        characters, total = service.search_characters("luke")
        assert total == 1
        assert characters[0].name == "Luke Skywalker"
        
        # Search for "a" (should match all since all names contain 'a': Vader, Leia, Han, Skywalker)
        characters, total = service.search_characters("a")
        assert total == 4
        
        # Search for non-existent
        characters, total = service.search_characters("nonexistent")
        assert total == 0

    def test_update_character(self, db):
        """Test updating a character"""
        service = CharacterService(db)
        char_data = CharacterCreate(swapi_id=1, name="Luke Skywalker", height="172")
        character = service.create_character(char_data)
        
        # Update character
        update_data = CharacterUpdate(height="175", mass="80")
        updated_character = service.update_character(character.id, update_data)
        
        assert updated_character is not None
        assert updated_character.height == "175"
        assert updated_character.mass == "80"
        assert updated_character.name == "Luke Skywalker"  # Unchanged

    def test_delete_character(self, db):
        """Test deleting a character"""
        service = CharacterService(db)
        char_data = CharacterCreate(swapi_id=1, name="Luke Skywalker")
        character = service.create_character(char_data)
        
        # Delete character
        result = service.delete_character(character.id)
        assert result is True
        
        # Verify deletion
        deleted_character = service.get_character(character.id)
        assert deleted_character is None
        
        # Try to delete non-existent character
        result = service.delete_character(999)
        assert result is False

    def test_vote_for_character(self, db):
        """Test voting for a character"""
        service = CharacterService(db)
        char_data = CharacterCreate(swapi_id=1, name="Luke Skywalker")
        character = service.create_character(char_data)
        
        # Initial votes should be 0
        assert character.votes == 0
        
        # Vote for character
        voted_character = service.vote_for_character(character.id)
        assert voted_character is not None
        assert voted_character.votes == 1
        
        # Vote again
        voted_character = service.vote_for_character(character.id)
        assert voted_character.votes == 2
        
        # Try to vote for non-existent character
        result = service.vote_for_character(999)
        assert result is None

    def test_get_top_characters(self, db):
        """Test getting top voted characters"""
        service = CharacterService(db)
        
        # Create characters
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
        
        # Get top characters
        top_characters = service.get_top_characters(limit=2)
        assert len(top_characters) == 2
        assert top_characters[0].name == "Luke Skywalker"
        assert top_characters[0].votes == 5
        assert top_characters[1].name == "Darth Vader"
        assert top_characters[1].votes == 3

    def test_create_or_update_from_swapi(self, db):
        """Test creating or updating character from SWAPI data"""
        service = CharacterService(db)
        
        # Test creating new character
        swapi_data = {
            "swapi_id": 1,
            "name": "Luke Skywalker",
            "height": "172",
            "mass": "77",
            "hair_color": "blond",
            "url": "https://swapi.dev/api/people/1/"
        }
        
        character = service.create_or_update_from_swapi(swapi_data)
        assert character.name == "Luke Skywalker"
        assert character.swapi_id == 1
        
        # Test updating existing character
        updated_swapi_data = {
            "swapi_id": 1,
            "name": "Luke Skywalker",
            "height": "175",  # Changed
            "mass": "80",     # Changed
            "hair_color": "blond",
            "url": "https://swapi.dev/api/people/1/"
        }
        
        updated_character = service.create_or_update_from_swapi(updated_swapi_data)
        assert updated_character.id == character.id  # Same character
        assert updated_character.height == "175"     # Updated
        assert updated_character.mass == "80"        # Updated

    def test_search_characters_case_insensitive(self, db):
        """Test case insensitive character search"""
        service = CharacterService(db)
        
        # Create test character
        char_data = CharacterCreate(
            swapi_id=4,
            name="Darth Vader",
            height="202",
            mass="136"
        )
        character = service.create_character(char_data)
        
        # Search with different cases
        result, total = service.search_characters("darth")
        assert len(result) == 1
        assert total == 1
        
        result, total = service.search_characters("VADER")
        assert len(result) == 1
        assert total == 1

    def test_get_character_by_swapi_id_not_found(self, db):
        """Test getting character by SWAPI ID when not found"""
        service = CharacterService(db)
        character = service.get_character_by_swapi_id(999)
        assert character is None
