"""Unit tests for log database functions.

Tests for task 10: Implement log database functions.
"""
import pytest
import pytest_asyncio
import json

from app.db.database import (
    create_log,
    get_logs,
    get_unique_log_symbols,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_create_log_stores_symbol_data_action_correctly():
    """Test create_log stores symbol, data (as JSON text), action correctly."""
    symbol = "BTCUSDT"
    data = {"price": 50000.00, "volume": 100.5, "timestamp": "2024-01-01T00:00:00Z"}
    action = "buy"
    
    # Clean up any existing log first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1 AND action = $2", symbol, action)
    
    # Create log
    record = await create_log(symbol, data, action)
    
    assert record is not None
    assert record["symbol"] == symbol
    assert record["action"] == action
    assert "id" in record
    assert "created_at" in record
    assert "updated_at" in record
    
    # Verify data is stored as JSON text
    data_text = record["data"]
    assert isinstance(data_text, str)
    
    # Parse and verify JSON content
    parsed_data = json.loads(data_text)
    assert parsed_data == data
    assert parsed_data["price"] == 50000.00
    assert parsed_data["volume"] == 100.5
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE id = $1", record["id"])


@pytest.mark.asyncio
async def test_get_logs_returns_logs_ordered_by_created_at_desc():
    """Test get_logs returns logs ordered by created_at DESC."""
    symbol1 = "BTCUSDT"
    symbol2 = "ETHUSDT"
    data1 = {"price": 50000.00}
    data2 = {"price": 3000.00}
    action = "analysis"
    
    # Clean up any existing logs first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for symbol in [symbol1, symbol2]:
            await conn.execute("DELETE FROM log WHERE symbol = $1 AND action = $2", symbol, action)
    
    # Create logs with delays to ensure different created_at timestamps
    import asyncio
    log1 = await create_log(symbol1, data1, action)
    await asyncio.sleep(0.01)  # Small delay
    log2 = await create_log(symbol2, data2, action)
    
    # Get logs
    logs, total_count = await get_logs()
    
    # Should be ordered by created_at DESC (newest first)
    assert total_count >= 2
    
    # Find our logs in the results
    log_ids = {log["id"] for log in logs}
    assert log1["id"] in log_ids
    assert log2["id"] in log_ids
    
    # Find positions of our logs
    log1_index = next(i for i, log in enumerate(logs) if log["id"] == log1["id"])
    log2_index = next(i for i, log in enumerate(logs) if log["id"] == log2["id"])
    
    # log2 should come before log1 (newer first)
    assert log2_index < log1_index
    
    # Clean up
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for log_id in [log1["id"], log2["id"]]:
            await conn.execute("DELETE FROM log WHERE id = $1", log_id)


@pytest.mark.asyncio
async def test_get_logs_filters_by_symbol_like_search():
    """Test get_logs filters by symbol (LIKE search)."""
    symbol1 = "BTCUSDT"
    symbol2 = "ETHUSDT"
    data1 = {"price": 50000.00}
    data2 = {"price": 3000.00}
    action = "buy"
    
    # Clean up any existing logs first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for symbol in [symbol1, symbol2]:
            await conn.execute("DELETE FROM log WHERE symbol = $1 AND action = $2", symbol, action)
    
    # Create logs with different symbols
    log1 = await create_log(symbol1, data1, action)
    log2 = await create_log(symbol2, data2, action)
    
    # Filter by "BTC" (should match BTCUSDT)
    logs, total_count = await get_logs(symbol="BTC")
    
    # Should find at least our BTC log
    log_ids = {log["id"] for log in logs}
    assert log1["id"] in log_ids
    # log2 should not be in results (different symbol)
    assert log2["id"] not in log_ids
    
    # All results should contain "BTC" in symbol
    for log in logs:
        assert "BTC" in log["symbol"]
    
    # Clean up
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for log_id in [log1["id"], log2["id"]]:
            await conn.execute("DELETE FROM log WHERE id = $1", log_id)


@pytest.mark.asyncio
async def test_get_logs_supports_pagination_limit_offset():
    """Test get_logs supports pagination (limit, offset)."""
    symbol = "TESTUSDT"
    action = "test"
    
    # Clean up any existing logs first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)
    
    # Create multiple logs
    created_logs = []
    for i in range(5):
        data = {"index": i, "value": f"test_{i}"}
        log = await create_log(symbol, data, action)
        created_logs.append(log)
    
    # Get first page (limit=2, offset=0)
    logs_page1, total_count = await get_logs(limit=2, offset=0)
    
    assert total_count >= 5
    assert len(logs_page1) == 2
    
    # Get second page (limit=2, offset=2)
    logs_page2, _ = await get_logs(limit=2, offset=2)
    
    assert len(logs_page2) == 2
    
    # Verify no overlap between pages
    page1_ids = {log["id"] for log in logs_page1}
    page2_ids = {log["id"] for log in logs_page2}
    assert page1_ids.isdisjoint(page2_ids)
    
    # Get third page (limit=2, offset=4)
    logs_page3, _ = await get_logs(limit=2, offset=4)
    
    assert len(logs_page3) >= 1  # At least one more log
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)


@pytest.mark.asyncio
async def test_get_logs_returns_total_count_for_pagination():
    """Test get_logs returns total_count for pagination."""
    symbol = "COUNTUSDT"
    action = "count_test"
    
    # Clean up any existing logs first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)
    
    # Create multiple logs
    created_count = 7
    for i in range(created_count):
        data = {"index": i}
        await create_log(symbol, data, action)
    
    # Get logs with pagination
    logs_page1, total_count = await get_logs(symbol=symbol, limit=3, offset=0)
    
    # total_count should match the number of logs we created (at least)
    assert total_count >= created_count
    assert len(logs_page1) == 3
    
    # Get second page
    logs_page2, total_count2 = await get_logs(symbol=symbol, limit=3, offset=3)
    
    # total_count should be the same
    assert total_count2 == total_count
    
    # Get third page
    logs_page3, total_count3 = await get_logs(symbol=symbol, limit=3, offset=6)
    
    # total_count should still be the same
    assert total_count3 == total_count
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1", symbol)


@pytest.mark.asyncio
async def test_get_unique_log_symbols_returns_list_of_unique_symbols():
    """Test get_unique_log_symbols returns list of unique symbols."""
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BTCUSDT"]  # BTCUSDT appears twice
    action = "unique_test"
    
    # Clean up any existing logs first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        for symbol in set(symbols):
            await conn.execute("DELETE FROM log WHERE symbol = $1 AND action = $2", symbol, action)
    
    # Create logs with duplicate symbols
    for symbol in symbols:
        data = {"symbol": symbol}
        await create_log(symbol, data, action)
    
    # Get unique symbols
    unique_symbols = await get_unique_log_symbols()
    
    # Should contain our symbols (unique)
    unique_set = set(unique_symbols)
    assert "BTCUSDT" in unique_set
    assert "ETHUSDT" in unique_set
    assert "ADAUSDT" in unique_set
    
    # Should be sorted alphabetically
    assert unique_symbols == sorted(unique_symbols)
    
    # Clean up
    async with pool.acquire() as conn:
        for symbol in set(symbols):
            await conn.execute("DELETE FROM log WHERE symbol = $1 AND action = $2", symbol, action)


@pytest.mark.asyncio
async def test_data_field_is_stored_and_retrieved_as_json_text():
    """Test data field is stored and retrieved as JSON text."""
    symbol = "JSONUSDT"
    action = "json_test"
    
    # Complex nested data structure
    data = {
        "price": 50000.00,
        "volume": 100.5,
        "metadata": {
            "source": "binance",
            "timestamp": "2024-01-01T00:00:00Z",
            "tags": ["crypto", "btc"]
        },
        "array": [1, 2, 3, 4, 5],
        "boolean": True,
        "null_value": None
    }
    
    # Clean up any existing log first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE symbol = $1 AND action = $2", symbol, action)
    
    # Create log
    created_log = await create_log(symbol, data, action)
    
    # Verify data is stored as JSON text string
    data_text = created_log["data"]
    assert isinstance(data_text, str)
    
    # Parse JSON and verify content
    parsed_data = json.loads(data_text)
    assert parsed_data["price"] == 50000.00
    assert parsed_data["volume"] == 100.5
    assert parsed_data["metadata"]["source"] == "binance"
    assert parsed_data["metadata"]["tags"] == ["crypto", "btc"]
    assert parsed_data["array"] == [1, 2, 3, 4, 5]
    assert parsed_data["boolean"] is True
    assert parsed_data["null_value"] is None
    
    # Retrieve log using get_logs
    logs, _ = await get_logs(symbol=symbol)
    
    assert len(logs) >= 1
    retrieved_log = next(log for log in logs if log["id"] == created_log["id"])
    
    # Verify retrieved data is also JSON text
    retrieved_data_text = retrieved_log["data"]
    assert isinstance(retrieved_data_text, str)
    
    # Parse and verify it matches original
    retrieved_parsed = json.loads(retrieved_data_text)
    assert retrieved_parsed == data
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM log WHERE id = $1", created_log["id"])

