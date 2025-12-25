"""Pytest configuration and fixtures for test suite.

This module configures the test environment to use a separate test database
from .env.test.local to prevent tests from altering the real database.
"""
import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv

# Load test environment variables BEFORE importing app modules
# This ensures test database configuration is loaded first and takes precedence
# override=True ensures test env vars override any existing ones
load_dotenv(".env.test.local", override=True)


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    """Configure test environment to use .env.test.local settings.
    
    This fixture runs automatically before any tests and ensures that
    the test database configuration from .env.test.local is used.
    It reloads the test environment to ensure it takes precedence over
    any .env file that might be loaded by config.py.
    """
    # Reload test environment variables to ensure they override .env
    # This is important because config.py calls load_dotenv() which loads .env
    load_dotenv(".env.test.local", override=True)
    
    # Verify test database is configured
    test_db_name = os.getenv("DB_NAME", "")
    if not test_db_name or test_db_name == "goblin":
        pytest.fail(
            "Test database name not configured in .env.test.local. "
            "Please ensure DB_NAME is set to a test database (not 'goblin'). "
            f"Current DB_NAME: {test_db_name}"
        )
    
    yield
    
    # Cleanup if needed
    pass


@pytest_asyncio.fixture(scope="session", autouse=True)
async def reset_db_pool():
    """Reset the database pool to ensure it uses test database settings.
    
    This fixture ensures that the global database pool is reset at the start
    of the test session so it gets recreated with test database configuration
    from .env.test.local. It also initializes the database schema.
    """
    from app.db import database
    from app.db.database import get_db_pool, init_db
    
    # Reset the global pool to force recreation with test settings
    if database._db_pool is not None:
        await database._db_pool.close()
        database._db_pool = None
    
    # Initialize database schema (create all tables)
    await get_db_pool()
    await init_db()
    
    yield
    
    # Cleanup: close the pool after all tests
    if database._db_pool is not None:
        await database._db_pool.close()
        database._db_pool = None


@pytest_asyncio.fixture(autouse=True)
async def verify_test_database():
    """Verify that tests are using the test database, not production.
    
    This fixture runs before each test to ensure we're connected to the
    test database. It checks both environment variables and settings object.
    """
    from app.core.config import settings
    
    # Verify we're using test database (check both env and settings)
    env_db_name = os.getenv("DB_NAME", "")
    settings_db_name = settings.DB_NAME
    
    if settings_db_name == "goblin" or env_db_name == "goblin":
        pytest.fail(
            "Tests are configured to use production database 'goblin'. "
            "Please ensure .env.test.local has DB_NAME set to a test database. "
            f"Environment DB_NAME: {env_db_name}, Settings DB_NAME: {settings_db_name}"
        )
    
    yield

