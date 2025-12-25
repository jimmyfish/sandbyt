from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TradeStrategyCreate(BaseModel):
    """Schema for creating a trade strategy."""
    symbol: str = Field(
        max_length=15,
        description="Trading symbol (required, max 15 characters)"
    )
    strategy_id: int = Field(
        description="Strategy ID (required, must exist in strategies table)"
    )
    timestamp: Optional[str] = Field(
        default="5m",
        description="Timestamp interval (optional, defaults to '5m')"
    )

    model_config = ConfigDict(extra="forbid")


class TradeStrategyUpdate(BaseModel):
    """Schema for updating a trade strategy."""
    symbol: Optional[str] = Field(
        default=None,
        max_length=15,
        description="Trading symbol (optional, max 15 characters)"
    )
    strategy_id: Optional[int] = Field(
        default=None,
        description="Strategy ID (optional, must exist in strategies table)"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp interval (optional)"
    )

    model_config = ConfigDict(extra="forbid")


class TradeStrategyResponse(BaseModel):
    """Schema for trade strategy response with all fields."""
    id: int
    symbol: str
    strategy_id: int
    timestamp: str
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Soft delete timestamp (NULL if not deleted)"
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        extra="forbid",
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class TradeStrategyListResponse(BaseModel):
    """Schema for trade strategy list response."""
    trade_strategies: List[TradeStrategyResponse] = Field(
        default_factory=list,
        description="List of trade strategies"
    )

    model_config = ConfigDict(extra="forbid")

