from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class StrategyCreate(BaseModel):
    """Schema for creating a strategy."""
    name: str = Field(
        min_length=1,
        description="Strategy name (required)"
    )
    slug: Optional[str] = Field(
        default=None,
        description="Strategy slug (optional, auto-generated from name if not provided)"
    )

    model_config = ConfigDict(extra="forbid")


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Strategy name (optional)"
    )
    slug: Optional[str] = Field(
        default=None,
        description="Strategy slug (optional)"
    )

    model_config = ConfigDict(extra="forbid")


class StrategyResponse(BaseModel):
    """Schema for strategy response with all fields."""
    id: int
    name: str
    slug: str
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Soft delete timestamp (NULL if not deleted)"
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="forbid")


class StrategyListResponse(BaseModel):
    """Schema for strategy list response."""
    strategies: List[StrategyResponse] = Field(
        default_factory=list,
        description="List of strategies"
    )

    model_config = ConfigDict(extra="forbid")

