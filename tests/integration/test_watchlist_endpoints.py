"""Integration tests for watchlist endpoints.

Tests for task 21: Implement watchlist router with GET, POST, DELETE endpoints.
"""
import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.core.security import create_access_token
from app.db.database import create_user, create_watchlist, delete_watchlist, get_db_pool, get_watchlists
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client for endpoint testing."""
    return TestClient(app)


@pytest_asyncio.fixture
async def test_user():
    """Create a test user for authenticated endpoints."""
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_watchlist@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Watchlist Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists")
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    
    yield {
        "id": user_record["id"],
        "email": email,
        "name": name,
        "balance": user_record["balance"],
    }
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists")
        await conn.execute("DELETE FROM users WHERE id = $1", user_record["id"])


@pytest.fixture
def auth_token(test_user):
    """Generate a JWT token for the test user."""
    return create_access_token({"sub": test_user["email"]})


@pytest.fixture
def authenticated_client(client, auth_token):
    """Test client with authentication headers."""
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client


@pytest.mark.asyncio
async def test_get_watchlist_returns_all_watchlists(test_user, authenticated_client):
    """Test GET /watchlist returns all watchlists."""
    # Create multiple watchlist entries
    w1 = await create_watchlist("BTCUSDT")
    w2 = await create_watchlist("ETHUSDT")
    w3 = await create_watchlist("ADAUSDT")
    
    response = authenticated_client.get("/watchlist")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "watchlists" in data["data"]
    assert "unique_symbols" in data["data"]
    
    watchlists = data["data"]["watchlists"]
    assert len(watchlists) >= 3
    
    # Verify our created watchlists are in the results
    watchlist_ids = {w["id"] for w in watchlists}
    assert w1["id"] in watchlist_ids
    assert w2["id"] in watchlist_ids
    assert w3["id"] in watchlist_ids
    
    # Verify unique symbols
    unique_symbols = data["data"]["unique_symbols"]
    assert "BTCUSDT" in unique_symbols
    assert "ETHUSDT" in unique_symbols
    assert "ADAUSDT" in unique_symbols
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol IN ($1, $2, $3)", "BTCUSDT", "ETHUSDT", "ADAUSDT")


@pytest.mark.asyncio
async def test_get_watchlist_requires_authentication(client):
    """Test GET /watchlist requires authentication (returns 401 without token)."""
    response = client.get("/watchlist")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_post_watchlist_creates_watchlist_entry_successfully(test_user, authenticated_client):
    """Test POST /watchlist creates watchlist entry successfully."""
    symbol = "BTCUSDT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    response = authenticated_client.post(
        "/watchlist",
        json={"symbol": symbol}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["symbol"] == symbol
    assert "id" in data["data"]
    assert "created_at" in data["data"]
    
    # Verify it was actually created in the database
    watchlists = await get_watchlists()
    watchlist_symbols = {w["symbol"] for w in watchlists}
    assert symbol in watchlist_symbols
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)


@pytest.mark.asyncio
async def test_post_watchlist_validates_symbol_max_10_chars(test_user, authenticated_client):
    """Test POST /watchlist validates symbol (max 10 chars)."""
    # Try to create watchlist with symbol exceeding 10 characters
    response = authenticated_client.post(
        "/watchlist",
        json={"symbol": "BTCUSDTEXTRA"}  # 13 characters
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    # Pydantic validation error should mention symbol length


@pytest.mark.asyncio
async def test_post_watchlist_uppercases_symbol(test_user, authenticated_client):
    """Test POST /watchlist uppercases symbol."""
    symbol = "btcusdt"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", "BTCUSDT")
    
    response = authenticated_client.post(
        "/watchlist",
        json={"symbol": symbol}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["data"]["symbol"] == "BTCUSDT"  # Should be uppercased
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", "BTCUSDT")


@pytest.mark.asyncio
async def test_delete_watchlist_deletes_watchlist_entry_successfully(test_user, authenticated_client):
    """Test DELETE /watchlist/{symbol} deletes watchlist entry successfully."""
    symbol = "ETHUSDT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Create watchlist entry first
    await create_watchlist(symbol)
    
    # Verify it exists
    watchlists_before = await get_watchlists()
    watchlist_symbols_before = {w["symbol"] for w in watchlists_before}
    assert symbol in watchlist_symbols_before
    
    # Delete watchlist entry
    response = authenticated_client.delete(f"/watchlist/{symbol}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    assert symbol in data["message"]
    
    # Verify it was actually deleted
    watchlists_after = await get_watchlists()
    watchlist_symbols_after = {w["symbol"] for w in watchlists_after}
    assert symbol not in watchlist_symbols_after


@pytest.mark.asyncio
async def test_delete_watchlist_returns_404_when_symbol_not_found(test_user, authenticated_client):
    """Test DELETE /watchlist/{symbol} returns 404 when symbol not found."""
    symbol = "NONEXISTENT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Try to delete non-existent watchlist
    response = authenticated_client.delete(f"/watchlist/{symbol}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_watchlist_uppercases_symbol(test_user, authenticated_client):
    """Test DELETE /watchlist/{symbol} uppercases symbol."""
    symbol = "btcusdt"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", "BTCUSDT")
    
    # Create watchlist entry with uppercase symbol
    await create_watchlist("BTCUSDT")
    
    # Delete using lowercase symbol
    response = authenticated_client.delete(f"/watchlist/{symbol}")
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verify it was deleted
    watchlists = await get_watchlists()
    watchlist_symbols = {w["symbol"] for w in watchlists}
    assert "BTCUSDT" not in watchlist_symbols


@pytest.mark.asyncio
async def test_delete_watchlist_validates_symbol_max_10_chars(test_user, authenticated_client):
    """Test DELETE /watchlist/{symbol} validates symbol max 10 chars."""
    # Try to delete with symbol exceeding 10 characters
    response = authenticated_client.delete("/watchlist/BTCUSDTEXTRA")  # 13 characters
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "10 characters" in data["detail"].lower()


@pytest.mark.asyncio
async def test_all_endpoints_require_authentication(client):
    """Test all endpoints require authentication."""
    # Test GET /watchlist
    response = client.get("/watchlist")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test POST /watchlist
    response = client.post("/watchlist", json={"symbol": "BTCUSDT"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test DELETE /watchlist/{symbol}
    response = client.delete("/watchlist/BTCUSDT")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

