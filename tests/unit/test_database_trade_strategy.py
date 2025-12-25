"""Unit tests for trade_strategy database functions.

Tests for task 12: Implement trade_strategy database functions.
"""
import pytest
import pytest_asyncio
import asyncpg

from app.db.database import (
    create_trade_strategy,
    get_trade_strategies,
    get_trade_strategy_by_id,
    update_trade_strategy,
    soft_delete_trade_strategy,
    create_strategy,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_create_trade_strategy_creates_record_with_symbol_strategy_id_timestamp():
    """Test create_trade_strategy creates record with symbol, strategy_id, timestamp."""
    # First create a strategy to reference
    strategy_name = "Test Strategy"
    strategy_slug = "test-strategy"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", strategy_slug)
    
    strategy = await create_strategy(strategy_name, strategy_slug)
    strategy_id = strategy["id"]
    
    # Clean up any existing trade_strategy first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", "BTCUSDT", strategy_id)
    
    # Create trade_strategy
    record = await create_trade_strategy("BTCUSDT", strategy_id, "15m")
    
    assert record is not None
    assert record["symbol"] == "BTCUSDT"
    assert record["strategy_id"] == strategy_id
    assert record["timestamp"] == "15m"
    assert "id" in record
    assert "created_at" in record
    assert "updated_at" in record
    assert record["deleted_at"] is None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", record["id"])
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_create_trade_strategy_defaults_timestamp_to_5m_if_not_provided():
    """Test create_trade_strategy defaults timestamp to '5m' if not provided."""
    # First create a strategy to reference
    strategy_name = "Test Strategy 2"
    strategy_slug = "test-strategy-2"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", strategy_slug)
    
    strategy = await create_strategy(strategy_name, strategy_slug)
    strategy_id = strategy["id"]
    
    # Clean up any existing trade_strategy first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", "ETHUSDT", strategy_id)
    
    # Create trade_strategy without timestamp (should default to '5m')
    record = await create_trade_strategy("ETHUSDT", strategy_id)
    
    assert record is not None
    assert record["symbol"] == "ETHUSDT"
    assert record["strategy_id"] == strategy_id
    assert record["timestamp"] == "5m"  # Default value
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", record["id"])
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_get_trade_strategies_returns_all_trade_strategies_including_soft_deleted_when_include_deleted_true():
    """Test get_trade_strategies returns all trade strategies including soft-deleted when include_deleted=True."""
    # First create strategies to reference
    strategy_name1 = "Strategy 1"
    strategy_slug1 = "strategy-1"
    strategy_name2 = "Strategy 2"
    strategy_slug2 = "strategy-2"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", strategy_slug1, strategy_slug2)
    
    strategy1 = await create_strategy(strategy_name1, strategy_slug1)
    strategy2 = await create_strategy(strategy_name2, strategy_slug2)
    strategy_id1 = strategy1["id"]
    strategy_id2 = strategy2["id"]
    
    # Clean up any existing trade_strategies first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol IN ($1, $2)", "BTCUSDT", "ETHUSDT")
    
    # Create two trade_strategies
    record1 = await create_trade_strategy("BTCUSDT", strategy_id1, "5m")
    record2 = await create_trade_strategy("ETHUSDT", strategy_id2, "15m")
    
    # Soft delete one trade_strategy
    await soft_delete_trade_strategy(record2["id"])
    
    # Get all trade_strategies including deleted
    trade_strategies = await get_trade_strategies(include_deleted=True)
    
    # Should contain both trade_strategies
    trade_strategy_ids = {ts["id"] for ts in trade_strategies}
    assert record1["id"] in trade_strategy_ids
    assert record2["id"] in trade_strategy_ids
    
    # Find the soft-deleted trade_strategy
    deleted_trade_strategy = next(ts for ts in trade_strategies if ts["id"] == record2["id"])
    assert deleted_trade_strategy["deleted_at"] is not None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id IN ($1, $2)", record1["id"], record2["id"])
        await conn.execute("DELETE FROM strategies WHERE id IN ($1, $2)", strategy_id1, strategy_id2)


@pytest.mark.asyncio
async def test_get_trade_strategies_excludes_soft_deleted_when_include_deleted_false():
    """Test get_trade_strategies excludes soft-deleted when include_deleted=False."""
    # First create strategies to reference
    strategy_name1 = "Strategy 3"
    strategy_slug1 = "strategy-3"
    strategy_name2 = "Strategy 4"
    strategy_slug2 = "strategy-4"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", strategy_slug1, strategy_slug2)
    
    strategy1 = await create_strategy(strategy_name1, strategy_slug1)
    strategy2 = await create_strategy(strategy_name2, strategy_slug2)
    strategy_id1 = strategy1["id"]
    strategy_id2 = strategy2["id"]
    
    # Clean up any existing trade_strategies first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol IN ($1, $2)", "BTCUSDT", "ETHUSDT")
    
    # Create two trade_strategies
    record1 = await create_trade_strategy("BTCUSDT", strategy_id1, "5m")
    record2 = await create_trade_strategy("ETHUSDT", strategy_id2, "15m")
    
    # Soft delete one trade_strategy
    await soft_delete_trade_strategy(record2["id"])
    
    # Get all trade_strategies excluding deleted
    trade_strategies = await get_trade_strategies(include_deleted=False)
    
    # Should contain only non-deleted trade_strategy
    trade_strategy_ids = {ts["id"] for ts in trade_strategies}
    assert record1["id"] in trade_strategy_ids
    assert record2["id"] not in trade_strategy_ids
    
    # Verify all returned trade_strategies are not deleted
    for trade_strategy in trade_strategies:
        assert trade_strategy["deleted_at"] is None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id IN ($1, $2)", record1["id"], record2["id"])
        await conn.execute("DELETE FROM strategies WHERE id IN ($1, $2)", strategy_id1, strategy_id2)


@pytest.mark.asyncio
async def test_get_trade_strategy_by_id_retrieves_trade_strategy_by_id():
    """Test get_trade_strategy_by_id retrieves trade strategy by ID."""
    # First create a strategy to reference
    strategy_name = "Test Strategy 3"
    strategy_slug = "test-strategy-3"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", strategy_slug)
    
    strategy = await create_strategy(strategy_name, strategy_slug)
    strategy_id = strategy["id"]
    
    # Clean up any existing trade_strategy first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", "BTCUSDT", strategy_id)
    
    # Create trade_strategy
    created_record = await create_trade_strategy("BTCUSDT", strategy_id, "5m")
    trade_strategy_id = created_record["id"]
    
    # Retrieve by ID
    retrieved_record = await get_trade_strategy_by_id(trade_strategy_id)
    
    assert retrieved_record is not None
    assert retrieved_record["id"] == trade_strategy_id
    assert retrieved_record["symbol"] == "BTCUSDT"
    assert retrieved_record["strategy_id"] == strategy_id
    assert retrieved_record["timestamp"] == "5m"
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_get_trade_strategy_by_id_returns_none_when_not_found():
    """Test get_trade_strategy_by_id returns None when not found."""
    non_existent_id = 999999
    
    # Try to retrieve non-existent trade_strategy
    result = await get_trade_strategy_by_id(non_existent_id)
    
    assert result is None


@pytest.mark.asyncio
async def test_update_trade_strategy_updates_symbol_strategy_id_and_or_timestamp():
    """Test update_trade_strategy updates symbol, strategy_id, and/or timestamp."""
    # First create strategies to reference
    strategy_name1 = "Original Strategy"
    strategy_slug1 = "original-strategy"
    strategy_name2 = "Updated Strategy"
    strategy_slug2 = "updated-strategy"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", strategy_slug1, strategy_slug2)
    
    strategy1 = await create_strategy(strategy_name1, strategy_slug1)
    strategy2 = await create_strategy(strategy_name2, strategy_slug2)
    strategy_id1 = strategy1["id"]
    strategy_id2 = strategy2["id"]
    
    # Clean up any existing trade_strategies first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol IN ($1, $2)", "BTCUSDT", "ETHUSDT")
    
    # Create trade_strategy
    created_record = await create_trade_strategy("BTCUSDT", strategy_id1, "5m")
    trade_strategy_id = created_record["id"]
    
    # Update all fields
    updated_record = await update_trade_strategy(
        trade_strategy_id,
        symbol="ETHUSDT",
        strategy_id=strategy_id2,
        timestamp="15m"
    )
    
    assert updated_record is not None
    assert updated_record["id"] == trade_strategy_id
    assert updated_record["symbol"] == "ETHUSDT"
    assert updated_record["strategy_id"] == strategy_id2
    assert updated_record["timestamp"] == "15m"
    
    # Verify update persisted
    retrieved_record = await get_trade_strategy_by_id(trade_strategy_id)
    assert retrieved_record["symbol"] == "ETHUSDT"
    assert retrieved_record["strategy_id"] == strategy_id2
    assert retrieved_record["timestamp"] == "15m"
    
    # Update only symbol
    updated_record2 = await update_trade_strategy(trade_strategy_id, symbol="ADAUSDT")
    
    assert updated_record2["symbol"] == "ADAUSDT"
    assert updated_record2["strategy_id"] == strategy_id2  # Unchanged
    assert updated_record2["timestamp"] == "15m"  # Unchanged
    
    # Update only strategy_id
    updated_record3 = await update_trade_strategy(trade_strategy_id, strategy_id=strategy_id1)
    
    assert updated_record3["symbol"] == "ADAUSDT"  # Unchanged
    assert updated_record3["strategy_id"] == strategy_id1
    assert updated_record3["timestamp"] == "15m"  # Unchanged
    
    # Update only timestamp
    updated_record4 = await update_trade_strategy(trade_strategy_id, timestamp="1h")
    
    assert updated_record4["symbol"] == "ADAUSDT"  # Unchanged
    assert updated_record4["strategy_id"] == strategy_id1  # Unchanged
    assert updated_record4["timestamp"] == "1h"
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)
        await conn.execute("DELETE FROM strategies WHERE id IN ($1, $2)", strategy_id1, strategy_id2)


@pytest.mark.asyncio
async def test_update_trade_strategy_raises_value_error_when_not_found():
    """Test update_trade_strategy raises ValueError when trade strategy not found."""
    non_existent_id = 999999
    
    # Try to update non-existent trade_strategy
    with pytest.raises(ValueError, match="not found"):
        await update_trade_strategy(non_existent_id, symbol="BTCUSDT")


@pytest.mark.asyncio
async def test_soft_delete_trade_strategy_sets_deleted_at_timestamp():
    """Test soft_delete_trade_strategy sets deleted_at timestamp."""
    # First create a strategy to reference
    strategy_name = "Strategy to Delete"
    strategy_slug = "strategy-to-delete"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", strategy_slug)
    
    strategy = await create_strategy(strategy_name, strategy_slug)
    strategy_id = strategy["id"]
    
    # Clean up any existing trade_strategy first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", "BTCUSDT", strategy_id)
    
    # Create trade_strategy
    created_record = await create_trade_strategy("BTCUSDT", strategy_id, "5m")
    trade_strategy_id = created_record["id"]
    
    # Verify it's not deleted
    assert created_record["deleted_at"] is None
    
    # Soft delete trade_strategy
    deleted_record = await soft_delete_trade_strategy(trade_strategy_id)
    
    assert deleted_record is not None
    assert deleted_record["id"] == trade_strategy_id
    assert deleted_record["deleted_at"] is not None
    
    # Verify deletion persisted
    retrieved_record = await get_trade_strategy_by_id(trade_strategy_id)
    assert retrieved_record["deleted_at"] is not None
    
    # Clean up (hard delete for test cleanup)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_soft_delete_trade_strategy_does_not_remove_record_from_database():
    """Test soft_delete_trade_strategy does not remove record from database."""
    # First create a strategy to reference
    strategy_name = "Strategy to Soft Delete"
    strategy_slug = "strategy-to-soft-delete"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", strategy_slug)
    
    strategy = await create_strategy(strategy_name, strategy_slug)
    strategy_id = strategy["id"]
    
    # Clean up any existing trade_strategy first
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE symbol = $1 AND strategy_id = $2", "BTCUSDT", strategy_id)
    
    # Create trade_strategy
    created_record = await create_trade_strategy("BTCUSDT", strategy_id, "5m")
    trade_strategy_id = created_record["id"]
    
    # Soft delete trade_strategy
    await soft_delete_trade_strategy(trade_strategy_id)
    
    # Verify record still exists in database
    retrieved_record = await get_trade_strategy_by_id(trade_strategy_id)
    assert retrieved_record is not None
    assert retrieved_record["id"] == trade_strategy_id
    assert retrieved_record["symbol"] == "BTCUSDT"
    assert retrieved_record["strategy_id"] == strategy_id
    assert retrieved_record["timestamp"] == "5m"
    assert retrieved_record["deleted_at"] is not None
    
    # Clean up (hard delete for test cleanup)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_strategies WHERE id = $1", trade_strategy_id)
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_soft_delete_trade_strategy_raises_value_error_when_not_found():
    """Test soft_delete_trade_strategy raises ValueError when trade strategy not found."""
    non_existent_id = 999999
    
    # Try to soft delete non-existent trade_strategy
    with pytest.raises(ValueError, match="not found"):
        await soft_delete_trade_strategy(non_existent_id)


@pytest.mark.asyncio
async def test_foreign_key_constraint_prevents_creating_trade_strategy_with_invalid_strategy_id():
    """Test foreign key constraint prevents creating trade_strategy with invalid strategy_id."""
    invalid_strategy_id = 999999
    
    # Try to create trade_strategy with non-existent strategy_id
    with pytest.raises(asyncpg.ForeignKeyViolationError):
        await create_trade_strategy("BTCUSDT", invalid_strategy_id, "5m")

