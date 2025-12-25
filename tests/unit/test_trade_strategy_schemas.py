"""Unit tests for trade_strategy schema validation.

Tests for task 17: Create trade_strategy schemas (TradeStrategyCreate, TradeStrategyUpdate, TradeStrategyResponse, TradeStrategyListResponse).
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.trade_strategy import (
    TradeStrategyCreate,
    TradeStrategyUpdate,
    TradeStrategyResponse,
    TradeStrategyListResponse
)


def test_trade_strategy_create_validates_symbol_required():
    """Test TradeStrategyCreate validates symbol (required, max 15 chars)."""
    trade_strategy = TradeStrategyCreate(
        symbol="BTCUSDT",
        strategy_id=1
    )
    assert trade_strategy.symbol == "BTCUSDT"
    assert trade_strategy.strategy_id == 1
    assert trade_strategy.timestamp == "5m"  # Default value


def test_trade_strategy_create_validates_strategy_id_required():
    """Test TradeStrategyCreate validates strategy_id (required)."""
    trade_strategy = TradeStrategyCreate(
        symbol="BTCUSDT",
        strategy_id=1
    )
    assert trade_strategy.strategy_id == 1


def test_trade_strategy_create_validates_timestamp_optional_default():
    """Test TradeStrategyCreate validates timestamp (optional, default '5m')."""
    # With timestamp provided
    trade_strategy_with_timestamp = TradeStrategyCreate(
        symbol="BTCUSDT",
        strategy_id=1,
        timestamp="15m"
    )
    assert trade_strategy_with_timestamp.timestamp == "15m"
    
    # Without timestamp (should default to '5m')
    trade_strategy_without_timestamp = TradeStrategyCreate(
        symbol="BTCUSDT",
        strategy_id=1
    )
    assert trade_strategy_without_timestamp.timestamp == "5m"


def test_trade_strategy_create_rejects_symbol_exceeding_15_characters():
    """Test TradeStrategyCreate rejects symbol exceeding 15 characters."""
    with pytest.raises(ValidationError) as exc_info:
        TradeStrategyCreate(
            symbol="BTCUSDTEXTRA12345",  # 18 characters
            strategy_id=1
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and (
            "max_length" in str(error["type"]).lower() or
            "max_length" in str(error.get("msg", "")).lower() or
            "string_too_long" in str(error["type"]).lower()
        )
        for error in errors
    )


def test_trade_strategy_create_accepts_symbol_at_max_length():
    """Test TradeStrategyCreate accepts symbol at max length (15 characters)."""
    symbol_15_chars = "A" * 15
    trade_strategy = TradeStrategyCreate(
        symbol=symbol_15_chars,
        strategy_id=1
    )
    assert trade_strategy.symbol == symbol_15_chars


def test_trade_strategy_update_allows_optional_symbol_strategy_id_timestamp():
    """Test TradeStrategyUpdate allows optional symbol, strategy_id, and timestamp."""
    # Update with all fields
    trade_strategy_update_all = TradeStrategyUpdate(
        symbol="ETHUSDT",
        strategy_id=2,
        timestamp="1h"
    )
    assert trade_strategy_update_all.symbol == "ETHUSDT"
    assert trade_strategy_update_all.strategy_id == 2
    assert trade_strategy_update_all.timestamp == "1h"
    
    # Update with only symbol
    trade_strategy_update_symbol = TradeStrategyUpdate(symbol="ETHUSDT")
    assert trade_strategy_update_symbol.symbol == "ETHUSDT"
    assert trade_strategy_update_symbol.strategy_id is None
    assert trade_strategy_update_symbol.timestamp is None
    
    # Update with only strategy_id
    trade_strategy_update_strategy_id = TradeStrategyUpdate(strategy_id=2)
    assert trade_strategy_update_strategy_id.symbol is None
    assert trade_strategy_update_strategy_id.strategy_id == 2
    assert trade_strategy_update_strategy_id.timestamp is None
    
    # Update with only timestamp
    trade_strategy_update_timestamp = TradeStrategyUpdate(timestamp="1h")
    assert trade_strategy_update_timestamp.symbol is None
    assert trade_strategy_update_timestamp.strategy_id is None
    assert trade_strategy_update_timestamp.timestamp == "1h"
    
    # Update with neither (empty update)
    trade_strategy_update_empty = TradeStrategyUpdate()
    assert trade_strategy_update_empty.symbol is None
    assert trade_strategy_update_empty.strategy_id is None
    assert trade_strategy_update_empty.timestamp is None


def test_trade_strategy_update_rejects_symbol_exceeding_15_characters():
    """Test TradeStrategyUpdate rejects symbol exceeding 15 characters when provided."""
    with pytest.raises(ValidationError) as exc_info:
        TradeStrategyUpdate(symbol="BTCUSDTEXTRA12345")  # 18 characters
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and (
            "max_length" in str(error["type"]).lower() or
            "max_length" in str(error.get("msg", "")).lower() or
            "string_too_long" in str(error["type"]).lower()
        )
        for error in errors
    )


def test_trade_strategy_response_includes_all_trade_strategy_fields():
    """Test TradeStrategyResponse includes all trade_strategy fields."""
    now = datetime.now()
    trade_strategy = TradeStrategyResponse(
        id=1,
        symbol="BTCUSDT",
        strategy_id=1,
        timestamp="5m",
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
    
    assert trade_strategy.id == 1
    assert trade_strategy.symbol == "BTCUSDT"
    assert trade_strategy.strategy_id == 1
    assert trade_strategy.timestamp == "5m"
    assert trade_strategy.deleted_at is None
    assert trade_strategy.created_at == now
    assert trade_strategy.updated_at == now


def test_trade_strategy_response_includes_deleted_at_when_soft_deleted():
    """Test TradeStrategyResponse includes deleted_at when trade_strategy is soft-deleted."""
    now = datetime.now()
    deleted_at = datetime.now()
    trade_strategy = TradeStrategyResponse(
        id=1,
        symbol="BTCUSDT",
        strategy_id=1,
        timestamp="5m",
        deleted_at=deleted_at,
        created_at=now,
        updated_at=now
    )
    
    assert trade_strategy.deleted_at == deleted_at
    assert isinstance(trade_strategy.deleted_at, datetime)


def test_trade_strategy_list_response_includes_trade_strategies_list():
    """Test TradeStrategyListResponse includes trade_strategies list."""
    now = datetime.now()
    trade_strategy1 = TradeStrategyResponse(
        id=1,
        symbol="BTCUSDT",
        strategy_id=1,
        timestamp="5m",
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
    
    trade_strategy2 = TradeStrategyResponse(
        id=2,
        symbol="ETHUSDT",
        strategy_id=2,
        timestamp="15m",
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
    
    trade_strategy_list = TradeStrategyListResponse(
        trade_strategies=[trade_strategy1, trade_strategy2]
    )
    
    assert len(trade_strategy_list.trade_strategies) == 2
    assert trade_strategy_list.trade_strategies[0].symbol == "BTCUSDT"
    assert trade_strategy_list.trade_strategies[1].symbol == "ETHUSDT"
    assert trade_strategy_list.trade_strategies[0].id == 1
    assert trade_strategy_list.trade_strategies[1].id == 2


def test_trade_strategy_list_response_empty_list():
    """Test TradeStrategyListResponse handles empty list correctly."""
    trade_strategy_list = TradeStrategyListResponse()
    
    assert trade_strategy_list.trade_strategies == []


def test_trade_strategy_create_rejects_missing_symbol():
    """Test TradeStrategyCreate rejects missing symbol."""
    with pytest.raises(ValidationError) as exc_info:
        TradeStrategyCreate(strategy_id=1)
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and (
            "missing" in str(error["type"]).lower() or
            "required" in str(error["type"]).lower()
        )
        for error in errors
    )


def test_trade_strategy_create_rejects_missing_strategy_id():
    """Test TradeStrategyCreate rejects missing strategy_id."""
    with pytest.raises(ValidationError) as exc_info:
        TradeStrategyCreate(symbol="BTCUSDT")
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("strategy_id",) and (
            "missing" in str(error["type"]).lower() or
            "required" in str(error["type"]).lower()
        )
        for error in errors
    )


def test_trade_strategy_create_rejects_extra_fields():
    """Test TradeStrategyCreate rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        TradeStrategyCreate(
            symbol="BTCUSDT",
            strategy_id=1,
            timestamp="5m",
            extra_field="not allowed"
        )
    
    errors = exc_info.value.errors()
    assert any(
        "extra" in str(error["type"]).lower() or "forbidden" in str(error["msg"]).lower()
        for error in errors
    )


def test_trade_strategy_response_rejects_extra_fields():
    """Test TradeStrategyResponse rejects extra fields."""
    now = datetime.now()
    with pytest.raises(ValidationError) as exc_info:
        TradeStrategyResponse(
            id=1,
            symbol="BTCUSDT",
            strategy_id=1,
            timestamp="5m",
            deleted_at=None,
            created_at=now,
            updated_at=now,
            extra_field="not allowed"
        )
    
    errors = exc_info.value.errors()
    assert any(
        "extra" in str(error["type"]).lower() or "forbidden" in str(error["msg"]).lower()
        for error in errors
    )

