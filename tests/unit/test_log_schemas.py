"""Unit tests for log schema validation.

Tests for task 15: Create log schemas (LogCreate, LogResponse, LogListResponse).
"""
import pytest
import json
from datetime import datetime
from pydantic import ValidationError

from app.schemas.log import (
    LogCreate,
    LogResponse,
    LogListResponse
)


def test_log_create_validates_symbol_required():
    """Test LogCreate validates symbol (required)."""
    log = LogCreate(
        symbol="BTCUSDT",
        data={"price": 50000.0, "quantity": 0.1},
        action="buy"
    )
    assert log.symbol == "BTCUSDT"
    assert log.data == {"price": 50000.0, "quantity": 0.1}
    assert log.action == "buy"


def test_log_create_validates_data_required():
    """Test LogCreate validates data (required, dict)."""
    log = LogCreate(
        symbol="BTCUSDT",
        data={"key": "value", "number": 123},
        action="analysis"
    )
    assert isinstance(log.data, dict)
    assert log.data["key"] == "value"
    assert log.data["number"] == 123


def test_log_create_validates_action_required():
    """Test LogCreate validates action (required)."""
    log = LogCreate(
        symbol="BTCUSDT",
        data={"test": "data"},
        action="sell"
    )
    assert log.action == "sell"


def test_log_create_rejects_missing_symbol():
    """Test LogCreate rejects missing symbol field."""
    with pytest.raises(ValidationError) as exc_info:
        LogCreate(
            data={"test": "data"},
            action="buy"
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "missing"
        for error in errors
    )


def test_log_create_rejects_missing_data():
    """Test LogCreate rejects missing data field."""
    with pytest.raises(ValidationError) as exc_info:
        LogCreate(
            symbol="BTCUSDT",
            action="buy"
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("data",) and error["type"] == "missing"
        for error in errors
    )


def test_log_create_rejects_missing_action():
    """Test LogCreate rejects missing action field."""
    with pytest.raises(ValidationError) as exc_info:
        LogCreate(
            symbol="BTCUSDT",
            data={"test": "data"}
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("action",) and error["type"] == "missing"
        for error in errors
    )


def test_log_create_rejects_empty_symbol():
    """Test LogCreate rejects empty symbol."""
    with pytest.raises(ValidationError) as exc_info:
        LogCreate(
            symbol="",
            data={"test": "data"},
            action="buy"
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_short"
        for error in errors
    )


def test_log_create_rejects_empty_action():
    """Test LogCreate rejects empty action."""
    with pytest.raises(ValidationError) as exc_info:
        LogCreate(
            symbol="BTCUSDT",
            data={"test": "data"},
            action=""
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("action",) and error["type"] == "string_too_short"
        for error in errors
    )


def test_log_response_includes_all_fields():
    """Test LogResponse includes id, symbol, data (parsed JSON), action, created_at, updated_at."""
    log = LogResponse(
        id=1,
        symbol="BTCUSDT",
        data={"price": 50000.0, "quantity": 0.1},
        action="buy",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert log.id == 1
    assert log.symbol == "BTCUSDT"
    assert isinstance(log.data, dict)
    assert log.data["price"] == 50000.0
    assert log.data["quantity"] == 0.1
    assert log.action == "buy"
    assert isinstance(log.created_at, datetime)
    assert isinstance(log.updated_at, datetime)


def test_log_response_parses_json_string_data():
    """Test LogResponse parses JSON string data field correctly."""
    json_data = json.dumps({"price": 50000.0, "quantity": 0.1})
    
    log = LogResponse(
        id=1,
        symbol="BTCUSDT",
        data=json_data,  # Pass as JSON string
        action="buy",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert isinstance(log.data, dict)
    assert log.data["price"] == 50000.0
    assert log.data["quantity"] == 0.1


def test_log_response_accepts_dict_data():
    """Test LogResponse accepts dict data directly."""
    log = LogResponse(
        id=1,
        symbol="BTCUSDT",
        data={"price": 50000.0, "quantity": 0.1},  # Pass as dict
        action="buy",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert isinstance(log.data, dict)
    assert log.data["price"] == 50000.0


def test_log_response_rejects_invalid_json_string():
    """Test LogResponse rejects invalid JSON string in data field."""
    with pytest.raises(ValidationError) as exc_info:
        LogResponse(
            id=1,
            symbol="BTCUSDT",
            data="invalid json string {",  # Invalid JSON
            action="buy",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    errors = exc_info.value.errors()
    # Should have validation error for data field
    assert any(
        error["loc"] == ("data",)
        for error in errors
    )


def test_log_list_response_includes_logs_list():
    """Test LogListResponse includes logs list, unique_symbols, and pagination metadata."""
    log1 = LogResponse(
        id=1,
        symbol="BTCUSDT",
        data={"price": 50000.0},
        action="buy",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    log2 = LogResponse(
        id=2,
        symbol="ETHUSDT",
        data={"price": 3000.0},
        action="sell",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    log_list = LogListResponse(
        logs=[log1, log2],
        unique_symbols=["BTCUSDT", "ETHUSDT"],
        total_count=2,
        limit=100,
        offset=0
    )
    
    assert len(log_list.logs) == 2
    assert log_list.logs[0].symbol == "BTCUSDT"
    assert log_list.logs[1].symbol == "ETHUSDT"
    assert len(log_list.unique_symbols) == 2
    assert "BTCUSDT" in log_list.unique_symbols
    assert "ETHUSDT" in log_list.unique_symbols
    assert log_list.total_count == 2
    assert log_list.limit == 100
    assert log_list.offset == 0


def test_log_list_response_includes_pagination_metadata():
    """Test LogListResponse includes pagination metadata (total_count, limit, offset)."""
    log_list = LogListResponse(
        logs=[],
        unique_symbols=[],
        total_count=50,
        limit=10,
        offset=20
    )
    
    assert log_list.total_count == 50
    assert log_list.limit == 10
    assert log_list.offset == 20


def test_log_list_response_default_values():
    """Test LogListResponse has correct default values."""
    log_list = LogListResponse()
    
    assert log_list.logs == []
    assert log_list.unique_symbols == []
    assert log_list.total_count == 0
    assert log_list.limit == 100
    assert log_list.offset == 0


def test_log_response_data_field_serialization():
    """Test data field is properly serialized/deserialized as JSON."""
    # Test with complex nested data
    complex_data = {
        "price": 50000.0,
        "quantity": 0.1,
        "metadata": {
            "source": "binance",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "array": [1, 2, 3]
    }
    
    log = LogResponse(
        id=1,
        symbol="BTCUSDT",
        data=complex_data,
        action="buy",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Verify data is preserved correctly
    assert log.data == complex_data
    assert log.data["metadata"]["source"] == "binance"
    assert log.data["array"] == [1, 2, 3]
    
    # Test serialization to JSON
    log_dict = log.model_dump()
    assert isinstance(log_dict["data"], dict)
    assert log_dict["data"]["price"] == 50000.0


def test_log_response_parses_json_string_with_nested_data():
    """Test LogResponse parses JSON string with nested data structures."""
    nested_json = json.dumps({
        "price": 50000.0,
        "metadata": {
            "source": "binance",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "array": [1, 2, 3]
    })
    
    log = LogResponse(
        id=1,
        symbol="BTCUSDT",
        data=nested_json,
        action="buy",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert isinstance(log.data, dict)
    assert log.data["price"] == 50000.0
    assert isinstance(log.data["metadata"], dict)
    assert log.data["metadata"]["source"] == "binance"
    assert isinstance(log.data["array"], list)
    assert log.data["array"] == [1, 2, 3]


def test_log_create_symbol_max_length_boundary():
    """Test LogCreate accepts symbol at exactly 10 characters."""
    log = LogCreate(
        symbol="1234567890",  # Exactly 10 characters
        data={"test": "data"},
        action="buy"
    )
    assert log.symbol == "1234567890"


def test_log_create_symbol_exceeds_max_length():
    """Test LogCreate rejects symbol exceeding 10 characters."""
    with pytest.raises(ValidationError) as exc_info:
        LogCreate(
            symbol="BTCUSDTEXTRA",  # 13 characters
            data={"test": "data"},
            action="buy"
        )
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_long"
        for error in errors
    )

