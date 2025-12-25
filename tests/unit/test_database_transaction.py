"""Unit tests for transaction (order) database functions.

Tests for task 8: Implement transaction (order) database functions.
"""
import pytest
import pytest_asyncio
from decimal import Decimal

from app.db.database import (
    create_transaction,
    get_active_transaction,
    update_transaction,
    get_user_transactions,
    create_user,
    get_db_pool,
)


@pytest.mark.asyncio
async def test_create_transaction_creates_record_with_status_one():
    """Test create_transaction creates record with status=1 (active)."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_create_tx@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Create TX Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
        await conn.execute("DELETE FROM transact WHERE user_id IN (SELECT id FROM users WHERE email = $1)", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transaction
    symbol = "BTCUSDT"
    buy_price = Decimal("50000.00")
    quantity = Decimal("0.1")
    
    transaction = await create_transaction(user_id, symbol, buy_price, quantity)
    
    assert transaction is not None
    assert transaction["status"] == 1  # Active
    assert transaction["symbol"] == symbol
    assert transaction["buy_price"] == buy_price
    assert transaction["quantity"] == quantity
    assert transaction["user_id"] == user_id
    assert transaction["sell_price"] is None  # Not set yet
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_create_transaction_stores_buy_price_quantity_symbol_user_id_correctly():
    """Test create_transaction stores buy_price, quantity, symbol, user_id correctly."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_store_tx@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Store TX Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transaction with specific values
    symbol = "ETHUSDT"
    buy_price = Decimal("3000.50")
    quantity = Decimal("2.5")
    
    transaction = await create_transaction(user_id, symbol, buy_price, quantity)
    
    assert transaction is not None
    assert transaction["symbol"] == symbol
    assert transaction["buy_price"] == buy_price
    assert transaction["quantity"] == quantity
    assert transaction["user_id"] == user_id
    assert "id" in transaction
    assert "created_at" in transaction
    assert "updated_at" in transaction
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_active_transaction_finds_active_transaction():
    """Test get_active_transaction finds active transaction (status=1) for user and symbol."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_get_active@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Get Active Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create active transaction
    symbol = "BTCUSDT"
    buy_price = Decimal("50000.00")
    quantity = Decimal("0.1")
    
    created_tx = await create_transaction(user_id, symbol, buy_price, quantity)
    tx_id = created_tx["id"]
    
    # Retrieve active transaction
    active_tx = await get_active_transaction(user_id, symbol)
    
    assert active_tx is not None
    assert active_tx["id"] == tx_id
    assert active_tx["status"] == 1
    assert active_tx["symbol"] == symbol
    assert active_tx["user_id"] == user_id
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_active_transaction_returns_none_when_no_active_transaction_exists():
    """Test get_active_transaction returns None when no active transaction exists."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_no_active@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "No Active Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Try to get active transaction for non-existent symbol
    active_tx = await get_active_transaction(user_id, "ETHUSDT")
    
    assert active_tx is None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_active_transaction_returns_none_for_closed_transaction():
    """Test get_active_transaction returns None for closed transaction (status=2)."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_closed_tx@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Closed TX Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create and close transaction
    symbol = "BTCUSDT"
    buy_price = Decimal("50000.00")
    quantity = Decimal("0.1")
    
    created_tx = await create_transaction(user_id, symbol, buy_price, quantity)
    tx_id = created_tx["id"]
    
    # Close the transaction
    sell_price = Decimal("51000.00")
    await update_transaction(tx_id, sell_price, 2)
    
    # Try to get active transaction (should return None)
    active_tx = await get_active_transaction(user_id, symbol)
    
    assert active_tx is None
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_update_transaction_updates_sell_price_and_status_correctly():
    """Test update_transaction updates sell_price and status correctly."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_update_tx@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Update TX Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transaction
    symbol = "BTCUSDT"
    buy_price = Decimal("50000.00")
    quantity = Decimal("0.1")
    
    created_tx = await create_transaction(user_id, symbol, buy_price, quantity)
    tx_id = created_tx["id"]
    
    # Update transaction
    sell_price = Decimal("51000.00")
    new_status = 2
    
    updated_tx = await update_transaction(tx_id, sell_price, new_status)
    
    assert updated_tx is not None
    assert updated_tx["id"] == tx_id
    assert updated_tx["sell_price"] == sell_price
    assert updated_tx["status"] == new_status
    assert updated_tx["buy_price"] == buy_price  # Should remain unchanged
    assert updated_tx["quantity"] == quantity  # Should remain unchanged
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_user_transactions_returns_all_transactions_for_user():
    """Test get_user_transactions returns all transactions for user."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_get_all@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Get All Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create multiple transactions
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    tx3 = await create_transaction(user_id, "ADAUSDT", Decimal("1.00"), Decimal("100.0"))
    
    # Get all transactions
    transactions = await get_user_transactions(user_id)
    
    assert len(transactions) == 3
    tx_ids = {tx["id"] for tx in transactions}
    assert tx1["id"] in tx_ids
    assert tx2["id"] in tx_ids
    assert tx3["id"] in tx_ids
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_user_transactions_filters_by_active_only_true():
    """Test get_user_transactions filters by active_only=True."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_filter_active@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Filter Active Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transactions
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    
    # Close one transaction
    await update_transaction(tx1["id"], Decimal("51000.00"), 2)
    
    # Get only active transactions
    active_transactions = await get_user_transactions(user_id, active_only=True)
    
    assert len(active_transactions) == 1
    assert active_transactions[0]["id"] == tx2["id"]
    assert active_transactions[0]["status"] == 1
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_user_transactions_filters_by_symbol():
    """Test get_user_transactions filters by symbol."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_filter_symbol@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Filter Symbol Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transactions with different symbols
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    tx3 = await create_transaction(user_id, "BTCUSDT", Decimal("51000.00"), Decimal("0.2"))
    
    # Get transactions filtered by symbol
    btc_transactions = await get_user_transactions(user_id, symbol="BTCUSDT")
    
    assert len(btc_transactions) == 2
    for tx in btc_transactions:
        assert tx["symbol"] == "BTCUSDT"
        assert tx["id"] in [tx1["id"], tx3["id"]]
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_user_transactions_orders_by_status_asc_created_at_desc():
    """Test get_user_transactions orders by status ASC, created_at DESC."""
    from passlib.context import CryptContext
    import asyncio
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_order@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Order Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transactions with delays to ensure different created_at timestamps
    tx1 = await create_transaction(user_id, "BTCUSDT", Decimal("50000.00"), Decimal("0.1"))
    await asyncio.sleep(0.01)  # Small delay
    
    tx2 = await create_transaction(user_id, "ETHUSDT", Decimal("3000.00"), Decimal("1.0"))
    await asyncio.sleep(0.01)
    
    tx3 = await create_transaction(user_id, "ADAUSDT", Decimal("1.00"), Decimal("100.0"))
    
    # Close tx2 (status=2)
    await update_transaction(tx2["id"], Decimal("3100.00"), 2)
    
    # Get all transactions
    transactions = await get_user_transactions(user_id)
    
    # Should be ordered by status ASC (1 comes before 2), then created_at DESC
    assert len(transactions) == 3
    
    # First two should be status=1 (active), ordered by created_at DESC (newest first)
    assert transactions[0]["status"] == 1
    assert transactions[1]["status"] == 1
    assert transactions[0]["id"] == tx3["id"]  # Newest active
    assert transactions[1]["id"] == tx1["id"]  # Older active
    
    # Last should be status=2 (closed)
    assert transactions[2]["status"] == 2
    assert transactions[2]["id"] == tx2["id"]
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_user_transactions_calculates_computed_fields():
    """Test get_user_transactions calculates computed fields (diff, buyAggregate, sellAggregate, diffDollar)."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_computed@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Computed Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create transaction
    buy_price = Decimal("50000.00")
    quantity = Decimal("0.1")
    tx = await create_transaction(user_id, "BTCUSDT", buy_price, quantity)
    
    # Get transactions (should have NULL sell_price)
    transactions = await get_user_transactions(user_id)
    
    assert len(transactions) == 1
    tx_result = transactions[0]
    
    # Check computed fields for active transaction
    assert tx_result["buyAggregate"] == buy_price * quantity  # 5000.00
    assert tx_result["sellAggregate"] is None  # sell_price is NULL
    assert tx_result["diff"] is None  # sell_price is NULL
    assert tx_result["diffDollar"] == 0  # status=1, so diffDollar=0
    
    # Close transaction
    sell_price = Decimal("51000.00")
    await update_transaction(tx["id"], sell_price, 2)
    
    # Get transactions again
    transactions = await get_user_transactions(user_id)
    
    assert len(transactions) == 1
    tx_result = transactions[0]
    
    # Check computed fields for closed transaction
    expected_diff = sell_price - buy_price
    expected_buy_agg = buy_price * quantity
    expected_sell_agg = sell_price * quantity
    expected_diff_dollar = expected_diff * quantity
    
    assert tx_result["diff"] == expected_diff  # 1000.00
    assert tx_result["buyAggregate"] == expected_buy_agg  # 5000.00
    assert tx_result["sellAggregate"] == expected_sell_agg  # 5100.00
    assert tx_result["diffDollar"] == expected_diff_dollar  # 100.00
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_get_user_transactions_computed_fields_handle_null_sell_price_correctly():
    """Test computed fields handle NULL sell_price correctly."""
    from passlib.context import CryptContext
    
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    email = "test_null_sell@example.com"
    password_hash = password_context.hash("testpassword123")
    name = "Null Sell Test User"
    
    # Clean up any existing user first
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE email = $1", email)
    
    # Create user
    user_record = await create_user(email, password_hash, name)
    user_id = user_record["id"]
    
    # Create active transaction (sell_price is NULL)
    buy_price = Decimal("50000.00")
    quantity = Decimal("0.1")
    tx = await create_transaction(user_id, "BTCUSDT", buy_price, quantity)
    
    # Get transactions
    transactions = await get_user_transactions(user_id)
    
    assert len(transactions) == 1
    tx_result = transactions[0]
    
    # When sell_price is NULL:
    # - diff should be NULL (sell_price - buy_price = NULL)
    # - sellAggregate should be NULL (sell_price * quantity = NULL)
    # - buyAggregate should be calculated (buy_price * quantity)
    # - diffDollar should be 0 (status=1)
    assert tx_result["sell_price"] is None
    assert tx_result["diff"] is None
    assert tx_result["sellAggregate"] is None
    assert tx_result["buyAggregate"] == buy_price * quantity
    assert tx_result["diffDollar"] == 0
    
    # Clean up
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM transact WHERE user_id = $1", user_id)
        await conn.execute("DELETE FROM users WHERE id = $1", user_id)

