"""Order management router.

This module provides endpoints for creating, closing, and listing trading orders.
All endpoints require authentication via JWT token.

Endpoints:
    POST /order - Create a buy order
    DELETE /order - Close a sell order
    GET /order - List user orders
"""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.constants import (
    ERROR_DUPLICATE_ORDER,
    ERROR_INSUFFICIENT_BALANCE,
    ERROR_ORDER_NOT_FOUND,
    SUCCESS_ORDER_CLOSED,
)
from app.core.security import get_current_user
from app.db.database import (
    close_order_atomic,
    create_order_atomic,
    get_active_transaction,
    get_user_transactions,
    get_user_with_balance,
)
from app.schemas.common import StandardResponse
from app.schemas.order import OrderClose, OrderCreate, OrderListResponse, TransactionResponse
from app.services.binance import (
    BinanceAPIError,
    BinanceConnectionError,
    BinanceInvalidResponseError,
    get_current_price,
)

router = APIRouter(prefix="/order", tags=["Orders"])


def _serialize_transaction(record) -> TransactionResponse:
    """Convert an asyncpg.Record to a TransactionResponse."""
    # Calculate computed fields
    buy_price = Decimal(str(record["buy_price"]))
    quantity = Decimal(str(record["quantity"]))
    sell_price = Decimal(str(record["sell_price"])) if record["sell_price"] else None
    
    buy_aggregate = buy_price * quantity
    sell_aggregate = sell_price * quantity if sell_price else None
    diff = sell_price - buy_price if sell_price else None
    
    # diffDollar: equity if status=2, else 0
    if record["status"] == 2 and sell_price:
        diff_dollar = (sell_price - buy_price) * quantity
    else:
        diff_dollar = Decimal("0")
    
    return TransactionResponse.model_validate(
        {
            "id": record["id"],
            "symbol": record["symbol"],
            "buy_price": str(buy_price),
            "sell_price": str(sell_price) if sell_price else None,
            "status": record["status"],
            "quantity": str(quantity),
            "user_id": record["user_id"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
            "diff": str(diff) if diff else None,
            "buyAggregate": str(buy_aggregate),
            "sellAggregate": str(sell_aggregate) if sell_aggregate else None,
            "diffDollar": str(diff_dollar),
        }
    )


@router.post(
    "/",
    response_model=StandardResponse[TransactionResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    payload: OrderCreate,
    current_user=Depends(get_current_user),
):
    """Create a buy order for a trading symbol.
    
    This endpoint:
    1. Validates the symbol and quantity
    2. Fetches the current market price from Binance API
    3. Checks if user has sufficient balance
    4. Checks for duplicate active orders
    5. Creates the transaction and updates balance atomically
    
    Args:
        payload: OrderCreate schema with symbol and quantity
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with TransactionResponse containing the created order
        
    Raises:
        HTTPException 400: If balance is insufficient or duplicate order exists
        HTTPException 503: If Binance API is unavailable
        HTTPException 500: If Binance API returns invalid response or database error
    """
    user_id = current_user["id"]
    symbol = payload.symbol.upper()
    quantity = payload.quantity
    
    # Fetch current price from Binance API
    try:
        buy_price = await get_current_price(symbol)
    except BinanceConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except (BinanceInvalidResponseError, BinanceAPIError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
    # Calculate total cost
    total_cost = buy_price * quantity
    
    # Check user balance
    user = await get_user_with_balance(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user_balance = Decimal(str(user["balance"]))
    if user_balance < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_INSUFFICIENT_BALANCE,
        )
    
    # Check for duplicate active order
    existing_order = await get_active_transaction(user_id, symbol)
    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_DUPLICATE_ORDER,
        )
    
    # Create transaction and update balance atomically
    try:
        transaction = await create_order_atomic(
            user_id=user_id,
            symbol=symbol,
            buy_price=buy_price,
            quantity=quantity,
        )
    except ValueError as e:
        # Handle insufficient balance or user not found errors
        error_msg = str(e)
        if "Insufficient balance" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_INSUFFICIENT_BALANCE,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    except Exception as e:
        # Database errors (e.g., constraint violations) should be handled
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )
    
    return StandardResponse(data=_serialize_transaction(transaction))


@router.delete(
    "/",
    response_model=StandardResponse[dict],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def close_order(
    payload: OrderClose,
    current_user=Depends(get_current_user),
):
    """Close a sell order for a trading symbol.
    
    This endpoint:
    1. Validates the symbol
    2. Finds the active transaction for the user and symbol
    3. Fetches the current market price from Binance API
    4. Updates the transaction and balance atomically
    
    Args:
        payload: OrderClose schema with symbol
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with success message "sell order complete"
        
    Raises:
        HTTPException 400: If order is not found
        HTTPException 503: If Binance API is unavailable
        HTTPException 500: If Binance API returns invalid response or database error
    """
    user_id = current_user["id"]
    symbol = payload.symbol.upper()
    
    # Fetch current price from Binance API
    try:
        sell_price = await get_current_price(symbol)
    except BinanceConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except (BinanceInvalidResponseError, BinanceAPIError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
    # Close order and update balance atomically
    try:
        transaction = await close_order_atomic(
            user_id=user_id,
            symbol=symbol,
            sell_price=sell_price,
        )
    except ValueError as e:
        error_msg = str(e)
        if "No active order found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_ORDER_NOT_FOUND,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    except Exception as e:
        # Database errors should be handled
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close order: {str(e)}",
        )
    
    return StandardResponse(
        data={},
        message=SUCCESS_ORDER_CLOSED,
    )


@router.get(
    "/",
    response_model=StandardResponse[OrderListResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_orders(
    active_only: bool = False,
    symbol: str | None = None,
    current_user=Depends(get_current_user),
):
    """List user orders with optional filtering.
    
    This endpoint:
    1. Fetches all transactions for the authenticated user
    2. Optionally filters by active_only (status=1) and/or symbol
    3. Orders results by status ASC, created_at DESC
    4. Calculates computed fields (diff, buyAggregate, sellAggregate, diffDollar)
    5. Extracts unique symbols list
    
    Args:
        active_only: If True, only return active orders (status=1)
        symbol: Optional symbol to filter by
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with OrderListResponse containing:
        - orders: List of transactions with computed fields
        - unique_symbols: List of unique symbols from all orders
    """
    user_id = current_user["id"]
    
    # Normalize symbol to uppercase if provided
    if symbol:
        symbol = symbol.upper()
    
    # Fetch user transactions with filters
    transactions = await get_user_transactions(
        user_id=user_id,
        active_only=active_only,
        symbol=symbol,
    )
    
    # Serialize transactions with computed fields
    orders = [_serialize_transaction(tx) for tx in transactions]
    
    # Extract unique symbols from all user transactions (not just filtered ones)
    # We need to fetch all transactions to get unique symbols
    all_transactions = await get_user_transactions(user_id=user_id)
    unique_symbols = sorted(list(set(tx["symbol"] for tx in all_transactions)))
    
    return StandardResponse(
        data=OrderListResponse(
            orders=orders,
            unique_symbols=unique_symbols,
        )
    )

