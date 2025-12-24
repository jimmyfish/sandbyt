"""Unit tests for user database functions.

Tests for task 3: Update create_user function to handle name and balance.
"""
import pytest
import pytest_asyncio
from decimal import Decimal

from app.db.database import create_user, get_user_by_email


@pytest.mark.asyncio
async def test_create_user_accepts_name_parameter():
    """Test create_user accepts name parameter and stores it correctly."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_create@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Test User Name"
    
    # Clean up any existing user first
    from app.db.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    record = await create_user(email, password_hash, name)
    
    assert record is not None
    assert record["email"] == email
    assert record["name"] == name
    assert "id" in record
    assert "created_at" in record
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_create_user_initializes_balance_to_zero():
    """Test create_user initializes balance to 0.00000000000000000000."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_balance@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Balance Test User"
    
    # Clean up any existing user first
    from app.db.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    record = await create_user(email, password_hash, name)
    
    assert record is not None
    assert "balance" in record
    assert record["balance"] == Decimal("0.00000000000000000000")
    assert isinstance(record["balance"], Decimal)
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_create_user_returns_name_and_balance_fields():
    """Test create_user returns user record with name and balance fields."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_fields@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Fields Test User"
    
    # Clean up any existing user first
    from app.db.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    record = await create_user(email, password_hash, name)
    
    assert record is not None
    assert "name" in record
    assert "balance" in record
    assert record["name"] == name
    assert record["balance"] == Decimal("0.00000000000000000000")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_create_user_balance_precision_maintained():
    """Test balance precision is maintained (DECIMAL(30,20))."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_precision@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Precision Test User"
    
    # Clean up any existing user first
    from app.db.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    record = await create_user(email, password_hash, name)
    
    assert record is not None
    balance = record["balance"]
    
    # Verify balance is Decimal with correct precision
    assert isinstance(balance, Decimal)
    assert balance == Decimal("0.00000000000000000000")
    
    # Verify we can store high precision values (test by updating)
    high_precision = Decimal("12345678901234567890.12345678901234567890")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE email = $2",
            high_precision,
            email
        )
        updated_balance = await conn.fetchval(
            "SELECT balance FROM users WHERE email = $1",
            email
        )
        assert updated_balance == high_precision
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_get_user_by_email_returns_name_and_balance():
    """Test get_user_by_email returns name and balance fields."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_get@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Get Test User"
    
    # Clean up any existing user first
    from app.db.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user first
    await create_user(email, password_hash, name)
    
    # Retrieve user
    record = await get_user_by_email(email)
    
    assert record is not None
    assert record["email"] == email
    assert "name" in record
    assert "balance" in record
    assert record["name"] == name
    assert record["balance"] == Decimal("0.00000000000000000000")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)

