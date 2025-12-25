from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class LogCreate(BaseModel):
    """Schema for creating a log entry."""
    symbol: str = Field(
        min_length=1,
        max_length=10,
        description="Trading symbol (e.g., BTCUSDT)"
    )
    data: Dict[str, Any] = Field(
        description="Dictionary data to store as JSON"
    )
    action: str = Field(
        min_length=1,
        description="Action description (e.g., 'buy', 'sell', 'analysis')"
    )


class LogResponse(BaseModel):
    """Schema for log entry response with parsed JSON data."""
    id: int
    symbol: str
    data: Dict[str, Any] = Field(
        description="Parsed JSON data (stored as JSON text in database)"
    )
    action: str
    created_at: datetime
    updated_at: datetime

    @field_validator('data', mode='before')
    @classmethod
    def parse_json_data(cls, v: Any) -> Dict[str, Any]:
        """Parse JSON string to dict if needed."""
        import json
        if isinstance(v, str):
            return json.loads(v)
        if isinstance(v, dict):
            return v
        raise ValueError(f"data must be a dict or JSON string, got {type(v)}")

    model_config = ConfigDict(extra="forbid")


class LogListResponse(BaseModel):
    """Schema for log list response with unique symbols and pagination metadata."""
    logs: List[LogResponse] = Field(
        default_factory=list,
        description="List of log entries"
    )
    unique_symbols: List[str] = Field(
        default_factory=list,
        description="List of unique symbols from all logs"
    )
    total_count: int = Field(
        default=0,
        description="Total number of matching records (for pagination)"
    )
    limit: int = Field(
        default=100,
        description="Maximum number of records per page"
    )
    offset: int = Field(
        default=0,
        description="Number of records skipped for pagination"
    )

    model_config = ConfigDict(extra="forbid")

