import asyncpg
from decimal import Decimal
from app.core.config import settings

# Global database pool
_db_pool = None


async def get_db_pool():
    """Get or create database connection pool"""
    global _db_pool

    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            min_size=5,
            max_size=20,
            command_timeout=60,
            max_queries=50000,
            max_inactive_connection_lifetime=300.0
        )

    return _db_pool


async def init_db():
    """Ensure required database tables exist"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                balance NUMERIC(20, 8) NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT timezone('utc', now())
            );
            """
        )
        # Backward-compatible migration: add balance to existing installs.
        await conn.execute(
            """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS balance NUMERIC(20, 8) NOT NULL DEFAULT 0;
            """
        )


async def create_user(email: str, password_hash: str, name: str):
    """Insert a new user and return the created record
    
    Args:
        email: User's email address
        password_hash: Hashed password
        name: User's full name
        
    Returns:
        asyncpg.Record with id, email, name, balance, created_at
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
<<<<<<< HEAD
            INSERT INTO users (email, password, name, balance)
            VALUES ($1, $2, $3, 0.00000000000000000000)
            RETURNING id, email, name, balance, created_at;
=======
            INSERT INTO users (email, password)
            VALUES ($1, $2)
            RETURNING id, email, balance, created_at;
>>>>>>> 8dcfcd02f02dc3c8f4bcfc10d04995fc2e46c915
            """,
            email,
            password_hash,
            name
        )


async def get_user_by_email(email: str):
    """Fetch a user record by email
    
    Returns:
        asyncpg.Record with id, email, password, name, balance, created_at
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
<<<<<<< HEAD
            SELECT id, email, password, name, balance, created_at
=======
            SELECT id, email, password, balance, created_at
>>>>>>> 8dcfcd02f02dc3c8f4bcfc10d04995fc2e46c915
            FROM users
            WHERE email = $1;
            """,
            email
        )


async def user_exists(email: str) -> bool:
    """Check whether a user already exists by email"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        result = await conn.fetchval(
            """
            SELECT 1
            FROM users
            WHERE email = $1;
            """,
            email
        )
        return result is not None


async def update_user_balance(user_id: int, amount: Decimal, operation: str) -> asyncpg.Record:
    """Update user balance atomically with add or subtract operation
    
    Args:
        user_id: User ID to update
        amount: Amount to add or subtract (must be positive)
        operation: Either "add" or "subtract"
        
    Returns:
        asyncpg.Record with id, email, name, balance, created_at, updated_at
        
    Raises:
        ValueError: If operation is not "add" or "subtract"
    """
    if operation not in ("add", "subtract"):
        raise ValueError(f"Operation must be 'add' or 'subtract', got '{operation}'")
    
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            if operation == "add":
                return await conn.fetchrow(
                    """
                    UPDATE users
                    SET balance = balance + $1,
                        updated_at = timezone('utc', now())
                    WHERE id = $2
                    RETURNING id, email, name, balance, created_at, updated_at;
                    """,
                    amount,
                    user_id
                )
            else:  # subtract
                return await conn.fetchrow(
                    """
                    UPDATE users
                    SET balance = balance - $1,
                        updated_at = timezone('utc', now())
                    WHERE id = $2
                    RETURNING id, email, name, balance, created_at, updated_at;
                    """,
                    amount,
                    user_id
                )


async def get_user_with_balance(user_id: int) -> asyncpg.Record | None:
    """Fetch a user record by ID with balance field
    
    Args:
        user_id: User ID to fetch
        
    Returns:
        asyncpg.Record with id, email, password, name, balance, created_at, updated_at
        or None if user not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT id, email, password, name, balance, created_at, updated_at
            FROM users
            WHERE id = $1;
            """,
            user_id
        )


async def close_db_pool():
    """Close database connection pool"""
    global _db_pool

    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None
