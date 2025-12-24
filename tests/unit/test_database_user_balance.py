"""Unit tests for user balance management database functions.

Tests for task 7: Implement user balance management database functions.
"""
import pytest
import pytest_asyncio
from decimal import Decimal

from app.db.database import (
    update_user_balance,
    get_user_with_balance,
    create_user,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_update_user_balance_adds_amount_correctly():
    """Test update_user_balance adds amount correctly."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_add@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Add Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user with initial balance
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    initial_balance = user_record["balance"]
    
    # Add amount
    amount = Decimal("100.50")
    updated_user = await update_user_balance(user_id, amount, "add")
    
    assert updated_user is not None
    assert updated_user["balance"] == initial_balance + amount
    assert updated_user["balance"] == Decimal("100.50")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_update_user_balance_subtracts_amount_correctly():
    """Test update_user_balance subtracts amount correctly."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_subtract@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Subtract Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user and set initial balance
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Set initial balance to 1000
    initial_balance = Decimal("1000.00")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE id = $2",
            initial_balance,
            user_id
        )
    
    # Subtract amount
    amount = Decimal("250.75")
    updated_user = await update_user_balance(user_id, amount, "subtract")
    
    assert updated_user is not None
    assert updated_user["balance"] == initial_balance - amount
    assert updated_user["balance"] == Decimal("749.25")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_update_user_balance_maintains_decimal_precision():
    """Test update_user_balance maintains DECIMAL(30,20) precision."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_precision@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Precision Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Add high precision amount
    high_precision_amount = Decimal("12345678901234567890.12345678901234567890")
    updated_user = await update_user_balance(user_id, high_precision_amount, "add")
    
    assert updated_user is not None
    assert isinstance(updated_user["balance"], Decimal)
    assert updated_user["balance"] == high_precision_amount
    
    # Verify precision is maintained through another operation
    subtract_amount = Decimal("10000000000000000000.00000000000000000000")
    final_user = await update_user_balance(user_id, subtract_amount, "subtract")
    
    expected_balance = high_precision_amount - subtract_amount
    assert final_user["balance"] == expected_balance
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_update_user_balance_returns_updated_user_record():
    """Test update_user_balance returns updated user record."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_return@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Return Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Update balance
    amount = Decimal("500.00")
    updated_user = await update_user_balance(user_id, amount, "add")
    
    assert updated_user is not None
    assert updated_user["id"] == user_id
    assert updated_user["email"] == email
    assert updated_user["name"] == name
    assert "balance" in updated_user
    assert "created_at" in updated_user
    assert "updated_at" in updated_user
    assert updated_user["balance"] == Decimal("500.00")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_get_user_with_balance_retrieves_user_with_balance_field():
    """Test get_user_with_balance retrieves user with balance field."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_get_balance@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Get Balance Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Set balance
    test_balance = Decimal("1234.56")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE id = $2",
            test_balance,
            user_id
        )
    
    # Retrieve user with balance
    retrieved_user = await get_user_with_balance(user_id)
    
    assert retrieved_user is not None
    assert retrieved_user["id"] == user_id
    assert retrieved_user["email"] == email
    assert retrieved_user["name"] == name
    assert "balance" in retrieved_user
    assert retrieved_user["balance"] == test_balance
    assert isinstance(retrieved_user["balance"], Decimal)
    assert "created_at" in retrieved_user
    assert "updated_at" in retrieved_user
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_get_user_with_balance_returns_none_when_not_found():
    """Test get_user_with_balance returns None when user not found."""
    # Try to get non-existent user
    retrieved_user = await get_user_with_balance(999999)
    
    assert retrieved_user is None


@pytest.mark.asyncio
async def test_balance_operations_are_atomic():
    """Test balance operations are atomic (transaction safety)."""
    from passlib.context import CryptContext
    import asyncio
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_atomic@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Atomic Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user with initial balance
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Set initial balance
    initial_balance = Decimal("1000.00")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET balance = $1 WHERE id = $2",
            initial_balance,
            user_id
        )
    
    # Perform multiple concurrent operations
    async def add_amount(amount: Decimal):
        return await update_user_balance(user_id, amount, "add")
    
    async def subtract_amount(amount: Decimal):
        return await update_user_balance(user_id, amount, "subtract")
    
    # Run concurrent operations
    results = await asyncio.gather(
        add_amount(Decimal("100.00")),
        add_amount(Decimal("200.00")),
        subtract_amount(Decimal("50.00")),
        add_amount(Decimal("300.00")),
    )
    
    # Verify final balance
    final_user = await get_user_with_balance(user_id)
    expected_balance = initial_balance + Decimal("100.00") + Decimal("200.00") - Decimal("50.00") + Decimal("300.00")
    
    assert final_user is not None
    assert final_user["balance"] == expected_balance
    assert final_user["balance"] == Decimal("1550.00")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)


@pytest.mark.asyncio
async def test_update_user_balance_invalid_operation_raises_error():
    """Test update_user_balance raises ValueError for invalid operation."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_invalid@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Invalid Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Try invalid operation
    with pytest.raises(ValueError, match="Operation must be 'add' or 'subtract'"):
        await update_user_balance(user_id, Decimal("100.00"), "multiply")
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)

