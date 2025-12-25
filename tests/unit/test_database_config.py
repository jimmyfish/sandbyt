"""Test to verify that tests are using the test database configuration.

This test ensures that the test suite is configured to use the test database
from .env.test.local and not the production database.
"""
import os
import pytest
from app.core.config import settings


def test_uses_test_database():
    """Verify that tests are configured to use test database, not production."""
    # Check environment variable
    env_db_name = os.getenv("DB_NAME", "")
    
    # Check settings object
    settings_db_name = settings.DB_NAME
    
    # Both should be set to test database (not "goblin")
    assert settings_db_name != "goblin", (
        f"Tests are using production database 'goblin'. "
        f"Please ensure .env.test.local has DB_NAME set to a test database. "
        f"Current DB_NAME: {settings_db_name}"
    )
    
    assert env_db_name != "goblin", (
        f"Environment variable DB_NAME is set to production database 'goblin'. "
        f"Please ensure .env.test.local has DB_NAME set to a test database. "
        f"Current DB_NAME: {env_db_name}"
    )
    
    # Verify test database name is actually set
    assert settings_db_name, "DB_NAME is not set in test configuration"
    assert env_db_name, "DB_NAME environment variable is not set"


def test_test_database_configuration_loaded():
    """Verify that test database configuration is loaded from .env.test.local."""
    # The test database should have a different name than production
    assert settings.DB_NAME != "goblin"
    
    # Verify other database settings are loaded
    assert settings.DB_HOST is not None
    assert settings.DB_PORT is not None
    assert settings.DB_USER is not None

