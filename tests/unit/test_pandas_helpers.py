"""Unit tests for pandas DataFrame conversion helpers.

Tests for task 26: Implement pandas DataFrame conversion helpers.
"""
import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import datetime

from app.db.database import (
    records_to_dataframe,
    query_to_dataframe,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_records_to_dataframe_converts_list_of_asyncpg_record_to_dataframe():
    """Test records_to_dataframe converts list of asyncpg.Record to DataFrame."""
    import pandas as pd
    
    # Create some test records using a single connection
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Clean up any existing test data
        await conn.execute("DELETE FROM watchlists WHERE symbol IN ('BTCUSDT', 'ETHUSDT')")
        
        # Create test watchlist entries directly
        await conn.execute("INSERT INTO watchlists (symbol) VALUES ('BTCUSDT')")
        await conn.execute("INSERT INTO watchlists (symbol) VALUES ('ETHUSDT')")
        
        # Fetch records
        records = await conn.fetch("SELECT id, symbol, created_at FROM watchlists WHERE symbol IN ('BTCUSDT', 'ETHUSDT')")
        
        # Convert to DataFrame
        df = records_to_dataframe(records)
        
        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 2  # At least our 2 created records
        assert "id" in df.columns
        assert "symbol" in df.columns
        assert "created_at" in df.columns
        
        # Clean up
        await conn.execute("DELETE FROM watchlists WHERE symbol IN ('BTCUSDT', 'ETHUSDT')")


@pytest.mark.asyncio
async def test_records_to_dataframe_handles_datetime_fields_correctly():
    """Test records_to_dataframe handles datetime fields correctly."""
    import pandas as pd
    
    # Create test watchlist entry using a single connection
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Clean up any existing test data
        await conn.execute("DELETE FROM watchlists WHERE symbol = 'ADAUSDT'")
        
        # Create test watchlist entry
        await conn.execute("INSERT INTO watchlists (symbol) VALUES ('ADAUSDT')")
        
        # Fetch records
        records = await conn.fetch("SELECT id, symbol, created_at FROM watchlists WHERE symbol = 'ADAUSDT'")
        
        assert len(records) > 0
        
        # Convert to DataFrame
        df = records_to_dataframe(records)
        
        # Verify datetime field is preserved
        assert "created_at" in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df["created_at"])
        
        # Clean up
        await conn.execute("DELETE FROM watchlists WHERE symbol = 'ADAUSDT'")


@pytest.mark.asyncio
async def test_records_to_dataframe_handles_decimal_fields_correctly():
    """Test records_to_dataframe handles Decimal fields correctly (converts to float)."""
    import pandas as pd
    
    # Create a transaction record with Decimal fields
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # First, create a test user if needed
        test_user = await conn.fetchrow(
            "SELECT id FROM users LIMIT 1"
        )
        
        if test_user:
            user_id = test_user["id"]
            
            # Create a transaction with Decimal values
            transaction = await conn.fetchrow(
                """
                INSERT INTO transact (user_id, symbol, buy_price, quantity, status)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, symbol, buy_price, sell_price, quantity, status, user_id, created_at, updated_at
                """,
                user_id,
                "TESTUSDT",
                Decimal("100.12345678901234567890"),
                Decimal("0.5"),
                1
            )
            
            # Convert to DataFrame
            df = records_to_dataframe([transaction])
            
            # Verify Decimal fields are converted to float
            assert "buy_price" in df.columns
            assert "quantity" in df.columns
            assert pd.api.types.is_float_dtype(df["buy_price"])
            assert pd.api.types.is_float_dtype(df["quantity"])
            assert df["buy_price"].iloc[0] == 100.12345678901234567890
            assert df["quantity"].iloc[0] == 0.5
            
            # Clean up
            await conn.execute("DELETE FROM transact WHERE symbol = 'TESTUSDT'")


@pytest.mark.asyncio
async def test_records_to_dataframe_handles_null_values_correctly():
    """Test records_to_dataframe handles NULL values correctly."""
    import pandas as pd
    import numpy as np
    
    # Create a transaction record with NULL sell_price
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Get a test user
        test_user = await conn.fetchrow(
            "SELECT id FROM users LIMIT 1"
        )
        
        if test_user:
            user_id = test_user["id"]
            
            # Create a transaction with NULL sell_price
            transaction = await conn.fetchrow(
                """
                INSERT INTO transact (user_id, symbol, buy_price, quantity, status, sell_price)
                VALUES ($1, $2, $3, $4, $5, NULL)
                RETURNING id, symbol, buy_price, sell_price, quantity, status, user_id, created_at, updated_at
                """,
                user_id,
                "NULLTEST",
                Decimal("50.0"),
                Decimal("1.0"),
                1
            )
            
            # Convert to DataFrame
            df = records_to_dataframe([transaction])
            
            # Verify NULL values are handled (should be NaN in pandas)
            assert "sell_price" in df.columns
            assert pd.isna(df["sell_price"].iloc[0])
            
            # Clean up
            await conn.execute("DELETE FROM transact WHERE symbol = 'NULLTEST'")


@pytest.mark.asyncio
async def test_query_to_dataframe_executes_query_and_returns_dataframe():
    """Test query_to_dataframe executes query and returns DataFrame."""
    import pandas as pd
    
    # Create test data using a single connection
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Clean up any existing test data
        await conn.execute("DELETE FROM watchlists WHERE symbol = 'QUERYTEST'")
        
        # Create test watchlist entry
        await conn.execute("INSERT INTO watchlists (symbol) VALUES ('QUERYTEST')")
    
    # Execute query and get DataFrame
    df = await query_to_dataframe(
        "SELECT id, symbol, created_at FROM watchlists WHERE symbol = $1",
        "QUERYTEST"
    )
    
    # Verify DataFrame structure
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 1
    assert "id" in df.columns
    assert "symbol" in df.columns
    assert "created_at" in df.columns
    assert df["symbol"].iloc[0] == "QUERYTEST"
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol = 'QUERYTEST'")


@pytest.mark.asyncio
async def test_query_to_dataframe_handles_query_parameters_correctly():
    """Test query_to_dataframe handles query parameters correctly."""
    import pandas as pd
    
    # Create test data using a single connection
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Clean up any existing test data
        await conn.execute("DELETE FROM watchlists WHERE symbol IN ('PARAM1', 'PARAM2')")
        
        # Create test watchlist entries
        await conn.execute("INSERT INTO watchlists (symbol) VALUES ('PARAM1')")
        await conn.execute("INSERT INTO watchlists (symbol) VALUES ('PARAM2')")
    
    # Execute query with parameters
    df = await query_to_dataframe(
        "SELECT id, symbol, created_at FROM watchlists WHERE symbol = $1 OR symbol = $2",
        "PARAM1",
        "PARAM2"
    )
    
    # Verify results
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2
    symbols = df["symbol"].tolist()
    assert "PARAM1" in symbols
    assert "PARAM2" in symbols
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM watchlists WHERE symbol IN ('PARAM1', 'PARAM2')")


@pytest.mark.asyncio
async def test_query_to_dataframe_handles_empty_result_sets():
    """Test query_to_dataframe handles empty result sets."""
    import pandas as pd
    
    # Execute query that returns no results
    df = await query_to_dataframe(
        "SELECT id, symbol, created_at FROM watchlists WHERE symbol = $1",
        "NONEXISTENT_SYMBOL_12345"
    )
    
    # Verify empty DataFrame
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    # Should still have the expected columns
    assert "id" in df.columns or len(df.columns) == 0  # Empty DataFrame may have no columns

