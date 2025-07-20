import pytest
import os
from unittest.mock import patch
from app.config import Settings


class TestConfig:
    """Test cases for configuration"""

    def test_default_settings(self):
        """Test default settings"""
        settings = Settings()
        assert settings.PROJECT_NAME == "Star Wars API"
        assert settings.DEBUG is True  # Set in .env file
        assert settings.DATABASE_URL.startswith("sqlite")

    def test_settings_from_env(self):
        """Test settings loaded from environment variables"""
        env_vars = {
            "PROJECT_NAME": "Test Star Wars API",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://test:test@localhost/test"
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.PROJECT_NAME == "Test Star Wars API"
            assert settings.DEBUG is True
            assert settings.DATABASE_URL == "postgresql://test:test@localhost/test"

    def test_database_url_validation(self):
        """Test database URL validation"""
        # Test valid URLs
        valid_urls = [
            "sqlite:///./test.db",
            "postgresql://user:pass@localhost/db",
            "mysql://user:pass@localhost/db"
        ]
        
        for url in valid_urls:
            with patch.dict(os.environ, {"DATABASE_URL": url}):
                settings = Settings()
                assert settings.DATABASE_URL == url

    def test_swapi_base_url_default(self):
        """Test SWAPI base URL default value"""
        settings = Settings()
        assert settings.SWAPI_BASE_URL == "https://swapi.dev/api"

    def test_swapi_base_url_from_env(self):
        """Test SWAPI base URL from environment"""
        with patch.dict(os.environ, {"SWAPI_BASE_URL": "https://custom-swapi.com/api"}):
            settings = Settings()
            assert settings.SWAPI_BASE_URL == "https://custom-swapi.com/api"
