"""Integration tests for strategy endpoints.

Tests for task 23: Implement strategy router with GET, POST, PUT, DELETE endpoints.
"""
import pytest
import pytest_asyncio
from fastapi import status
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.core.security import create_access_token
from app.db.database import (
    create_strategy,
    create_user,
    get_all_strategies,
    get_db_pool,
    get_strategy_by_id,
    soft_delete_strategy,
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
    email = "test_strategy@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Strategy Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
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
        await conn.execute("DELETE FROM strategies")
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
async def test_get_strategy_returns_all_strategies_including_soft_deleted(test_user, authenticated_client):
    """Test GET /strategy returns all strategies including soft-deleted."""
    # Create multiple strategies
    s1 = await create_strategy("Momentum Strategy", "momentum-strategy")
    s2 = await create_strategy("Mean Reversion Strategy", "mean-reversion-strategy")
    s3 = await create_strategy("Breakout Strategy", "breakout-strategy")
    
    # Soft delete one strategy
    await soft_delete_strategy(s2["id"])
    
    # Get all strategies (including soft-deleted by default)
    response = authenticated_client.get("/strategy")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "strategies" in data["data"]
    
    strategies = data["data"]["strategies"]
    assert len(strategies) >= 3
    
    # Verify our created strategies are in the results
    strategy_ids = {s["id"] for s in strategies}
    assert s1["id"] in strategy_ids
    assert s2["id"] in strategy_ids  # Soft-deleted should still be included
    assert s3["id"] in strategy_ids
    
    # Verify soft-deleted strategy has deleted_at set
    s2_response = next(s for s in strategies if s["id"] == s2["id"])
    assert s2_response["deleted_at"] is not None
    
    # Verify non-deleted strategies have deleted_at as None
    s1_response = next(s for s in strategies if s["id"] == s1["id"])
    assert s1_response["deleted_at"] is None
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id IN ($1, $2, $3)", s1["id"], s2["id"], s3["id"])


@pytest.mark.asyncio
async def test_get_strategy_excludes_soft_deleted_when_include_deleted_false(test_user, authenticated_client):
    """Test GET /strategy excludes soft-deleted when include_deleted=false."""
    # Create strategies
    s1 = await create_strategy("Active Strategy", "active-strategy")
    s2 = await create_strategy("Deleted Strategy", "deleted-strategy")
    
    # Soft delete one strategy
    await soft_delete_strategy(s2["id"])
    
    # Get strategies excluding soft-deleted
    response = authenticated_client.get("/strategy?include_deleted=false")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    strategies = data["data"]["strategies"]
    
    # Should only include active strategy
    strategy_ids = {s["id"] for s in strategies}
    assert s1["id"] in strategy_ids
    assert s2["id"] not in strategy_ids  # Soft-deleted should be excluded
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id IN ($1, $2)", s1["id"], s2["id"])


@pytest.mark.asyncio
async def test_get_strategy_requires_authentication(client):
    """Test GET /strategy requires authentication (returns 401 without token)."""
    response = client.get("/strategy")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_post_strategy_creates_strategy_with_name_and_optional_slug(test_user, authenticated_client):
    """Test POST /strategy creates strategy with name and optional slug."""
    name = "Test Strategy"
    slug = "test-strategy"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)
    
    response = authenticated_client.post(
        "/strategy",
        json={"name": name, "slug": slug}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["name"] == name
    assert data["data"]["slug"] == slug
    assert "id" in data["data"]
    assert "created_at" in data["data"]
    assert "updated_at" in data["data"]
    assert data["data"]["deleted_at"] is None
    
    # Verify it was actually created in the database
    strategy = await get_strategy_by_id(data["data"]["id"])
    assert strategy is not None
    assert strategy["name"] == name
    assert strategy["slug"] == slug
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", data["data"]["id"])


@pytest.mark.asyncio
async def test_post_strategy_auto_generates_slug_from_name_if_not_provided(test_user, authenticated_client):
    """Test POST /strategy auto-generates slug from name if not provided."""
    name = "Auto Generated Slug Strategy"
    expected_slug = "auto-generated-slug-strategy"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", expected_slug)
    
    response = authenticated_client.post(
        "/strategy",
        json={"name": name}  # No slug provided
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == name
    assert data["data"]["slug"] == expected_slug  # Should be auto-generated
    
    # Verify it was actually created with auto-generated slug
    strategy = await get_strategy_by_id(data["data"]["id"])
    assert strategy is not None
    assert strategy["slug"] == expected_slug
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", data["data"]["id"])


@pytest.mark.asyncio
async def test_post_strategy_requires_authentication(client):
    """Test POST /strategy requires authentication (returns 401 without token)."""
    response = client.post(
        "/strategy",
        json={"name": "Test Strategy"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_put_strategy_updates_strategy_fields(test_user, authenticated_client):
    """Test PUT /strategy/{strategy_id} updates strategy fields."""
    # Create a strategy first
    strategy = await create_strategy("Original Strategy", "original-strategy")
    strategy_id = strategy["id"]
    
    # Update strategy
    response = authenticated_client.put(
        f"/strategy/{strategy_id}",
        json={"name": "Updated Strategy", "slug": "updated-strategy"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "Updated Strategy"
    assert data["data"]["slug"] == "updated-strategy"
    assert data["data"]["id"] == strategy_id
    
    # Verify it was actually updated in the database
    updated_strategy = await get_strategy_by_id(strategy_id)
    assert updated_strategy["name"] == "Updated Strategy"
    assert updated_strategy["slug"] == "updated-strategy"
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_put_strategy_auto_generates_slug_when_name_updated(test_user, authenticated_client):
    """Test PUT /strategy/{strategy_id} auto-generates slug when name is updated."""
    # Create a strategy first
    strategy = await create_strategy("Original Strategy", "original-strategy")
    strategy_id = strategy["id"]
    
    # Update only name (slug should be auto-generated)
    response = authenticated_client.put(
        f"/strategy/{strategy_id}",
        json={"name": "New Strategy Name"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data"]["name"] == "New Strategy Name"
    assert data["data"]["slug"] == "new-strategy-name"  # Should be auto-generated
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_put_strategy_returns_404_when_strategy_not_found(test_user, authenticated_client):
    """Test PUT /strategy/{strategy_id} returns 404 when strategy not found."""
    non_existent_id = 99999
    
    response = authenticated_client.put(
        f"/strategy/{non_existent_id}",
        json={"name": "Updated Strategy"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_put_strategy_requires_authentication(client):
    """Test PUT /strategy/{strategy_id} requires authentication (returns 401 without token)."""
    response = client.put(
        "/strategy/1",
        json={"name": "Updated Strategy"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_strategy_soft_deletes_strategy_sets_deleted_at(test_user, authenticated_client):
    """Test DELETE /strategy/{strategy_id} soft deletes strategy (sets deleted_at)."""
    # Create a strategy first
    strategy = await create_strategy("Strategy To Delete", "strategy-to-delete")
    strategy_id = strategy["id"]
    
    # Verify it's not deleted
    strategy_before = await get_strategy_by_id(strategy_id)
    assert strategy_before["deleted_at"] is None
    
    # Soft delete strategy
    response = authenticated_client.delete(f"/strategy/{strategy_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    assert "soft deleted" in data["message"].lower()
    
    # Verify deleted_at is set in database
    strategy_after = await get_strategy_by_id(strategy_id)
    assert strategy_after is not None  # Record should still exist
    assert strategy_after["deleted_at"] is not None  # But deleted_at should be set
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_delete_strategy_does_not_remove_record_from_database(test_user, authenticated_client):
    """Test DELETE /strategy/{strategy_id} does not remove record from database."""
    # Create a strategy first
    strategy = await create_strategy("Strategy To Soft Delete", "strategy-to-soft-delete")
    strategy_id = strategy["id"]
    
    # Soft delete strategy
    response = authenticated_client.delete(f"/strategy/{strategy_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify record still exists in database (not physically deleted)
    strategy_after = await get_strategy_by_id(strategy_id)
    assert strategy_after is not None
    assert strategy_after["id"] == strategy_id
    assert strategy_after["name"] == "Strategy To Soft Delete"
    assert strategy_after["deleted_at"] is not None  # But marked as deleted
    
    # Verify it appears in get_all_strategies with include_deleted=True
    all_strategies = await get_all_strategies(include_deleted=True)
    strategy_ids = {s["id"] for s in all_strategies}
    assert strategy_id in strategy_ids
    
    # Verify it does NOT appear in get_all_strategies with include_deleted=False
    active_strategies = await get_all_strategies(include_deleted=False)
    active_strategy_ids = {s["id"] for s in active_strategies}
    assert strategy_id not in active_strategy_ids
    
    # Cleanup
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_delete_strategy_returns_404_when_strategy_not_found(test_user, authenticated_client):
    """Test DELETE /strategy/{strategy_id} returns 404 when strategy not found."""
    non_existent_id = 99999
    
    response = authenticated_client.delete(f"/strategy/{non_existent_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_strategy_requires_authentication(client):
    """Test DELETE /strategy/{strategy_id} requires authentication (returns 401 without token)."""
    response = client.delete("/strategy/1")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_all_endpoints_require_authentication(client):
    """Test all endpoints require authentication."""
    # Test GET /strategy
    response = client.get("/strategy")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test POST /strategy
    response = client.post("/strategy", json={"name": "Test Strategy"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test PUT /strategy/{strategy_id}
    response = client.put("/strategy/1", json={"name": "Updated Strategy"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test DELETE /strategy/{strategy_id}
    response = client.delete("/strategy/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

