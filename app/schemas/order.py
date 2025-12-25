from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class OrderCreate(BaseModel):
    """Schema for creating a buy order."""
    symbol: str = Field(
        min_length=1,
        max_length=10,
        description="Trading symbol (e.g., BTCUSDT)"
    )
    quantity: Decimal = Field(
        gt=0,
        description="Quantity of the asset to buy (must be positive)"
    )


class OrderClose(BaseModel):
    """Schema for closing a sell order."""
    symbol: str = Field(
        min_length=1,
        max_length=10,
        description="Trading symbol (e.g., BTCUSDT)"
    )


class TransactionResponse(BaseModel):
    """Schema for transaction/order response with computed fields.
    
    All decimal fields are represented as strings to preserve precision
    in JSON serialization, consistent with UserResponse.balance pattern.
    """
    id: int
    symbol: str
    buy_price: str = Field(description="Buy price as string to preserve precision")
    sell_price: Optional[str] = Field(
        default=None,
        description="Sell price as string (NULL if not sold)"
    )
    status: int
    quantity: str = Field(description="Quantity as string to preserve precision")
    user_id: int
    created_at: datetime
    updated_at: datetime
    # Computed fields
    diff: Optional[str] = Field(
        default=None,
        description="sell_price - buy_price as string (NULL if sell_price is NULL)"
    )
    buyAggregate: str = Field(
        description="buy_price * quantity as string"
    )
    sellAggregate: Optional[str] = Field(
        default=None,
        description="sell_price * quantity as string (NULL if sell_price is NULL)"
    )
    diffDollar: str = Field(
        default="0",
        description="Equity as string if status=2, else '0'"
    )

    model_config = ConfigDict(
        extra="forbid"
    )


class OrderListResponse(BaseModel):
    """Schema for order list response with unique symbols."""
    orders: List[TransactionResponse] = Field(
        default_factory=list,
        description="List of user orders/transactions"
    )
    unique_symbols: List[str] = Field(
        default_factory=list,
        description="List of unique symbols from all orders"
    )

    model_config = ConfigDict(extra="forbid")

