import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.swapi_service import SWAPIService


class TestSWAPIService:
    """Test cases for SWAPI service"""

    @pytest.fixture
    def swapi_service(self):
        return SWAPIService()

    @pytest.mark.asyncio
    async def test_extract_id_from_url(self, swapi_service):
        """Test URL ID extraction"""
        # Test valid URL
        url = "https://swapi.dev/api/people/1/"
        assert swapi_service._extract_id_from_url(url) == 1
        
        # Test URL without trailing slash
        url = "https://swapi.dev/api/people/42"
        assert swapi_service._extract_id_from_url(url) == 42
        
        # Test invalid URL
        url = "invalid-url"
        assert swapi_service._extract_id_from_url(url) is None

    @pytest.mark.asyncio
    async def test_fetch_character_by_id_success(self, swapi_service):
        """Test successful character fetch"""
        # Mock the entire method instead of trying to mock HTTP client
        import unittest.mock
        
        mock_data = {
            "name": "Luke Skywalker",
            "height": "172",
            "url": "https://swapi.dev/api/people/1/",
            "swapi_id": 1
        }
        
        with unittest.mock.patch.object(swapi_service, '_fetch_by_id', return_value=mock_data):
            result = await swapi_service.fetch_character_by_id(1)
            
            assert result is not None
            assert result["name"] == "Luke Skywalker"
            assert result["swapi_id"] == 1

    @pytest.mark.asyncio
    async def test_fetch_character_by_id_not_found(self, swapi_service):
        """Test character not found"""
        import unittest.mock
        
        with unittest.mock.patch.object(swapi_service, '_fetch_by_id', return_value=None):
            result = await swapi_service.fetch_character_by_id(999)
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_all_characters(self, swapi_service):
        """Test fetching all characters with pagination"""
        import unittest.mock
        
        mock_data = [
            {
                "name": "Luke Skywalker",
                "url": "https://swapi.dev/api/people/1/",
                "swapi_id": 1
            },
            {
                "name": "Darth Vader", 
                "url": "https://swapi.dev/api/people/4/",
                "swapi_id": 4
            }
        ]
        
        with unittest.mock.patch.object(swapi_service, '_fetch_all_pages', return_value=mock_data):
            result = await swapi_service.fetch_all_characters()
            
            assert len(result) == 2
            assert result[0]["name"] == "Luke Skywalker"
            assert result[0]["swapi_id"] == 1
            assert result[1]["name"] == "Darth Vader"
            assert result[1]["swapi_id"] == 4

    # Note: Complex async tests for films/starships API calls are tested indirectly 
    # through integration tests in the API test files
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_fetch_with_http_error(self, mock_client, swapi_service):
        """Test handling HTTP errors"""
        from httpx import HTTPError
        
        mock_client.return_value.__aenter__.return_value.get.side_effect = HTTPError("Network error")
        
        result = await swapi_service.fetch_all_characters()
        
        assert result == []

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_fetch_with_unexpected_error(self, mock_client, swapi_service):
        """Test handling unexpected errors"""
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Unexpected error")
        
        result = await swapi_service.fetch_all_characters()
        
        assert result == []

    # Note: Complex async tests for individual fetch methods are tested indirectly 
    # through integration tests
    
    def test_extract_id_edge_cases(self, swapi_service):
        """Test edge cases for URL ID extraction"""
        # Test empty string
        assert swapi_service._extract_id_from_url("") is None
        
        # Test malformed URL
        assert swapi_service._extract_id_from_url("not-a-url") is None
        
        # Test URL with no ID
        assert swapi_service._extract_id_from_url("https://swapi.dev/api/people/") is None
        
        # Test URL with non-numeric ID
        assert swapi_service._extract_id_from_url("https://swapi.dev/api/people/abc/") is None

    def test_extract_id_with_trailing_slash(self, swapi_service):
        """Test extracting ID from URL with trailing slash"""
        url = "https://swapi.dev/api/people/1/"
        result = swapi_service._extract_id_from_url(url)
        assert result == 1

    def test_extract_id_without_trailing_slash(self, swapi_service):
        """Test extracting ID from URL without trailing slash"""
        url = "https://swapi.dev/api/people/1"
        result = swapi_service._extract_id_from_url(url)
        assert result == 1

    @pytest.mark.asyncio
    async def test_fetch_character_by_id_not_found_404(self, swapi_service):
        """Test fetching character by ID when it returns 404"""
        with patch('httpx.AsyncClient') as mock_client:
            import httpx
            
            mock_request = httpx.Request("GET", "https://swapi.dev/api/people/999/")
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not found", request=mock_request, response=mock_response
            )
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await swapi_service.fetch_character_by_id(999)
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_all_characters_simple_mock(self, swapi_service):
        """Test fetching characters with simplified mocking"""
        # This test focuses on the method signature and basic functionality
        # Complex async HTTP mocking is tested through integration tests
        with patch.object(swapi_service, '_fetch_all_pages') as mock_fetch:
            mock_fetch.return_value = []
            
            result = await swapi_service.fetch_all_characters()
            assert result == []
            mock_fetch.assert_called_once_with("people")
