"""Unit tests for user database functions.

Tests for task 3: Update create_user function to handle name and balance.
Tests for task 27: Update get_user_by_email to return name and balance fields.
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


# Task 27: Tests for get_user_by_email returning name and balance fields

@pytest.mark.asyncio
async def test_get_user_by_email_returns_name_field():
    """Test get_user_by_email returns name field."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_name_field@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Name Field Test User"
    
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
    assert "name" in record
    assert record["name"] == name
    assert isinstance(record["name"], str)
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_get_user_by_email_returns_balance_field():
    """Test get_user_by_email returns balance field."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_balance_field@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Balance Field Test User"
    
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
    assert "balance" in record
    assert record["balance"] == Decimal("0.00000000000000000000")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_get_user_by_email_balance_field_is_decimal_type():
    """Test balance field is returned as Decimal type."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_decimal_type@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Decimal Type Test User"
    
    # Clean up any existing user first
    from app.db.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user first
    await create_user(email, password_hash, name)
    
    # Update balance to a non-zero value
    test_balance = Decimal("123.45678901234567890")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE email = $2",
            test_balance,
            email
        )
    
    # Retrieve user
    record = await get_user_by_email(email)
    
    assert record is not None
    assert "balance" in record
    assert isinstance(record["balance"], Decimal)
    assert record["balance"] == test_balance
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_get_user_by_email_maintains_backward_compatibility():
    """Test get_user_by_email maintains backward compatibility with existing code.
    
    This test ensures that existing code that uses get_user_by_email still works
    correctly. The function should return all expected fields including id, email,
    password, name, balance, and created_at.
    """
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_backward_compat@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Backward Compat Test User"
    
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
    
    # Verify all expected fields are present (backward compatibility)
    assert "id" in record
    assert "email" in record
    assert "password" in record
    assert "name" in record
    assert "balance" in record
    assert "created_at" in record
    
    # Verify field values match what was created
    assert record["email"] == email
    assert record["name"] == name
    assert record["password"] == password_hash  # Should match the hash
    assert isinstance(record["id"], int)
    assert isinstance(record["balance"], Decimal)
    
    # Verify existing code patterns still work
    # Pattern 1: Accessing email and password (used in auth router)
    assert record["email"] is not None
    assert record["password"] is not None
    
    # Pattern 2: Accessing name with .get() fallback (used in auth router)
    name_value = record.get("name", "")
    assert name_value == name
    
    # Pattern 3: Accessing balance (used in auth router)
    balance_value = record["balance"]
    assert isinstance(balance_value, Decimal)
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)

