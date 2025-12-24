"""Unit tests for user schema validation.

Tests for task 2: Extend user schema with name and balance fields.
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserResponse


def test_user_create_accepts_name_field():
    """Test UserCreate accepts name field (required)."""
    user = UserCreate(
        email="test@example.com",
        password="password123",
        name="Test User"
    )
    assert user.name == "Test User"
    assert user.email == "test@example.com"


def test_user_create_rejects_missing_name_field():
    """Test UserCreate rejects missing name field."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="password123"
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("name",) for error in errors)


def test_user_create_rejects_empty_name_field():
    """Test name field validation (required, non-empty)."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="password123",
            name=""
        )
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("name",) for error in errors)


def test_user_response_includes_name_and_balance_fields():
    """Test UserResponse includes name and balance fields."""
    from datetime import datetime
    
    user_response = UserResponse(
        id=1,
        email="test@example.com",
        name="Test User",
        balance=Decimal("100.50"),
        created_at=datetime.now()
    )
    
    assert user_response.name == "Test User"
    assert user_response.balance == Decimal("100.50")
    assert isinstance(user_response.balance, Decimal)


def test_user_response_balance_uses_decimal_type():
    """Test balance field uses Decimal type for precision."""
    from datetime import datetime
    
    # Test with high precision value
    balance_value = Decimal("0.00000000000000000000")
    user_response = UserResponse(
        id=1,
        email="test@example.com",
        name="Test User",
        balance=balance_value,
        created_at=datetime.now()
    )
    
    assert isinstance(user_response.balance, Decimal)
    assert user_response.balance == Decimal("0.00000000000000000000")


def test_user_response_balance_precision():
    """Test balance field maintains DECIMAL(30,20) precision."""
    from datetime import datetime
    
    # Test with maximum precision value
    high_precision = Decimal("12345678901234567890.12345678901234567890")
    user_response = UserResponse(
        id=1,
        email="test@example.com",
        name="Test User",
        balance=high_precision,
        created_at=datetime.now()
    )
    
    assert user_response.balance == high_precision
    assert isinstance(user_response.balance, Decimal)

