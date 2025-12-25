"""Unit tests for order schema validation.

Tests for task 13: Create order schemas (OrderCreate, OrderClose, TransactionResponse, OrderListResponse).
"""
import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from app.schemas.order import (
    OrderCreate,
    OrderClose,
    TransactionResponse,
    OrderListResponse
)


def test_order_create_validates_symbol_required():
    """Test OrderCreate validates symbol (required, max 10 chars)."""
    order = OrderCreate(
        symbol="BTCUSDT",
        quantity=Decimal("0.1")
    )
    assert order.symbol == "BTCUSDT"
    assert order.quantity == Decimal("0.1")


def test_order_create_validates_quantity_required():
    """Test OrderCreate validates quantity (required, positive Decimal)."""
    order = OrderCreate(
        symbol="BTCUSDT",
        quantity=Decimal("0.1")
    )
    assert order.quantity == Decimal("0.1")
    assert isinstance(order.quantity, Decimal)


def test_order_create_rejects_symbol_exceeding_10_characters():
    """Test OrderCreate rejects symbol exceeding 10 characters."""
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(
            symbol="BTCUSDTEXTRA",  # 13 characters
            quantity=Decimal("0.1")
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_long"
        for error in errors
    )


def test_order_create_rejects_negative_quantity():
    """Test OrderCreate rejects negative quantity."""
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(
            symbol="BTCUSDT",
            quantity=Decimal("-0.1")
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("quantity",) and "greater_than" in str(error["type"]).lower()
        for error in errors
    )


def test_order_create_rejects_zero_quantity():
    """Test OrderCreate rejects zero quantity."""
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(
            symbol="BTCUSDT",
            quantity=Decimal("0")
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("quantity",) and "greater_than" in str(error["type"]).lower()
        for error in errors
    )


def test_order_close_validates_symbol_required():
    """Test OrderClose validates symbol (required, max 10 chars)."""
    order_close = OrderClose(symbol="BTCUSDT")
    assert order_close.symbol == "BTCUSDT"


def test_order_close_rejects_symbol_exceeding_10_characters():
    """Test OrderClose rejects symbol exceeding 10 characters."""
    with pytest.raises(ValidationError) as exc_info:
        OrderClose(symbol="BTCUSDTEXTRA")  # 13 characters
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_long"
        for error in errors
    )


def test_transaction_response_includes_all_transaction_fields():
    """Test TransactionResponse includes all transaction fields with computed fields.
    
    All decimal fields are now strings to preserve precision in JSON serialization,
    consistent with UserResponse.balance pattern.
    """
    transaction = TransactionResponse(
        id=1,
        symbol="BTCUSDT",
        buy_price="50000.00000000000000000000",
        sell_price="51000.00000000000000000000",
        status=2,
        quantity="0.10000000000000000000",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        diff="1000.00000000000000000000",
        buyAggregate="5000.00000000000000000000",
        sellAggregate="5100.00000000000000000000",
        diffDollar="100.00000000000000000000"
    )
    
    assert transaction.id == 1
    assert transaction.symbol == "BTCUSDT"
    assert transaction.buy_price == "50000.00000000000000000000"
    assert transaction.sell_price == "51000.00000000000000000000"
    assert transaction.status == 2
    assert transaction.quantity == "0.10000000000000000000"
    assert transaction.diff == "1000.00000000000000000000"
    assert transaction.buyAggregate == "5000.00000000000000000000"
    assert transaction.sellAggregate == "5100.00000000000000000000"
    assert transaction.diffDollar == "100.00000000000000000000"
    # Verify all decimal fields are strings
    assert isinstance(transaction.buy_price, str)
    assert isinstance(transaction.quantity, str)


def test_transaction_response_handles_null_sell_price():
    """Test TransactionResponse handles NULL sell_price correctly in computed fields."""
    transaction = TransactionResponse(
        id=1,
        symbol="BTCUSDT",
        buy_price="50000.00000000000000000000",
        sell_price=None,
        status=1,
        quantity="0.10000000000000000000",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        diff=None,
        buyAggregate="5000.00000000000000000000",
        sellAggregate=None,
        diffDollar="0.00000000000000000000"
    )
    
    assert transaction.sell_price is None
    assert transaction.diff is None
    assert transaction.sellAggregate is None
    assert transaction.diffDollar == "0.00000000000000000000"


def test_transaction_response_string_fields_maintain_precision():
    """Test string fields maintain precision in serialization.
    
    All decimal fields are now strings to preserve precision in JSON serialization.
    """
    high_precision = "50000.12345678901234567890"
    transaction = TransactionResponse(
        id=1,
        symbol="BTCUSDT",
        buy_price=high_precision,
        sell_price=None,
        status=1,
        quantity="0.12345678901234567890",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        buyAggregate="6172.83950617283950617290",
        diffDollar="0.00000000000000000000"
    )
    
    assert transaction.buy_price == high_precision
    assert isinstance(transaction.buy_price, str)
    assert isinstance(transaction.quantity, str)


def test_order_list_response_includes_orders_list():
    """Test OrderListResponse includes orders list and unique_symbols."""
    transaction1 = TransactionResponse(
        id=1,
        symbol="BTCUSDT",
        buy_price="50000.00000000000000000000",
        sell_price=None,
        status=1,
        quantity="0.10000000000000000000",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        buyAggregate="5000.00000000000000000000",
        diffDollar="0.00000000000000000000"
    )
    
    transaction2 = TransactionResponse(
        id=2,
        symbol="ETHUSDT",
        buy_price="3000.00000000000000000000",
        sell_price=None,
        status=1,
        quantity="1.00000000000000000000",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        buyAggregate="3000.00000000000000000000",
        diffDollar="0.00000000000000000000"
    )
    
    order_list = OrderListResponse(
        orders=[transaction1, transaction2],
        unique_symbols=["BTCUSDT", "ETHUSDT"]
    )
    
    assert len(order_list.orders) == 2
    assert order_list.orders[0].symbol == "BTCUSDT"
    assert order_list.orders[1].symbol == "ETHUSDT"
    assert len(order_list.unique_symbols) == 2
    assert "BTCUSDT" in order_list.unique_symbols
    assert "ETHUSDT" in order_list.unique_symbols


def test_order_list_response_empty_lists():
    """Test OrderListResponse handles empty lists correctly."""
    order_list = OrderListResponse()
    
    assert order_list.orders == []
    assert order_list.unique_symbols == []


def test_order_create_symbol_max_length_boundary():
    """Test OrderCreate accepts symbol at exactly 10 characters."""
    order = OrderCreate(
        symbol="1234567890",  # Exactly 10 characters
        quantity=Decimal("0.1")
    )
    assert order.symbol == "1234567890"


def test_order_create_symbol_min_length():
    """Test OrderCreate accepts symbol with minimum length (1 character)."""
    order = OrderCreate(
        symbol="A",
        quantity=Decimal("0.1")
    )
    assert order.symbol == "A"


def test_order_create_rejects_empty_symbol():
    """Test OrderCreate rejects empty symbol."""
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(
            symbol="",
            quantity=Decimal("0.1")
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_short"
        for error in errors
    )

