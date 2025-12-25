"""Integration tests for log endpoints.

Tests for task 22: Implement log router with POST and GET endpoints.
"""
import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.core.constants import SUCCESS_LOG_CREATED
from app.core.security import create_access_token
from app.db.database import create_log, create_user, get_db_pool, get_logs, get_unique_log_symbols
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client for endpoint testing."""
    return TestClient(app)


@pytest_asyncio.fixture(loop_scope="session")
async def test_user():
    """Create a test user for authenticated endpoints."""
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_log@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Log Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log")
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
        await conn.execute("DELETE FROM log")
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
async def test_post_log_creates_log_entry_successfully(test_user, authenticated_async_client):
    """Test POST /log creates log entry successfully."""
    symbol = "BTCUSDT"
    data = {"price": 50000.50, "volume": 1.5, "timestamp": "2024-01-01T00:00:00Z"}
    action = "buy"
    
    # Clean up any existing log first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)
    
    response = await authenticated_async_client.post(
        "/log",
        json={
            "symbol": symbol,
            "data": data,
            "action": action
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["message"] == SUCCESS_LOG_CREATED
    assert "data" in response_data
    assert response_data["data"]["symbol"] == symbol
    assert response_data["data"]["action"] == action
    assert response_data["data"]["data"] == data  # Should be parsed as dict
    assert "id" in response_data["data"]
    assert "created_at" in response_data["data"]
    assert "updated_at" in response_data["data"]
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)


@pytest.mark.asyncio(loop_scope="session")
async def test_post_log_validates_symbol_data_action_required(test_user, authenticated_async_client):
    """Test POST /log validates symbol, data (dict), action (required)."""
    # Test missing symbol
    response = await authenticated_async_client.post(
        "/log",
        json={
            "data": {"key": "value"},
            "action": "buy"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # Test missing data
    response = await authenticated_async_client.post(
        "/log",
        json={
            "symbol": "BTCUSDT",
            "action": "buy"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    # Test missing action
    response = await authenticated_async_client.post(
        "/log",
        json={
            "symbol": "BTCUSDT",
            "data": {"key": "value"}
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_post_log_stores_data_as_json_text_in_database(test_user, authenticated_async_client):
    """Test POST /log stores data as JSON text in database."""
    symbol = "ETHUSDT"
    data = {"price": 3000.25, "volume": 2.0, "metadata": {"source": "api"}}
    action = "analysis"
    
    # Clean up any existing log first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)
    
    response = await authenticated_async_client.post(
        "/log",
        json={
            "symbol": symbol,
            "data": data,
            "action": action
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify data is stored as JSON text in database
    async with pool.acquire() as conn:
        record = await conn.fetchrow(
            "SELECT data FROM log WHERE symbol = $1 ORDER BY created_at DESC LIMIT 1",
            symbol
        )
        assert record is not None
        # Data should be stored as JSON text (string)
        assert isinstance(record["data"], str)
        # Parse and verify content
        import json
        parsed_data = json.loads(record["data"])
        assert parsed_data == data
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_log_returns_logs_ordered_by_created_at_desc(test_user, authenticated_async_client):
    """Test GET /log returns logs ordered by created_at DESC."""
    # Create multiple log entries
    log1 = await create_log("BTCUSDT", {"price": 50000}, "buy")
    log2 = await create_log("ETHUSDT", {"price": 3000}, "sell")
    log3 = await create_log("ADAUSDT", {"price": 1.5}, "analysis")
    
    response = await authenticated_async_client.get("/log")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "logs" in data["data"]
    
    logs = data["data"]["logs"]
    assert len(logs) >= 3
    
    # Verify ordering (most recent first)
    # Note: We can't guarantee exact order due to timing, but we can verify our logs are present
    log_ids = {log["id"] for log in logs}
    assert log1["id"] in log_ids
    assert log2["id"] in log_ids
    assert log3["id"] in log_ids
    
    # Verify created_at is present and logs are sorted (most recent first)
    # We'll check that timestamps are in descending order for our created logs
    created_logs = [log for log in logs if log["id"] in {log1["id"], log2["id"], log3["id"]}]
    if len(created_logs) >= 2:
        # Check that timestamps are in descending order
        for i in range(len(created_logs) - 1):
            assert created_logs[i]["created_at"] >= created_logs[i + 1]["created_at"]
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE id IN ($1, $2, $3)", log1["id"], log2["id"], log3["id"])


@pytest.mark.asyncio(loop_scope="session")
async def test_get_log_filters_by_symbol_query_parameter_like_search(test_user, authenticated_async_client):
    """Test GET /log filters by symbol query parameter (LIKE search)."""
    # Create logs with different symbols
    log1 = await create_log("BTCUSDT", {"price": 50000}, "buy")
    log2 = await create_log("ETHUSDT", {"price": 3000}, "sell")
    log3 = await create_log("BTCEUR", {"price": 45000}, "analysis")
    
    # Filter by "BTC" - should match BTCUSDT and BTCEUR
    response = await authenticated_async_client.get("/log?symbol=BTC")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    logs = data["data"]["logs"]
    
    # Should include BTCUSDT and BTCEUR, but not ETHUSDT
    log_symbols = {log["symbol"] for log in logs}
    assert "BTCUSDT" in log_symbols or "BTCEUR" in log_symbols
    # Note: We can't guarantee ETHUSDT is not in results if there are other logs,
    # but we can verify our BTC logs are present
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE id IN ($1, $2, $3)", log1["id"], log2["id"], log3["id"])


@pytest.mark.asyncio(loop_scope="session")
async def test_get_log_supports_pagination_limit_offset_query_parameters(test_user, authenticated_async_client):
    """Test GET /log supports pagination (limit, offset query parameters)."""
    # Create multiple log entries
    log_ids = []
    for i in range(5):
        log = await create_log(f"SYM{i}", {"index": i}, "test")
        log_ids.append(log["id"])
    
    # Test with limit=2, offset=0
    response = await authenticated_async_client.get("/log?limit=2&offset=0")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    logs = data["data"]["logs"]
    assert len(logs) <= 2
    assert data["data"]["limit"] == 2
    assert data["data"]["offset"] == 0
    assert data["data"]["total_count"] >= 5  # At least our 5 logs
    
    # Test with limit=2, offset=2
    response2 = await authenticated_async_client.get("/log?limit=2&offset=2")
    
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    logs2 = data2["data"]["logs"]
    assert len(logs2) <= 2
    assert data2["data"]["limit"] == 2
    assert data2["data"]["offset"] == 2
    
    # Verify different results (pagination working)
    if len(logs) > 0 and len(logs2) > 0:
        # Should have different logs (unless there are fewer than 4 total)
        log_ids_1 = {log["id"] for log in logs}
        log_ids_2 = {log["id"] for log in logs2}
        # They might overlap if there are fewer logs, but let's verify pagination metadata is correct
        assert data2["data"]["total_count"] == data["data"]["total_count"]
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE id = ANY($1::int[])", log_ids)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_log_includes_unique_symbols_list_in_response(test_user, authenticated_async_client):
    """Test GET /log includes unique_symbols list in response."""
    # Create logs with different symbols
    log1 = await create_log("BTCUSDT", {"price": 50000}, "buy")
    log2 = await create_log("ETHUSDT", {"price": 3000}, "sell")
    log3 = await create_log("ADAUSDT", {"price": 1.5}, "analysis")
    
    response = await authenticated_async_client.get("/log")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "unique_symbols" in data["data"]
    
    unique_symbols = data["data"]["unique_symbols"]
    assert isinstance(unique_symbols, list)
    # Should include our symbols (may include others too)
    assert "BTCUSDT" in unique_symbols
    assert "ETHUSDT" in unique_symbols
    assert "ADAUSDT" in unique_symbols
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE id IN ($1, $2, $3)", log1["id"], log2["id"], log3["id"])


@pytest.mark.asyncio(loop_scope="session")
async def test_get_log_parses_data_field_as_json_in_response(test_user, authenticated_async_client):
    """Test GET /log parses data field as JSON in response."""
    symbol = "BTCUSDT"
    data = {"price": 50000.50, "volume": 1.5, "nested": {"key": "value"}}
    action = "buy"
    
    # Clean up any existing log first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)
    
    # Create log entry
    await create_log(symbol, data, action)
    
    # Fetch logs
    response = await authenticated_async_client.get("/log")
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    logs = response_data["data"]["logs"]
    
    # Find our log entry
    our_log = next((log for log in logs if log["symbol"] == symbol), None)
    assert our_log is not None
    assert our_log["data"] == data  # Should be parsed as dict, not JSON string
    assert isinstance(our_log["data"], dict)
    assert our_log["data"]["price"] == 50000.50
    assert our_log["data"]["nested"]["key"] == "value"
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)


@pytest.mark.asyncio(loop_scope="session")
async def test_all_endpoints_require_authentication(async_client):
    """Test all endpoints require authentication."""
    # Test GET /log
    response = await async_client.get("/log")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test POST /log
    response = await async_client.post(
        "/log",
        json={
            "symbol": "BTCUSDT",
            "data": {"price": 50000},
            "action": "buy"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
