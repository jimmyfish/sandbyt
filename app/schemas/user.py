from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=1, description="User's full name")


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


def _format_decimal(value: Decimal) -> str:
    """Format Decimal to string preserving full precision without scientific notation.
    
    DECIMAL(30,20) means 30 total digits, 20 after decimal point.
    This formats the decimal to always show the full precision.
    """
    # Use format specifier to avoid scientific notation
    # f format with 20 decimal places matches DECIMAL(30,20) scale
    return f"{value:.20f}"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    # Represented as string to preserve precision (stored as NUMERIC in Postgres).
    # Accepts Decimal and converts to string during validation.
    balance: str = Field(min_length=1)
    created_at: datetime

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Override to convert Decimal balance to string before validation."""
        if hasattr(obj, "__getitem__"):
            # Handle dict-like objects (including asyncpg.Record)
            if "balance" in obj and isinstance(obj.get("balance"), Decimal):
                # Convert to mutable dict and update balance
                obj_dict = dict(obj)
                obj_dict["balance"] = _format_decimal(obj["balance"])
                return super().model_validate(obj_dict, **kwargs)
        return super().model_validate(obj, **kwargs)

    def __init__(self, **data):
        """Convert Decimal balance to string during initialization."""
        if "balance" in data and isinstance(data["balance"], Decimal):
            data["balance"] = _format_decimal(data["balance"])
        super().__init__(**data)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class LoginResponse(TokenResponse):
    user: UserResponse
