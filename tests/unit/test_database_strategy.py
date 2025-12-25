"""Unit tests for strategy database functions.

Tests for task 11: Implement strategy database functions.
"""
import pytest
import pytest_asyncio

from app.db.database import (
    create_strategy,
    get_all_strategies,
    get_strategy_by_id,
    update_strategy,
    soft_delete_strategy,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_create_strategy_creates_record_with_name_and_slug():
    """Test create_strategy creates record with name and slug."""
    name = "Momentum Strategy"
    slug = "momentum-strategy"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)
    
    # Create strategy
    record = await create_strategy(name, slug)
    
    assert record is not None
    assert record["name"] == name
    assert record["slug"] == slug
    assert "id" in record
    assert "created_at" in record
    assert "updated_at" in record
    assert record["deleted_at"] is None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)


@pytest.mark.asyncio
async def test_create_strategy_auto_generates_slug_from_name_if_not_provided():
    """Test create_strategy auto-generates slug from name if not provided."""
    name = "Mean Reversion Strategy"
    expected_slug = "mean-reversion-strategy"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", expected_slug)
    
    # Create strategy without slug
    record = await create_strategy(name, slug=None)
    
    assert record is not None
    assert record["name"] == name
    assert record["slug"] == expected_slug
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", expected_slug)


@pytest.mark.asyncio
async def test_create_strategy_auto_generates_slug_with_special_characters():
    """Test create_strategy auto-generates slug correctly with special characters."""
    name = "R.S.I. Strategy (14-period)"
    expected_slug = "rsi-strategy-14-period"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", expected_slug)
    
    # Create strategy without slug
    record = await create_strategy(name, slug=None)
    
    assert record is not None
    assert record["name"] == name
    assert record["slug"] == expected_slug
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", expected_slug)


@pytest.mark.asyncio
async def test_get_all_strategies_returns_all_strategies_including_soft_deleted_when_include_deleted_true():
    """Test get_all_strategies returns all strategies including soft-deleted when include_deleted=True."""
    name1 = "Strategy 1"
    slug1 = "strategy-1"
    name2 = "Strategy 2"
    slug2 = "strategy-2"
    
    # Clean up any existing strategies first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", slug1, slug2)
    
    # Create two strategies
    record1 = await create_strategy(name1, slug1)
    record2 = await create_strategy(name2, slug2)
    
    # Soft delete one strategy
    await soft_delete_strategy(record2["id"])
    
    # Get all strategies including deleted
    strategies = await get_all_strategies(include_deleted=True)
    
    # Should contain both strategies
    strategy_ids = {s["id"] for s in strategies}
    assert record1["id"] in strategy_ids
    assert record2["id"] in strategy_ids
    
    # Find the soft-deleted strategy
    deleted_strategy = next(s for s in strategies if s["id"] == record2["id"])
    assert deleted_strategy["deleted_at"] is not None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", slug1, slug2)


@pytest.mark.asyncio
async def test_get_all_strategies_excludes_soft_deleted_when_include_deleted_false():
    """Test get_all_strategies excludes soft-deleted when include_deleted=False."""
    name1 = "Strategy 3"
    slug1 = "strategy-3"
    name2 = "Strategy 4"
    slug2 = "strategy-4"
    
    # Clean up any existing strategies first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", slug1, slug2)
    
    # Create two strategies
    record1 = await create_strategy(name1, slug1)
    record2 = await create_strategy(name2, slug2)
    
    # Soft delete one strategy
    await soft_delete_strategy(record2["id"])
    
    # Get all strategies excluding deleted
    strategies = await get_all_strategies(include_deleted=False)
    
    # Should contain only non-deleted strategy
    strategy_ids = {s["id"] for s in strategies}
    assert record1["id"] in strategy_ids
    assert record2["id"] not in strategy_ids
    
    # Verify all returned strategies are not deleted
    for strategy in strategies:
        assert strategy["deleted_at"] is None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", slug1, slug2)


@pytest.mark.asyncio
async def test_get_strategy_by_id_retrieves_strategy_by_id():
    """Test get_strategy_by_id retrieves strategy by ID."""
    name = "Test Strategy"
    slug = "test-strategy"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)
    
    # Create strategy
    created_record = await create_strategy(name, slug)
    strategy_id = created_record["id"]
    
    # Retrieve by ID
    retrieved_record = await get_strategy_by_id(strategy_id)
    
    assert retrieved_record is not None
    assert retrieved_record["id"] == strategy_id
    assert retrieved_record["name"] == name
    assert retrieved_record["slug"] == slug
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)


@pytest.mark.asyncio
async def test_get_strategy_by_id_returns_none_when_not_found():
    """Test get_strategy_by_id returns None when not found."""
    non_existent_id = 999999
    
    # Try to retrieve non-existent strategy
    result = await get_strategy_by_id(non_existent_id)
    
    assert result is None


@pytest.mark.asyncio
async def test_update_strategy_updates_name_and_or_slug():
    """Test update_strategy updates name and/or slug."""
    name1 = "Original Strategy"
    slug1 = "original-strategy"
    name2 = "Updated Strategy"
    slug2 = "updated-strategy"
    
    # Clean up any existing strategies first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug IN ($1, $2)", slug1, slug2)
    
    # Create strategy
    created_record = await create_strategy(name1, slug1)
    strategy_id = created_record["id"]
    
    # Update both name and slug
    updated_record = await update_strategy(strategy_id, name=name2, slug=slug2)
    
    assert updated_record is not None
    assert updated_record["id"] == strategy_id
    assert updated_record["name"] == name2
    assert updated_record["slug"] == slug2
    
    # Verify update persisted
    retrieved_record = await get_strategy_by_id(strategy_id)
    assert retrieved_record["name"] == name2
    assert retrieved_record["slug"] == slug2
    
    # Update only name (slug should auto-generate)
    name3 = "New Name Strategy"
    updated_record2 = await update_strategy(strategy_id, name=name3)
    
    assert updated_record2["name"] == name3
    assert updated_record2["slug"] == "new-name-strategy"
    
    # Update only slug
    slug3 = "custom-slug"
    updated_record3 = await update_strategy(strategy_id, slug=slug3)
    
    assert updated_record3["name"] == name3  # Name unchanged
    assert updated_record3["slug"] == slug3
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_update_strategy_raises_value_error_when_not_found():
    """Test update_strategy raises ValueError when strategy not found."""
    non_existent_id = 999999
    
    # Try to update non-existent strategy
    with pytest.raises(ValueError, match="not found"):
        await update_strategy(non_existent_id, name="New Name")


@pytest.mark.asyncio
async def test_soft_delete_strategy_sets_deleted_at_timestamp():
    """Test soft_delete_strategy sets deleted_at timestamp."""
    name = "Strategy to Delete"
    slug = "strategy-to-delete"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)
    
    # Create strategy
    created_record = await create_strategy(name, slug)
    strategy_id = created_record["id"]
    
    # Verify it's not deleted
    assert created_record["deleted_at"] is None
    
    # Soft delete strategy
    deleted_record = await soft_delete_strategy(strategy_id)
    
    assert deleted_record is not None
    assert deleted_record["id"] == strategy_id
    assert deleted_record["deleted_at"] is not None
    
    # Verify deletion persisted
    retrieved_record = await get_strategy_by_id(strategy_id)
    assert retrieved_record["deleted_at"] is not None
    
    # Clean up (hard delete for test cleanup)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_soft_delete_strategy_does_not_remove_record_from_database():
    """Test soft_delete_strategy does not remove record from database."""
    name = "Strategy to Soft Delete"
    slug = "strategy-to-soft-delete"
    
    # Clean up any existing strategy first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE slug = $1", slug)
    
    # Create strategy
    created_record = await create_strategy(name, slug)
    strategy_id = created_record["id"]
    
    # Soft delete strategy
    await soft_delete_strategy(strategy_id)
    
    # Verify record still exists in database
    retrieved_record = await get_strategy_by_id(strategy_id)
    assert retrieved_record is not None
    assert retrieved_record["id"] == strategy_id
    assert retrieved_record["name"] == name
    assert retrieved_record["slug"] == slug
    assert retrieved_record["deleted_at"] is not None
    
    # Clean up (hard delete for test cleanup)
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM strategies WHERE id = $1", strategy_id)


@pytest.mark.asyncio
async def test_soft_delete_strategy_raises_value_error_when_not_found():
    """Test soft_delete_strategy raises ValueError when strategy not found."""
    non_existent_id = 999999
    
    # Try to soft delete non-existent strategy
    with pytest.raises(ValueError, match="not found"):
        await soft_delete_strategy(non_existent_id)

