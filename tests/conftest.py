"""Pytest configuration and fixtures for test suite.

This module configures the test environment to use a separate test database
from .env.test.local to prevent tests from altering the real database.

Event Loop Configuration:
    pytest-asyncio is configured to use a session-scoped event loop for all
    async fixtures and tests. This ensures the asyncpg connection pool (which
    is bound to the event loop at creation time) remains valid throughout the
    entire test session.
    
    See: https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    See: https://github.com/encode/httpx/discussions/2959
"""
import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv
import httpx

# Configure pytest-asyncio to use session-scoped event loop for all async tests
# This ensures all async tests and fixtures run in the same event loop as the
# database connection pool, preventing "attached to a different loop" errors.
pytest_plugins = ('pytest_asyncio',)


def pytest_configure(config):
    """Configure pytest-asyncio default loop scope."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )

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


@pytest.fixture(scope="session", autouse=True)
def reset_db_pool_sync(request):
    """Reset the database pool reference to ensure it uses test database settings.
    
    This synchronous fixture ensures that the global database pool is reset at the start
    of the test session. The actual pool will be created lazily when tests need it,
    ensuring it's created in the correct event loop context.
    
    Uses a finalizer to clean up the pool at session end without requiring an active
    event loop, following Stack Overflow guidance for handling closed loops.
    """
    from app.db import database
    
    # Reset the global pool reference to force recreation with test settings
    if database._db_pool is not None:
        # Note: We can't await here in a sync fixture, so we just reset the reference
        # The pool will be closed properly in the finalizer
        try:
            database._db_pool.terminate()
        except Exception:
            pass
        finally:
            database._db_pool = None
    
    def _cleanup():
        """Finalizer to clean up the database pool at session end.
        
        Uses terminate() which doesn't require an active event loop,
        preventing "Event loop is closed" errors.
        """
        if database._db_pool is not None:
            try:
                database._db_pool.terminate()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                database._db_pool = None
    
    # Register finalizer to run at session end
    request.addfinalizer(_cleanup)
    
    yield


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def initialize_db_session():
    """Initialize database pool and schema at session start.
    
    This session-scoped fixture creates the database pool once for the entire
    test session. The pool persists across all tests, avoiding "different loop"
    errors by using a session-scoped event loop.
    
    The loop_scope="session" ensures this fixture runs in the session-scoped
    event loop, matching the asyncio_default_fixture_loop_scope configuration.
    
    Based on guidance from:
    - https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    - https://github.com/encode/httpx/discussions/2959
    """
    from app.db import database
    from app.db.database import get_db_pool, init_db
    
    # Reset any existing pool
    if database._db_pool is not None:
        try:
            database._db_pool.terminate()
        except Exception:
            pass
        finally:
            database._db_pool = None
    
    # Create the pool in the session-scoped event loop
    pool = await get_db_pool()
    
    # Initialize database schema
    await init_db()
    
    yield pool
    
    # Cleanup: close the pool at session end
    if database._db_pool is not None:
        try:
            await database._db_pool.close()
        except Exception:
            try:
                database._db_pool.terminate()
            except Exception:
                pass
        finally:
            database._db_pool = None


@pytest_asyncio.fixture(loop_scope="session", scope="function", autouse=True)
async def ensure_db_schema():
    """Ensure database schema is initialized (idempotent check).
    
    This fixture runs before each test to ensure the schema exists.
    The pool is managed by the session-scoped fixture above.
    
    Uses loop_scope="session" to run in the same event loop as the pool,
    preventing "attached to a different loop" errors.
    """
    from app.db.database import init_db
    await init_db()
    yield


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def verify_test_database():
    """Verify that tests are using the test database, not production.
    
    This fixture runs before each test to ensure we're connected to the
    test database. It checks both environment variables and settings object.
    
    Uses loop_scope="session" to run in the same event loop as the pool.
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


@pytest_asyncio.fixture(loop_scope="session")
async def async_client():
    """Async HTTP client for testing endpoints with async database operations.
    
    Use this fixture instead of TestClient when tests need to:
    1. Make HTTP requests to the API
    2. Perform async database operations in the same test
    
    This avoids "attached to a different loop" errors by keeping everything
    in the same event loop.
    """
    from app.main import app
    
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True
    ) as client:
        yield client

