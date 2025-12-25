"""Unit tests for watchlist database functions.

Tests for task 9: Implement watchlist database functions.
"""
import pytest
import pytest_asyncio

from app.db.database import (
    create_watchlist,
    get_watchlists,
    delete_watchlist,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_create_watchlist_creates_new_watchlist_entry_with_symbol():
    """Test create_watchlist creates new watchlist entry with symbol."""
    symbol = "BTCUSDT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Create watchlist
    record = await create_watchlist(symbol)
    
    assert record is not None
    assert record["symbol"] == symbol
    assert "id" in record
    assert "created_at" in record
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)


@pytest.mark.asyncio
async def test_get_watchlists_returns_all_watchlist_entries():
    """Test get_watchlists returns all watchlist entries."""
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    # Clean up any existing watchlists first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for symbol in symbols:
            await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Create multiple watchlists
    created_records = []
    for symbol in symbols:
        record = await create_watchlist(symbol)
        created_records.append(record)
    
    # Get all watchlists
    watchlists = await get_watchlists()
    
    # Should contain at least our created watchlists
    watchlist_symbols = {w["symbol"] for w in watchlists}
    for symbol in symbols:
        assert symbol in watchlist_symbols
    
    # Verify our created records are in the results
    watchlist_ids = {w["id"] for w in watchlists}
    for record in created_records:
        assert record["id"] in watchlist_ids
    
    # Clean up
    async with pool.acquire() as conn:
        for symbol in symbols:
            await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)


@pytest.mark.asyncio
async def test_delete_watchlist_removes_entry_by_symbol():
    """Test delete_watchlist removes entry by symbol."""
    symbol = "BTCUSDT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Create watchlist
    created_record = await create_watchlist(symbol)
    created_id = created_record["id"]
    
    # Verify it exists
    watchlists_before = await get_watchlists()
    watchlist_ids_before = {w["id"] for w in watchlists_before}
    assert created_id in watchlist_ids_before
    
    # Delete watchlist
    result = await delete_watchlist(symbol)
    
    assert result is True
    
    # Verify it's gone
    watchlists_after = await get_watchlists()
    watchlist_ids_after = {w["id"] for w in watchlists_after}
    assert created_id not in watchlist_ids_after


@pytest.mark.asyncio
async def test_delete_watchlist_returns_false_when_symbol_not_found():
    """Test delete_watchlist returns False when symbol not found."""
    symbol = "NONEXISTENT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Try to delete non-existent watchlist
    result = await delete_watchlist(symbol)
    
    assert result is False


@pytest.mark.asyncio
async def test_delete_watchlist_returns_true_when_deletion_succeeds():
    """Test delete_watchlist returns True when deletion succeeds."""
    symbol = "ETHUSDT"
    
    # Clean up any existing watchlist first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = $1", symbol)
    
    # Create watchlist
    await create_watchlist(symbol)
    
    # Delete watchlist
    result = await delete_watchlist(symbol)
    
    assert result is True
    
    # Verify it's actually deleted
    watchlists = await get_watchlists()
    watchlist_symbols = {w["symbol"] for w in watchlists}
    assert symbol not in watchlist_symbols

