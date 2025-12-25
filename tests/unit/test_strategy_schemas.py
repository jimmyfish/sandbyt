"""Unit tests for strategy schema validation.

Tests for task 16: Create strategy schemas (StrategyCreate, StrategyUpdate, StrategyResponse, StrategyListResponse).
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyListResponse
)


def test_strategy_create_validates_name_required():
    """Test StrategyCreate validates name (required)."""
    strategy = StrategyCreate(name="Momentum Strategy")
    assert strategy.name == "Momentum Strategy"
    assert strategy.slug is None


def test_strategy_create_validates_slug_optional():
    """Test StrategyCreate validates slug (optional)."""
    # With slug provided
    strategy_with_slug = StrategyCreate(
        name="Momentum Strategy",
        slug="momentum-strategy"
    )
    assert strategy_with_slug.name == "Momentum Strategy"
    assert strategy_with_slug.slug == "momentum-strategy"
    
    # Without slug (should default to None)
    strategy_without_slug = StrategyCreate(name="Momentum Strategy")
    assert strategy_without_slug.name == "Momentum Strategy"
    assert strategy_without_slug.slug is None


def test_strategy_create_rejects_empty_name():
    """Test StrategyCreate rejects empty name."""
    with pytest.raises(ValidationError) as exc_info:
        StrategyCreate(name="")
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("name",) and (
            "min_length" in str(error["type"]).lower() or
            "min_length" in str(error.get("msg", "")).lower() or
            "string_too_short" in str(error["type"]).lower()
        )
        for error in errors
    )


def test_strategy_update_allows_optional_name_and_slug():
    """Test StrategyUpdate allows optional name and slug fields."""
    # Update with both fields
    strategy_update_both = StrategyUpdate(
        name="Updated Strategy",
        slug="updated-strategy"
    )
    assert strategy_update_both.name == "Updated Strategy"
    assert strategy_update_both.slug == "updated-strategy"
    
    # Update with only name
    strategy_update_name = StrategyUpdate(name="Updated Strategy")
    assert strategy_update_name.name == "Updated Strategy"
    assert strategy_update_name.slug is None
    
    # Update with only slug
    strategy_update_slug = StrategyUpdate(slug="updated-strategy")
    assert strategy_update_slug.name is None
    assert strategy_update_slug.slug == "updated-strategy"
    
    # Update with neither (empty update)
    strategy_update_empty = StrategyUpdate()
    assert strategy_update_empty.name is None
    assert strategy_update_empty.slug is None


def test_strategy_update_rejects_empty_name():
    """Test StrategyUpdate rejects empty name when provided."""
    with pytest.raises(ValidationError) as exc_info:
        StrategyUpdate(name="")
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("name",) and (
            "min_length" in str(error["type"]).lower() or
            "min_length" in str(error.get("msg", "")).lower() or
            "string_too_short" in str(error["type"]).lower()
        )
        for error in errors
    )


def test_strategy_response_includes_all_strategy_fields():
    """Test StrategyResponse includes all strategy fields including deleted_at."""
    now = datetime.now()
    strategy = StrategyResponse(
        id=1,
        name="Momentum Strategy",
        slug="momentum-strategy",
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
    
    assert strategy.id == 1
    assert strategy.name == "Momentum Strategy"
    assert strategy.slug == "momentum-strategy"
    assert strategy.deleted_at is None
    assert strategy.created_at == now
    assert strategy.updated_at == now


def test_strategy_response_includes_deleted_at_when_soft_deleted():
    """Test StrategyResponse includes deleted_at when strategy is soft-deleted."""
    now = datetime.now()
    deleted_at = datetime.now()
    strategy = StrategyResponse(
        id=1,
        name="Momentum Strategy",
        slug="momentum-strategy",
        deleted_at=deleted_at,
        created_at=now,
        updated_at=now
    )
    
    assert strategy.deleted_at == deleted_at
    assert isinstance(strategy.deleted_at, datetime)


def test_strategy_list_response_includes_strategies_list():
    """Test StrategyListResponse includes strategies list."""
    now = datetime.now()
    strategy1 = StrategyResponse(
        id=1,
        name="Momentum Strategy",
        slug="momentum-strategy",
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
    
    strategy2 = StrategyResponse(
        id=2,
        name="Mean Reversion Strategy",
        slug="mean-reversion-strategy",
        deleted_at=None,
        created_at=now,
        updated_at=now
    )
    
    strategy_list = StrategyListResponse(
        strategies=[strategy1, strategy2]
    )
    
    assert len(strategy_list.strategies) == 2
    assert strategy_list.strategies[0].name == "Momentum Strategy"
    assert strategy_list.strategies[1].name == "Mean Reversion Strategy"
    assert strategy_list.strategies[0].id == 1
    assert strategy_list.strategies[1].id == 2


def test_strategy_list_response_empty_list():
    """Test StrategyListResponse handles empty list correctly."""
    strategy_list = StrategyListResponse()
    
    assert strategy_list.strategies == []


def test_strategy_create_name_min_length():
    """Test StrategyCreate accepts name with minimum length (1 character)."""
    strategy = StrategyCreate(name="A")
    assert strategy.name == "A"


def test_strategy_create_rejects_extra_fields():
    """Test StrategyCreate rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        StrategyCreate(
            name="Momentum Strategy",
            slug="momentum-strategy",
            extra_field="not allowed"
        )
    
    errors = exc_info.value.errors()
    assert any(
        "extra" in str(error["type"]).lower() or "forbidden" in str(error["msg"]).lower()
        for error in errors
    )


def test_strategy_response_rejects_extra_fields():
    """Test StrategyResponse rejects extra fields."""
    now = datetime.now()
    with pytest.raises(ValidationError) as exc_info:
        StrategyResponse(
            id=1,
            name="Momentum Strategy",
            slug="momentum-strategy",
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

