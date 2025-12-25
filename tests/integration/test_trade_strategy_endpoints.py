"""Integration tests for trade strategy endpoints.

Tests for task 24: Implement trade_strategy router with GET, POST, PUT, DELETE endpoints.
"""
import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.core.security import create_access_token
from app.db.database import (
    create_strategy,
    create_trade_strategy,
    create_user,
    get_db_pool,
    get_trade_strategy_by_id,
    get_trade_strategies,
    soft_delete_trade_strategy,
)
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client for endpoint testing."""
    return TestClient(app)


@pytest_asyncio.fixture
async def test_user():
    """Create a test user for authenticated endpoints."""
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_trade_strategy@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Trade Strategy Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies")
        await conn.execute("DELETE FROM strategies")
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
        await conn.execute("DELETE FROM trade_strategies")
        await conn.execute("DELETE FROM strategies")
        await conn.execute("DELETE FROM users WHERE id = $1", user_record["id"])


@pytest_asyncio.fixture
async def test_strategy():
    """Create a test strategy for trade strategy endpoints."""
    strategy = await create_strategy("Test Strategy", "test-strategy")
    
    yield strategy
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy["id"])


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
async def test_get_trade_strategy_returns_all_trade_strategies_including_soft_deleted(test_user, test_strategy, authenticated_client):
    """Test GET /trade-strategy returns all trade strategies including soft-deleted."""
    # Create multiple trade strategies
    ts1 = await create_trade_strategy("BTCUSDT", test_strategy["id"], "5m")
    ts2 = await create_trade_strategy("ETHUSDT", test_strategy["id"], "15m")
    ts3 = await create_trade_strategy("ADAUSDT", test_strategy["id"], "1h")
    
    # Soft delete one trade strategy
    await soft_delete_trade_strategy(ts2["id"])
    
    # Get all trade strategies (including soft-deleted by default)
    response = authenticated_client.get("/trade-strategy")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "trade_strategies" in data["data"]
    
    trade_strategies = data["data"]["trade_strategies"]
    assert len(trade_strategies) >= 3
    
    # Verify our created trade strategies are in the results
    trade_strategy_ids = {ts["id"] for ts in trade_strategies}
    assert ts1["id"] in trade_strategy_ids
    assert ts2["id"] in trade_strategy_ids  # Soft-deleted should still be included
    assert ts3["id"] in trade_strategy_ids
    
    # Verify soft-deleted trade strategy has deleted_at set
    ts2_response = next(ts for ts in trade_strategies if ts["id"] == ts2["id"])
    assert ts2_response["deleted_at"] is not None
    
    # Verify non-deleted trade strategies have deleted_at as None
    ts1_response = next(ts for ts in trade_strategies if ts["id"] == ts1["id"])
    assert ts1_response["deleted_at"] is None
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id IN ($1, $2, $3)", ts1["id"], ts2["id"], ts3["id"])


@pytest.mark.asyncio
async def test_get_trade_strategy_excludes_soft_deleted_when_include_deleted_false(test_user, test_strategy, authenticated_client):
    """Test GET /trade-strategy excludes soft-deleted when include_deleted=false."""
    # Create trade strategies
    ts1 = await create_trade_strategy("BTCUSDT", test_strategy["id"], "5m")
    ts2 = await create_trade_strategy("ETHUSDT", test_strategy["id"], "15m")
    
    # Soft delete one trade strategy
    await soft_delete_trade_strategy(ts2["id"])
    
    # Get trade strategies excluding soft-deleted
    response = authenticated_client.get("/trade-strategy?include_deleted=false")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    trade_strategies = data["data"]["trade_strategies"]
    
    # Should only include active trade strategy
    trade_strategy_ids = {ts["id"] for ts in trade_strategies}
    assert ts1["id"] in trade_strategy_ids
    assert ts2["id"] not in trade_strategy_ids  # Soft-deleted should be excluded
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id IN ($1, $2)", ts1["id"], ts2["id"])


@pytest.mark.asyncio
async def test_get_trade_strategy_requires_authentication(client):
    """Test GET /trade-strategy requires authentication (returns 401 without token)."""
    response = client.get("/trade-strategy")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_post_trade_strategy_creates_trade_strategy_with_symbol_strategy_id_optional_timestamp(test_user, test_strategy, authenticated_client):
    """Test POST /trade-strategy creates trade strategy with symbol, strategy_id, optional timestamp."""
    symbol = "BTCUSDT"
    strategy_id = test_strategy["id"]
    timestamp = "15m"
    
    # Clean up any existing trade strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", symbol, strategy_id)
    
    response = authenticated_client.post(
        "/trade-strategy",
        json={"symbol": symbol, "strategy_id": strategy_id, "timestamp": timestamp}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["symbol"] == symbol
    assert data["data"]["strategy_id"] == strategy_id
    assert data["data"]["timestamp"] == timestamp
    assert "id" in data["data"]
    assert "created_at" in data["data"]
    assert "updated_at" in data["data"]
    assert data["data"]["deleted_at"] is None
    
    # Verify it was actually created in the database
    trade_strategy = await get_trade_strategy_by_id(data["data"]["id"])
    assert trade_strategy is not None
    assert trade_strategy["symbol"] == symbol
    assert trade_strategy["strategy_id"] == strategy_id
    assert trade_strategy["timestamp"] == timestamp
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", data["data"]["id"])


@pytest.mark.asyncio
async def test_post_trade_strategy_defaults_timestamp_to_5m_if_not_provided(test_user, test_strategy, authenticated_client):
    """Test POST /trade-strategy defaults timestamp to '5m' if not provided."""
    symbol = "ETHUSDT"
    strategy_id = test_strategy["id"]
    
    # Clean up any existing trade strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", symbol, strategy_id)
    
    response = authenticated_client.post(
        "/trade-strategy",
        json={"symbol": symbol, "strategy_id": strategy_id}  # No timestamp provided
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["symbol"] == symbol
    assert data["data"]["strategy_id"] == strategy_id
    assert data["data"]["timestamp"] == "5m"  # Should default to '5m'
    
    # Verify it was actually created with default timestamp
    trade_strategy = await get_trade_strategy_by_id(data["data"]["id"])
    assert trade_strategy is not None
    assert trade_strategy["timestamp"] == "5m"
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", data["data"]["id"])


@pytest.mark.asyncio
async def test_post_trade_strategy_validates_symbol_max_15_chars(test_user, test_strategy, authenticated_client):
    """Test POST /trade-strategy validates symbol (max 15 chars)."""
    # Symbol with 16 characters (exceeds max)
    symbol = "A" * 16
    strategy_id = test_strategy["id"]
    
    response = authenticated_client.post(
        "/trade-strategy",
        json={"symbol": symbol, "strategy_id": strategy_id}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    # Should have validation error for symbol length


@pytest.mark.asyncio
async def test_post_trade_strategy_returns_400_when_strategy_id_does_not_exist(test_user, authenticated_client):
    """Test POST /trade-strategy returns 400 when strategy_id does not exist (foreign key constraint)."""
    symbol = "BTCUSDT"
    non_existent_strategy_id = 99999
    
    response = authenticated_client.post(
        "/trade-strategy",
        json={"symbol": symbol, "strategy_id": non_existent_strategy_id}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "does not exist" in data["detail"].lower() or "strategy" in data["detail"].lower()


@pytest.mark.asyncio
async def test_post_trade_strategy_requires_authentication(client):
    """Test POST /trade-strategy requires authentication (returns 401 without token)."""
    response = client.post(
        "/trade-strategy",
        json={"symbol": "BTCUSDT", "strategy_id": 1}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_put_trade_strategy_updates_trade_strategy_fields(test_user, test_strategy, authenticated_client):
    """Test PUT /trade-strategy/{trade_strategy_id} updates trade strategy fields."""
    # Create a trade strategy first
    trade_strategy = await create_trade_strategy("BTCUSDT", test_strategy["id"], "5m")
    trade_strategy_id = trade_strategy["id"]
    
    # Create another strategy for update
    strategy2 = await create_strategy("Updated Strategy", "updated-strategy")
    
    # Update trade strategy
    response = authenticated_client.put(
        f"/trade-strategy/{trade_strategy_id}",
        json={"symbol": "ETHUSDT", "strategy_id": strategy2["id"], "timestamp": "15m"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["symbol"] == "ETHUSDT"
    assert data["data"]["strategy_id"] == strategy2["id"]
    assert data["data"]["timestamp"] == "15m"
    assert data["data"]["id"] == trade_strategy_id
    
    # Verify it was actually updated in the database
    updated_trade_strategy = await get_trade_strategy_by_id(trade_strategy_id)
    assert updated_trade_strategy["symbol"] == "ETHUSDT"
    assert updated_trade_strategy["strategy_id"] == strategy2["id"]
    assert updated_trade_strategy["timestamp"] == "15m"
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy2["id"])


@pytest.mark.asyncio
async def test_put_trade_strategy_returns_404_when_trade_strategy_not_found(test_user, test_strategy, authenticated_client):
    """Test PUT /trade-strategy/{trade_strategy_id} returns 404 when trade_strategy not found."""
    non_existent_id = 99999
    
    response = authenticated_client.put(
        f"/trade-strategy/{non_existent_id}",
        json={"symbol": "BTCUSDT"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_put_trade_strategy_returns_400_when_strategy_id_does_not_exist(test_user, test_strategy, authenticated_client):
    """Test PUT /trade-strategy/{trade_strategy_id} returns 400 when strategy_id does not exist."""
    # Create a trade strategy first
    trade_strategy = await create_trade_strategy("BTCUSDT", test_strategy["id"], "5m")
    trade_strategy_id = trade_strategy["id"]
    
    non_existent_strategy_id = 99999
    
    # Try to update with non-existent strategy_id
    response = authenticated_client.put(
        f"/trade-strategy/{trade_strategy_id}",
        json={"strategy_id": non_existent_strategy_id}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "does not exist" in data["detail"].lower() or "strategy" in data["detail"].lower()
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)


@pytest.mark.asyncio
async def test_put_trade_strategy_requires_authentication(client):
    """Test PUT /trade-strategy/{trade_strategy_id} requires authentication (returns 401 without token)."""
    response = client.put(
        "/trade-strategy/1",
        json={"symbol": "BTCUSDT"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_trade_strategy_soft_deletes_trade_strategy(test_user, test_strategy, authenticated_client):
    """Test DELETE /trade-strategy/{trade_strategy_id} soft deletes trade strategy."""
    # Create a trade strategy first
    trade_strategy = await create_trade_strategy("BTCUSDT", test_strategy["id"], "5m")
    trade_strategy_id = trade_strategy["id"]
    
    # Verify it's not deleted
    trade_strategy_before = await get_trade_strategy_by_id(trade_strategy_id)
    assert trade_strategy_before["deleted_at"] is None
    
    # Soft delete trade strategy
    response = authenticated_client.delete(f"/trade-strategy/{trade_strategy_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    assert "soft deleted" in data["message"].lower()
    
    # Verify deleted_at is set in database
    trade_strategy_after = await get_trade_strategy_by_id(trade_strategy_id)
    assert trade_strategy_after is not None  # Record should still exist
    assert trade_strategy_after["deleted_at"] is not None  # But deleted_at should be set
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)


@pytest.mark.asyncio
async def test_delete_trade_strategy_does_not_remove_record_from_database(test_user, test_strategy, authenticated_client):
    """Test DELETE /trade-strategy/{trade_strategy_id} does not remove record from database."""
    # Create a trade strategy first
    trade_strategy = await create_trade_strategy("ETHUSDT", test_strategy["id"], "15m")
    trade_strategy_id = trade_strategy["id"]
    
    # Soft delete trade strategy
    response = authenticated_client.delete(f"/trade-strategy/{trade_strategy_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify record still exists in database (not physically deleted)
    trade_strategy_after = await get_trade_strategy_by_id(trade_strategy_id)
    assert trade_strategy_after is not None
    assert trade_strategy_after["id"] == trade_strategy_id
    assert trade_strategy_after["symbol"] == "ETHUSDT"
    assert trade_strategy_after["deleted_at"] is not None  # But marked as deleted
    
    # Verify it appears in get_trade_strategies with include_deleted=True
    all_trade_strategies = await get_trade_strategies(include_deleted=True)
    trade_strategy_ids = {ts["id"] for ts in all_trade_strategies}
    assert trade_strategy_id in trade_strategy_ids
    
    # Verify it does NOT appear in get_trade_strategies with include_deleted=False
    active_trade_strategies = await get_trade_strategies(include_deleted=False)
    active_trade_strategy_ids = {ts["id"] for ts in active_trade_strategies}
    assert trade_strategy_id not in active_trade_strategy_ids
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)


@pytest.mark.asyncio
async def test_delete_trade_strategy_returns_404_when_trade_strategy_not_found(test_user, authenticated_client):
    """Test DELETE /trade-strategy/{trade_strategy_id} returns 404 when trade_strategy not found."""
    non_existent_id = 99999
    
    response = authenticated_client.delete(f"/trade-strategy/{non_existent_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_trade_strategy_requires_authentication(client):
    """Test DELETE /trade-strategy/{trade_strategy_id} requires authentication (returns 401 without token)."""
    response = client.delete("/trade-strategy/1")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_all_endpoints_require_authentication(client):
    """Test all endpoints require authentication."""
    # Test GET /trade-strategy
    response = client.get("/trade-strategy")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test POST /trade-strategy
    response = client.post("/trade-strategy", json={"symbol": "BTCUSDT", "strategy_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test PUT /trade-strategy/{trade_strategy_id}
    response = client.put("/trade-strategy/1", json={"symbol": "BTCUSDT"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test DELETE /trade-strategy/{trade_strategy_id}
    response = client.delete("/trade-strategy/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

