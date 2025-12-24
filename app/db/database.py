import asyncpg
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


async def create_user(email: str, password_hash: str):
    """Insert a new user and return the created record"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO users (email, password)
            VALUES ($1, $2)
            RETURNING id, email, balance, created_at;
            """,
            email,
            password_hash
        )


async def get_user_by_email(email: str):
    """Fetch a user record by email"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT id, email, password, balance, created_at
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


async def close_db_pool():
    """Close database connection pool"""
    global _db_pool

    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None
