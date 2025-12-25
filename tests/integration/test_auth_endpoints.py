"""Integration tests for auth endpoints.

Tests for task 28: Update auth router to handle name field in user registration.
Tests for task 29: Update auth router profile endpoint to return name and balance.
"""
import pytest
import pytest_asyncio
from decimal import Decimal
from fastapi import status
from fastapi.testclient import TestClient

from app.db.database import get_user_by_email, get_db_pool
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client for endpoint testing."""
    return TestClient(app)


@pytest_asyncio.fixture(loop_scope="session")
async def cleanup_emails():
    """Fixture to track emails for cleanup after test execution."""
    emails = []
    yield emails
    
    # Cleanup after test
    if emails:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            for email in emails:
                await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio(loop_scope="session")
async def test_post_auth_register_accepts_name_field_in_request(async_client, cleanup_emails):
    """Test POST /auth/register accepts name field in request."""
    email = "test_name_field@example.com"
    cleanup_emails.append(email)
    
    # Register user with name field
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": "Test User Name"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_post_auth_register_stores_name_in_database(async_client, cleanup_emails):
    """Test POST /auth/register stores name in database."""
    email = "test_store_name@example.com"
    name = "Stored Name Test User"
    cleanup_emails.append(email)
    
    # Register user with name field
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify name is stored in database (async operation)
    user_record = await get_user_by_email(email)
    assert user_record is not None
    assert user_record["name"] == name


@pytest.mark.asyncio(loop_scope="session")
async def test_post_auth_register_returns_name_in_response(async_client, cleanup_emails):
    """Test POST /auth/register returns name in response."""
    email = "test_return_name@example.com"
    name = "Return Name Test User"
    cleanup_emails.append(email)
    
    # Register user with name field
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    
    user_data = data["data"]
    assert "name" in user_data
    assert user_data["name"] == name


@pytest.mark.asyncio(loop_scope="session")
async def test_post_auth_register_returns_422_when_name_is_missing(async_client, cleanup_emails):
    """Test POST /auth/register returns 422 when name is missing."""
    email = "test_missing_name@example.com"
    cleanup_emails.append(email)
    
    # Try to register user without name field
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123"
            # name field is missing
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_post_auth_register_returns_422_when_name_is_missing_verifies_no_user_created(async_client, cleanup_emails):
    """Test POST /auth/register returns 422 when name is missing and verifies user was not created."""
    email = "test_missing_name_verify@example.com"
    cleanup_emails.append(email)
    
    # Try to register user without name field
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123"
            # name field is missing
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify user was not created (async operation)
    user_record = await get_user_by_email(email)
    assert user_record is None


@pytest.mark.asyncio(loop_scope="session")
async def test_post_auth_register_initializes_balance_to_0(async_client, cleanup_emails):
    """Test POST /auth/register initializes balance to 0."""
    email = "test_balance_init@example.com"
    name = "Balance Init Test User"
    cleanup_emails.append(email)
    
    # Register user
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verify balance is initialized to 0 in database (async operation)
    user_record = await get_user_by_email(email)
    assert user_record is not None
    assert user_record["balance"] == Decimal("0.00000000000000000000")
    
    # Verify balance is returned as "0" in response
    data = response.json()
    user_data = data["data"]
    assert "balance" in user_data
    assert user_data["balance"] == "0.00000000000000000000"


# Task 29: Tests for GET /auth/profile returning name and balance fields

@pytest.mark.asyncio(loop_scope="session")
async def test_get_auth_profile_returns_name_field(async_client, cleanup_emails):
    """Test GET /auth/profile returns name field."""
    email = "test_profile_name@example.com"
    name = "Profile Name Test User"
    cleanup_emails.append(email)
    
    # Register user
    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # Login to get token
    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()
    access_token = login_data["data"]["access_token"]
    
    # Get profile with token
    profile_response = await async_client.get(
        "/auth/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert profile_response.status_code == status.HTTP_200_OK
    profile_data = profile_response.json()
    assert profile_data["status"] == "success"
    assert "data" in profile_data
    
    user_data = profile_data["data"]
    assert "name" in user_data
    assert user_data["name"] == name


@pytest.mark.asyncio(loop_scope="session")
async def test_get_auth_profile_returns_balance_field(async_client, cleanup_emails):
    """Test GET /auth/profile returns balance field."""
    email = "test_profile_balance@example.com"
    name = "Profile Balance Test User"
    cleanup_emails.append(email)
    
    # Register user
    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # Login to get token
    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()
    access_token = login_data["data"]["access_token"]
    
    # Get profile with token
    profile_response = await async_client.get(
        "/auth/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert profile_response.status_code == status.HTTP_200_OK
    profile_data = profile_response.json()
    assert profile_data["status"] == "success"
    assert "data" in profile_data
    
    user_data = profile_data["data"]
    assert "balance" in user_data
    # Balance should be returned as string (as per UserResponse schema)
    assert isinstance(user_data["balance"], str)
    assert user_data["balance"] == "0.00000000000000000000"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_auth_profile_balance_field_is_decimal_type_in_database(async_client, cleanup_emails):
    """Test balance field is returned as Decimal type from database (serialized as string in response)."""
    email = "test_profile_decimal@example.com"
    name = "Profile Decimal Test User"
    cleanup_emails.append(email)
    
    # Register user
    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "testpassword123",
            "name": name
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # Update balance in database to a non-zero value (async database operation)
    test_balance = Decimal("123.45678901234567890")
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE email = $2",
            test_balance,
            email
        )
    
    # Login to get token
    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()
    access_token = login_data["data"]["access_token"]
    
    # Get profile with token
    profile_response = await async_client.get(
        "/auth/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert profile_response.status_code == status.HTTP_200_OK
    profile_data = profile_response.json()
    assert profile_data["status"] == "success"
    assert "data" in profile_data
    
    user_data = profile_data["data"]
    assert "balance" in user_data
    
    # Verify balance is returned as string (as per UserResponse schema)
    assert isinstance(user_data["balance"], str)
    
    # Verify the balance value matches what we set (as string with 20 decimal places)
    assert user_data["balance"] == "123.45678901234567890000"
    
    # Verify in database that it's stored as Decimal (async database operation)
    user_record = await get_user_by_email(email)
    assert user_record is not None
    assert isinstance(user_record["balance"], Decimal)
    assert user_record["balance"] == test_balance
