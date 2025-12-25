import asyncpg
import json
import re
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
                name TEXT NOT NULL,
                balance NUMERIC(20, 8) NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
                updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
            );
            """
        )
        # Backward-compatible migration: add name, balance, and updated_at to existing installs.
        await conn.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='users' AND column_name='name') THEN
                    ALTER TABLE users ADD COLUMN name TEXT;
                    UPDATE users SET name = '' WHERE name IS NULL;
                    ALTER TABLE users ALTER COLUMN name SET NOT NULL;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='users' AND column_name='balance') THEN
                    ALTER TABLE users ADD COLUMN balance NUMERIC(20, 8) NOT NULL DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='users' AND column_name='updated_at') THEN
                    ALTER TABLE users ADD COLUMN updated_at TIMESTAMPTZ DEFAULT timezone('utc', now());
                END IF;
            END $$;
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
            INSERT INTO users (email, password, name, balance)
            VALUES ($1, $2, $3, 0.00000000000000000000)
            RETURNING id, email, name, balance, created_at;
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
            SELECT id, email, password, name, balance, created_at
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


async def create_transaction(
    user_id: int,
    symbol: str,
    buy_price: Decimal,
    quantity: Decimal
) -> asyncpg.Record:
    """Create a new transaction (order) with status=1 (active)
    
    Args:
        user_id: User ID who owns the transaction
        symbol: Trading symbol (e.g., "BTCUSDT")
        buy_price: Price at which the asset was bought
        quantity: Quantity of the asset
        
    Returns:
        asyncpg.Record with transaction fields including id, symbol, buy_price,
        sell_price, status, quantity, user_id, created_at, updated_at
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO transact (symbol, buy_price, quantity, user_id, status)
            VALUES ($1, $2, $3, $4, 1)
            RETURNING id, symbol, buy_price, sell_price, status, quantity, user_id, created_at, updated_at;
            """,
            symbol,
            buy_price,
            quantity,
            user_id
        )


async def get_active_transaction(
    user_id: int,
    symbol: str
) -> asyncpg.Record | None:
    """Find active transaction (status=1) for user and symbol
    
    Args:
        user_id: User ID to search for
        symbol: Trading symbol to search for
        
    Returns:
        asyncpg.Record with transaction fields if found, None otherwise
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT id, symbol, buy_price, sell_price, status, quantity, user_id, created_at, updated_at
            FROM transact
            WHERE user_id = $1 AND symbol = $2 AND status = 1;
            """,
            user_id,
            symbol
        )


async def create_order_atomic(
    user_id: int,
    symbol: str,
    buy_price: Decimal,
    quantity: Decimal
) -> asyncpg.Record:
    """Create a new transaction and update user balance atomically in a single database transaction
    
    This function ensures that both the transaction creation and balance update
    happen atomically - if either operation fails, both are rolled back.
    
    Args:
        user_id: User ID who owns the transaction
        symbol: Trading symbol (e.g., "BTCUSDT")
        buy_price: Price at which the asset was bought
        quantity: Quantity of the asset
        
    Returns:
        asyncpg.Record with transaction fields including id, symbol, buy_price,
        sell_price, status, quantity, user_id, created_at, updated_at
        
    Raises:
        ValueError: If user doesn't have sufficient balance
        asyncpg.exceptions.UniqueViolationError: If duplicate transaction constraint is violated
    """
    pool = await get_db_pool()
    total_cost = buy_price * quantity
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Check user balance first
            user_balance = await conn.fetchval(
                """
                SELECT balance FROM users WHERE id = $1;
                """,
                user_id
            )
            
            if user_balance is None:
                raise ValueError(f"User {user_id} not found")
            
            if Decimal(str(user_balance)) < total_cost:
                raise ValueError("Insufficient balance")
            
            # Create transaction record
            transaction = await conn.fetchrow(
                """
                INSERT INTO transact (symbol, buy_price, quantity, user_id, status)
                VALUES ($1, $2, $3, $4, 1)
                RETURNING id, symbol, buy_price, sell_price, status, quantity, user_id, created_at, updated_at;
                """,
                symbol,
                buy_price,
                quantity,
                user_id
            )
            
            # Update user balance (subtract total cost)
            await conn.execute(
                """
                UPDATE users
                SET balance = balance - $1,
                    updated_at = timezone('utc', now())
                WHERE id = $2;
                """,
                total_cost,
                user_id
            )
            
            return transaction


async def update_transaction(
    transaction_id: int,
    sell_price: Decimal,
    status: int
) -> asyncpg.Record:
    """Update transaction with sell price and status
    
    Args:
        transaction_id: Transaction ID to update
        sell_price: Price at which the asset was sold
        status: New status (typically 2 for closed)
        
    Returns:
        asyncpg.Record with updated transaction fields
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            UPDATE transact
            SET sell_price = $1,
                status = $2,
                updated_at = timezone('utc', now())
            WHERE id = $3
            RETURNING id, symbol, buy_price, sell_price, status, quantity, user_id, created_at, updated_at;
            """,
            sell_price,
            status,
            transaction_id
        )


async def close_order_atomic(
    user_id: int,
    symbol: str,
    sell_price: Decimal
) -> asyncpg.Record:
    """Close an active order and update user balance atomically in a single database transaction
    
    This function ensures that both the transaction update and balance update
    happen atomically - if either operation fails, both are rolled back.
    
    Args:
        user_id: User ID who owns the transaction
        symbol: Trading symbol (e.g., "BTCUSDT")
        sell_price: Price at which the asset is being sold
        
    Returns:
        asyncpg.Record with updated transaction fields including id, symbol, buy_price,
        sell_price, status, quantity, user_id, created_at, updated_at
        
    Raises:
        ValueError: If no active transaction is found for the user and symbol
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Find active transaction
            transaction = await conn.fetchrow(
                """
                SELECT id, symbol, buy_price, sell_price, status, quantity, user_id, created_at, updated_at
                FROM transact
                WHERE user_id = $1 AND symbol = $2 AND status = 1;
                """,
                user_id,
                symbol
            )
            
            if transaction is None:
                raise ValueError(f"No active order found for symbol {symbol}")
            
            quantity = Decimal(str(transaction["quantity"]))
            total_proceeds = sell_price * quantity
            
            # Update transaction with sell price and status=2 (closed)
            updated_transaction = await conn.fetchrow(
                """
                UPDATE transact
                SET sell_price = $1,
                    status = 2,
                    updated_at = timezone('utc', now())
                WHERE id = $2
                RETURNING id, symbol, buy_price, sell_price, status, quantity, user_id, created_at, updated_at;
                """,
                sell_price,
                transaction["id"]
            )
            
            # Update user balance (add total proceeds)
            await conn.execute(
                """
                UPDATE users
                SET balance = balance + $1,
                    updated_at = timezone('utc', now())
                WHERE id = $2;
                """,
                total_proceeds,
                user_id
            )
            
            return updated_transaction


async def get_user_transactions(
    user_id: int,
    active_only: bool = False,
    symbol: str | None = None
) -> list[asyncpg.Record]:
    """Fetch user transactions with optional filtering and computed fields
    
    Args:
        user_id: User ID to fetch transactions for
        active_only: If True, only return transactions with status=1
        symbol: If provided, filter by symbol
        
    Returns:
        List of asyncpg.Record objects with transaction fields plus computed fields:
        - diff: sell_price - buy_price (or NULL if sell_price is NULL)
        - buyAggregate: buy_price * quantity
        - sellAggregate: sell_price * quantity (or NULL if sell_price is NULL)
        - diffDollar: equity if status=2, else 0
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Build query with conditional WHERE clauses
        base_query = """
            SELECT 
                id,
                symbol,
                buy_price,
                sell_price,
                status,
                quantity,
                user_id,
                created_at,
                updated_at,
                -- Computed fields
                (sell_price - buy_price) AS diff,
                (buy_price * quantity) AS "buyAggregate",
                (sell_price * quantity) AS "sellAggregate",
                CASE 
                    WHEN status = 2 AND sell_price IS NOT NULL THEN (sell_price - buy_price) * quantity
                    ELSE 0
                END AS "diffDollar"
            FROM transact
            WHERE user_id = $1
        """
        
        params = [user_id]
        param_index = 2
        
        if active_only:
            base_query += f" AND status = ${param_index}"
            params.append(1)
            param_index += 1
        
        if symbol:
            base_query += f" AND symbol = ${param_index}"
            params.append(symbol)
            param_index += 1
        
        base_query += " ORDER BY status ASC, created_at DESC;"
        
        return await conn.fetch(base_query, *params)


async def create_watchlist(symbol: str) -> asyncpg.Record:
    """Create a new watchlist entry
    
    Args:
        symbol: Trading symbol to add to watchlist (e.g., "BTCUSDT")
        
    Returns:
        asyncpg.Record with id, symbol, created_at
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO watchlists (symbol)
            VALUES ($1)
            RETURNING id, symbol, created_at;
            """,
            symbol
        )


async def get_watchlists() -> list[asyncpg.Record]:
    """Get all watchlist entries
    
    Returns:
        List of asyncpg.Record objects with id, symbol, created_at
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT id, symbol, created_at
            FROM watchlists
            ORDER BY created_at DESC;
            """
        )


async def delete_watchlist(symbol: str) -> bool:
    """Delete a watchlist entry by symbol
    
    Args:
        symbol: Trading symbol to remove from watchlist
        
    Returns:
        True if deletion succeeded, False if symbol not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Check if watchlist exists first
        exists = await conn.fetchval(
            """
            SELECT 1
            FROM watchlists
            WHERE symbol = $1;
            """,
            symbol
        )
        
        if exists is None:
            return False
        
        # Delete the watchlist
        await conn.execute(
            """
            DELETE FROM watchlists
            WHERE symbol = $1;
            """,
            symbol
        )
        
        return True


async def create_log(symbol: str, data: dict, action: str) -> asyncpg.Record:
    """Create a new log entry with JSON data storage
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSDT")
        data: Dictionary data to store as JSON text
        action: Action description (e.g., "buy", "sell", "analysis")
        
    Returns:
        asyncpg.Record with id, symbol, data (as JSON text), action, created_at, updated_at
    """
    pool = await get_db_pool()
    
    # Serialize data dict to JSON text
    data_json = json.dumps(data)
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO log (symbol, data, action)
            VALUES ($1, $2, $3)
            RETURNING id, symbol, data, action, created_at, updated_at;
            """,
            symbol,
            data_json,
            action
        )


async def get_logs(
    symbol: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> tuple[list[asyncpg.Record], int]:
    """Fetch logs with optional symbol filtering and pagination
    
    Args:
        symbol: If provided, filter by symbol using LIKE search (e.g., "BTC%" matches "BTCUSDT")
        limit: Maximum number of records to return (default: 100)
        offset: Number of records to skip for pagination (default: 0)
        
    Returns:
        Tuple of (list of asyncpg.Record objects, total_count):
        - Records contain id, symbol, data (as JSON text), action, created_at, updated_at
        - total_count is the total number of matching records (for pagination)
        - Results are ordered by created_at DESC
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Build WHERE clause for symbol filtering
        where_clause = ""
        params = []
        param_index = 1
        
        if symbol:
            where_clause = "WHERE symbol LIKE $1"
            params.append(f"%{symbol}%")
            param_index = 2  # Next parameter index after symbol
        
        # Get total count for pagination
        count_query = f"SELECT COUNT(*) FROM log {where_clause};"
        total_count = await conn.fetchval(count_query, *params)
        
        # Build main query with pagination
        query = f"""
            SELECT id, symbol, data, action, created_at, updated_at
            FROM log
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_index} OFFSET ${param_index + 1};
        """
        params.extend([limit, offset])
        
        records = await conn.fetch(query, *params)
        
        return records, total_count


async def get_unique_log_symbols() -> list[str]:
    """Get list of unique symbols from log entries
    
    Returns:
        List of unique symbol strings, sorted alphabetically
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        records = await conn.fetch(
            """
            SELECT DISTINCT symbol
            FROM log
            ORDER BY symbol ASC;
            """
        )
        
        return [record["symbol"] for record in records]


def _slugify(name: str) -> str:
    """Convert a name string to a URL-friendly slug
    
    Args:
        name: String to convert to slug
        
    Returns:
        Slugified string (lowercase, spaces to hyphens, special chars removed)
    """
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove all non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    # Replace multiple consecutive hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    return slug


async def create_strategy(name: str, slug: str | None = None) -> asyncpg.Record:
    """Create a new strategy with name and slug
    
    Args:
        name: Strategy name (required)
        slug: Strategy slug (optional, auto-generated from name if not provided)
        
    Returns:
        asyncpg.Record with id, name, slug, deleted_at, created_at, updated_at
    """
    # Auto-generate slug from name if not provided
    if slug is None:
        slug = _slugify(name)
    
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO strategies (name, slug)
            VALUES ($1, $2)
            RETURNING id, name, slug, deleted_at, created_at, updated_at;
            """,
            name,
            slug
        )


async def get_all_strategies(include_deleted: bool = True) -> list[asyncpg.Record]:
    """Get all strategies, optionally including soft-deleted ones
    
    Args:
        include_deleted: If True, include strategies with deleted_at set (default: True)
        
    Returns:
        List of asyncpg.Record objects with id, name, slug, deleted_at, created_at, updated_at
        Ordered by created_at DESC
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        if include_deleted:
            return await conn.fetch(
                """
                SELECT id, name, slug, deleted_at, created_at, updated_at
                FROM strategies
                ORDER BY created_at DESC;
                """
            )
        else:
            return await conn.fetch(
                """
                SELECT id, name, slug, deleted_at, created_at, updated_at
                FROM strategies
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC;
                """
            )


async def get_strategy_by_id(strategy_id: int) -> asyncpg.Record | None:
    """Fetch a strategy by ID
    
    Args:
        strategy_id: Strategy ID to fetch
        
    Returns:
        asyncpg.Record with id, name, slug, deleted_at, created_at, updated_at
        or None if not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT id, name, slug, deleted_at, created_at, updated_at
            FROM strategies
            WHERE id = $1;
            """,
            strategy_id
        )


async def update_strategy(
    strategy_id: int,
    name: str | None = None,
    slug: str | None = None
) -> asyncpg.Record:
    """Update strategy name and/or slug
    
    Args:
        strategy_id: Strategy ID to update
        name: New name (optional)
        slug: New slug (optional, auto-generated from name if name provided and slug not provided)
        
    Returns:
        asyncpg.Record with updated strategy fields
        
    Raises:
        ValueError: If strategy not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Build dynamic UPDATE query based on provided fields
        updates = []
        params = []
        param_index = 1
        
        if name is not None:
            updates.append(f"name = ${param_index}")
            params.append(name)
            param_index += 1
            
            # Auto-generate slug from name if slug not explicitly provided
            if slug is None:
                slug = _slugify(name)
        
        if slug is not None:
            updates.append(f"slug = ${param_index}")
            params.append(slug)
            param_index += 1
        
        if not updates:
            # No fields to update, just fetch and return
            return await get_strategy_by_id(strategy_id)
        
        # Add updated_at
        updates.append("updated_at = timezone('utc', now())")
        
        # Add strategy_id parameter
        params.append(strategy_id)
        
        query = f"""
            UPDATE strategies
            SET {', '.join(updates)}
            WHERE id = ${param_index}
            RETURNING id, name, slug, deleted_at, created_at, updated_at;
        """
        
        result = await conn.fetchrow(query, *params)
        
        if result is None:
            raise ValueError(f"Strategy with id {strategy_id} not found")
        
        return result


async def soft_delete_strategy(strategy_id: int) -> asyncpg.Record:
    """Soft delete a strategy by setting deleted_at timestamp
    
    Args:
        strategy_id: Strategy ID to soft delete
        
    Returns:
        asyncpg.Record with updated strategy fields (deleted_at will be set)
        
    Raises:
        ValueError: If strategy not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """
            UPDATE strategies
            SET deleted_at = timezone('utc', now()),
                updated_at = timezone('utc', now())
            WHERE id = $1
            RETURNING id, name, slug, deleted_at, created_at, updated_at;
            """,
            strategy_id
        )
        
        if result is None:
            raise ValueError(f"Strategy with id {strategy_id} not found")
        
        return result


async def create_trade_strategy(
    symbol: str,
    strategy_id: int,
    timestamp: str = "5m"
) -> asyncpg.Record:
    """Create a new trade strategy mapping with symbol, strategy_id, and timestamp
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSDT", max 15 chars)
        strategy_id: Strategy ID (must exist in strategies table)
        timestamp: Time interval (default: "5m")
        
    Returns:
        asyncpg.Record with id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
        
    Raises:
        asyncpg.ForeignKeyViolationError: If strategy_id does not exist
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO trade_strategies (symbol, strategy_id, timestamp)
            VALUES ($1, $2, $3)
            RETURNING id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at;
            """,
            symbol,
            strategy_id,
            timestamp
        )


async def get_trade_strategies(include_deleted: bool = True) -> list[asyncpg.Record]:
    """Get all trade strategies, optionally including soft-deleted ones
    
    Args:
        include_deleted: If True, include trade strategies with deleted_at set (default: True)
        
    Returns:
        List of asyncpg.Record objects with id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
        Ordered by created_at DESC
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        if include_deleted:
            return await conn.fetch(
                """
                SELECT id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
                FROM trade_strategies
                ORDER BY created_at DESC;
                """
            )
        else:
            return await conn.fetch(
                """
                SELECT id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
                FROM trade_strategies
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC;
                """
            )


async def get_trade_strategy_by_id(trade_strategy_id: int) -> asyncpg.Record | None:
    """Fetch a trade strategy by ID
    
    Args:
        trade_strategy_id: Trade strategy ID to fetch
        
    Returns:
        asyncpg.Record with id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
        or None if not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
            FROM trade_strategies
            WHERE id = $1;
            """,
            trade_strategy_id
        )


async def update_trade_strategy(
    trade_strategy_id: int,
    symbol: str | None = None,
    strategy_id: int | None = None,
    timestamp: str | None = None
) -> asyncpg.Record:
    """Update trade strategy symbol, strategy_id, and/or timestamp
    
    Args:
        trade_strategy_id: Trade strategy ID to update
        symbol: New symbol (optional)
        strategy_id: New strategy_id (optional, must exist in strategies table)
        timestamp: New timestamp (optional)
        
    Returns:
        asyncpg.Record with updated trade strategy fields
        
    Raises:
        ValueError: If trade strategy not found
        asyncpg.ForeignKeyViolationError: If strategy_id does not exist
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Build dynamic UPDATE query based on provided fields
        updates = []
        params = []
        param_index = 1
        
        if symbol is not None:
            updates.append(f"symbol = ${param_index}")
            params.append(symbol)
            param_index += 1
        
        if strategy_id is not None:
            updates.append(f"strategy_id = ${param_index}")
            params.append(strategy_id)
            param_index += 1
        
        if timestamp is not None:
            updates.append(f"timestamp = ${param_index}")
            params.append(timestamp)
            param_index += 1
        
        if not updates:
            # No fields to update, just fetch and return
            return await get_trade_strategy_by_id(trade_strategy_id)
        
        # Add updated_at
        updates.append("updated_at = timezone('utc', now())")
        
        # Add trade_strategy_id parameter
        params.append(trade_strategy_id)
        
        query = f"""
            UPDATE trade_strategies
            SET {', '.join(updates)}
            WHERE id = ${param_index}
            RETURNING id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at;
        """
        
        result = await conn.fetchrow(query, *params)
        
        if result is None:
            raise ValueError(f"Trade strategy with id {trade_strategy_id} not found")
        
        return result


async def soft_delete_trade_strategy(trade_strategy_id: int) -> asyncpg.Record:
    """Soft delete a trade strategy by setting deleted_at timestamp
    
    Args:
        trade_strategy_id: Trade strategy ID to soft delete
        
    Returns:
        asyncpg.Record with updated trade strategy fields (deleted_at will be set)
        
    Raises:
        ValueError: If trade strategy not found
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """
            UPDATE trade_strategies
            SET deleted_at = timezone('utc', now()),
                updated_at = timezone('utc', now())
            WHERE id = $1
            RETURNING id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at;
            """,
            trade_strategy_id
        )
        
        if result is None:
            raise ValueError(f"Trade strategy with id {trade_strategy_id} not found")
        
        return result


def records_to_dataframe(records: list[asyncpg.Record]):
    """Convert a list of asyncpg.Record objects to a pandas DataFrame.
    
    This function handles type conversions for common database types:
    - datetime fields are preserved as datetime64
    - Decimal fields are converted to float
    - NULL values are preserved as NaN
    
    Args:
        records: List of asyncpg.Record objects from database queries
        
    Returns:
        pandas.DataFrame with columns matching the record fields
        
    Raises:
        ImportError: If pandas is not installed (optional dependency)
        
    Example:
        >>> records = await get_user_transactions(user_id=1)
        >>> df = records_to_dataframe(records)
        >>> print(df.head())
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame conversion. "
            "Install it with: pip install pandas"
        )
    
    if not records:
        return pd.DataFrame()
    
    # Convert records to list of dictionaries
    data = []
    for record in records:
        row = {}
        for key in record.keys():
            value = record[key]
            
            # Convert Decimal to float
            if isinstance(value, Decimal):
                row[key] = float(value) if value is not None else None
            # Keep datetime as-is (pandas handles it well)
            elif value is None:
                row[key] = None
            else:
                row[key] = value
        
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df


async def query_to_dataframe(query: str, *args):
    """Execute a SQL query and return results as a pandas DataFrame.
    
    This function executes a query using the database connection pool and
    converts the results to a DataFrame using records_to_dataframe().
    
    Args:
        query: SQL query string (supports parameterized queries with $1, $2, etc.)
        *args: Query parameters to bind to the query
        
    Returns:
        pandas.DataFrame with query results
        
    Raises:
        ImportError: If pandas is not installed (optional dependency)
        
    Example:
        >>> df = await query_to_dataframe(
        ...     "SELECT * FROM transact WHERE user_id = $1",
        ...     1
        ... )
        >>> print(df.head())
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        records = await conn.fetch(query, *args)
        return records_to_dataframe(records)


async def close_db_pool():
    """Close database connection pool"""
    global _db_pool

    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None
