"""Integration tests for order endpoints.

Tests for task 20: Implement order router with GET /order endpoint (order listing).
"""
import pytest
import pytest_asyncio
from decimal import Decimal
from fastapi import status
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.core.security import create_access_token
from app.db.database import create_transaction, create_user, get_db_pool, update_transaction
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client for endpoint testing."""
    return TestClient(app)


@pytest_asyncio.fixture(loop_scope="session")
async def test_user():
    """Create a test user for authenticated endpoints."""
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_list_orders@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "List Orders Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id IN (SELECT id FROM users WHERE email = $1)", email)
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
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_record["id"])
        await conn.execute("DELETE FROM users WHERE id = $1", user_record["id"])


@pytest.fixture
def auth_token(test_user):
    """Generate a JWT token for the test user."""
    return create_access_token({"sub": test_user["email"]})


@pytest_asyncio.fixture(loop_scope="session")
async def authenticated_async_client(async_client, test_user):
    """Async test client with authentication headers."""
    token = create_access_token({"sub": test_user["email"]})
    async_client.headers = {"Authorization": f"Bearer {token}"}
    return async_client


@pytest.fixture
def authenticated_client(client, auth_token):
    """Test client with authentication headers."""
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_returns_all_orders_for_authenticated_user(test_user, authenticated_async_client):
    """Test GET /order returns all orders for authenticated user."""
    user_id = test_user["id"]
    
    # Create multiple transactions
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    tx3 = await create_transaction(user_id, "ADAUSDT", Decimal("1.00"), Decimal("100.0"))
    
    # Close one transaction (status=2)
    await update_transaction(tx1["id"], Decimal("51000.00"), 2)
    
    response = await authenticated_async_client.get("/order")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "orders" in data["data"]
    assert "unique_symbols" in data["data"]
    
    orders = data["data"]["orders"]
    assert len(orders) == 3
    
    # Verify all transactions are present
    order_ids = {order["id"] for order in orders}
    assert tx1["id"] in order_ids
    assert tx2["id"] in order_ids
    assert tx3["id"] in order_ids
    
    # Verify unique symbols
    unique_symbols = data["data"]["unique_symbols"]
    assert len(unique_symbols) == 3
    assert "BTCUSDT" in unique_symbols
    assert "ETHUSDT" in unique_symbols
    assert "ADAUSDT" in unique_symbols
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_requires_authentication(async_client):
    """Test GET /order requires authentication (returns 401 without token)."""
    response = await async_client.get("/order")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_filters_by_active_only_true(test_user, authenticated_async_client):
    """Test GET /order filters by active_only=True query parameter."""
    user_id = test_user["id"]
    
    # Create multiple transactions
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    
    # Close one transaction (status=2)
    await update_transaction(tx1["id"], Decimal("51000.00"), 2)
    
    # Get only active orders
    response = await authenticated_async_client.get("/order?active_only=true")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    orders = data["data"]["orders"]
    
    # Should only return active orders (status=1)
    assert len(orders) == 1
    assert orders[0]["id"] == tx2["id"]
    assert orders[0]["status"] == 1
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_filters_by_symbol(test_user, authenticated_async_client):
    """Test GET /order filters by symbol query parameter."""
    user_id = test_user["id"]
    
    # Create multiple transactions with different symbols
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    tx3 = await create_transaction(user_id, "ADAUSDT", Decimal("1.00"), Decimal("100.0"))
    
    # Filter by symbol
    response = await authenticated_async_client.get("/order?symbol=BTCUSDT")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    orders = data["data"]["orders"]
    
    # Should only return BTCUSDT orders
    assert len(orders) == 1
    assert orders[0]["id"] == tx1["id"]
    assert orders[0]["symbol"] == "BTCUSDT"
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_orders_results_by_status_asc_created_at_desc(test_user, authenticated_async_client):
    """Test GET /order orders results by status ASC, created_at DESC."""
    user_id = test_user["id"]
    
    # Create transactions with different statuses
    # Create them in a specific order to test sorting
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    tx3 = await create_transaction(user_id, "ADAUSDT", Decimal("1.00"), Decimal("100.0"))
    
    # Close tx2 (status=2)
    await update_transaction(tx2["id"], Decimal("3100.00"), 2)
    
    response = await authenticated_async_client.get("/order")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    orders = data["data"]["orders"]
    
    # Should be ordered by status ASC, then created_at DESC
    # Status 1 orders first (tx3, tx1), then status 2 (tx2)
    # Within status 1, newer first (tx3, then tx1)
    assert len(orders) == 3
    
    # First two should be status=1, ordered by created_at DESC (newer first)
    assert orders[0]["status"] == 1
    assert orders[1]["status"] == 1
    # Last should be status=2
    assert orders[2]["status"] == 2
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_includes_computed_fields(test_user, authenticated_async_client):
    """Test GET /order includes computed fields (diff, buyAggregate, sellAggregate, diffDollar)."""
    user_id = test_user["id"]
    
    # Create a transaction and close it
    tx = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    await update_transaction(tx["id"], Decimal("51000.00"), 2)
    
    response = await authenticated_async_client.get("/order")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    orders = data["data"]["orders"]
    
    # Find the closed order
    closed_order = next((o for o in orders if o["status"] == 2), None)
    assert closed_order is not None
    
    # Verify computed fields
    assert "diff" in closed_order
    assert closed_order["diff"] == "1000.00"  # 51000 - 50000
    
    assert "buyAggregate" in closed_order
    assert closed_order["buyAggregate"] == "5000.00"  # 50000 * 0.1
    
    assert "sellAggregate" in closed_order
    assert closed_order["sellAggregate"] == "5100.00"  # 51000 * 0.1
    
    assert "diffDollar" in closed_order
    assert closed_order["diffDollar"] == "100.00"  # (51000 - 50000) * 0.1
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_includes_unique_symbols_list(test_user, authenticated_async_client):
    """Test GET /order includes unique_symbols list in response."""
    user_id = test_user["id"]
    
    # Create transactions with multiple symbols (some duplicates)
    await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    await create_transaction(user_id, "ADAUSDT", Decimal("1.00"), Decimal("100.0"))
    await create_transaction(user_id, "BTCUSDT", Decimal("51000.00"), Decimal("0.05"))  # Duplicate symbol
    
    response = await authenticated_async_client.get("/order")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify unique symbols (should be sorted)
    unique_symbols = data["data"]["unique_symbols"]
    assert len(unique_symbols) == 3
    assert "ADAUSDT" in unique_symbols
    assert "BTCUSDT" in unique_symbols
    assert "ETHUSDT" in unique_symbols
    # Should be sorted
    assert unique_symbols == sorted(unique_symbols)
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_handles_null_sell_price_in_computed_fields(test_user, authenticated_async_client):
    """Test GET /order handles NULL sell_price in computed fields."""
    user_id = test_user["id"]
    
    # Create an active transaction (no sell_price)
    tx = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    
    response = await authenticated_async_client.get("/order")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    orders = data["data"]["orders"]
    
    # Find the active order
    active_order = next((o for o in orders if o["id"] == tx["id"]), None)
    assert active_order is not None
    assert active_order["status"] == 1
    
    # Verify computed fields handle NULL sell_price
    assert active_order["sell_price"] is None
    assert active_order["diff"] is None  # diff should be None when sell_price is NULL
    assert active_order["buyAggregate"] == "5000.00"  # buyAggregate should still be calculated
    assert active_order["sellAggregate"] is None  # sellAggregate should be None
    assert active_order["diffDollar"] == "0"  # diffDollar should be 0 for active orders
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
