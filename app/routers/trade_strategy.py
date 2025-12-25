"""Trade strategy management router.

This module provides endpoints for managing trade strategies (symbol-strategy mappings).
All endpoints require authentication via JWT token.

Endpoints:
    GET /trade-strategy - List all trade strategies (including soft-deleted by default)
    POST /trade-strategy - Create a new trade strategy
    PUT /trade-strategy/{trade_strategy_id} - Update a trade strategy
    DELETE /trade-strategy/{trade_strategy_id} - Soft delete a trade strategy
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
import asyncpg

from app.core.security import get_current_user
from app.db.database import (
    create_trade_strategy,
    get_trade_strategies,
    get_trade_strategy_by_id,
    soft_delete_trade_strategy,
    update_trade_strategy,
)
from app.schemas.common import StandardResponse
from app.schemas.trade_strategy import (
    TradeStrategyCreate,
    TradeStrategyListResponse,
    TradeStrategyResponse,
    TradeStrategyUpdate,
)

router = APIRouter(prefix="/trade-strategy", tags=["Trade Strategy"])


def _serialize_trade_strategy(record) -> TradeStrategyResponse:
    """Convert an asyncpg.Record to a TradeStrategyResponse."""
    return TradeStrategyResponse.model_validate(
        {
            "id": record["id"],
            "symbol": record["symbol"],
            "strategy_id": record["strategy_id"],
            "timestamp": record["timestamp"],
            "deleted_at": record["deleted_at"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }
    )


@router.get(
    "/",
    response_model=StandardResponse[TradeStrategyListResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def list_trade_strategies(
    include_deleted: bool = Query(
        default=True,
        description="Include soft-deleted trade strategies in results (default: True)"
    ),
    current_user=Depends(get_current_user),
):
    """List all trade strategies.
    
    This endpoint returns all trade strategies, optionally including soft-deleted ones.
    Results are ordered by created_at DESC.
    
    Args:
        include_deleted: If True, include soft-deleted trade strategies (default: True)
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with TradeStrategyListResponse containing:
        - trade_strategies: List of trade strategy entries
    """
    trade_strategy_records = await get_trade_strategies(include_deleted=include_deleted)
    
    # Serialize trade strategy records
    trade_strategies = [_serialize_trade_strategy(record) for record in trade_strategy_records]
    
    return StandardResponse(
        data=TradeStrategyListResponse(trade_strategies=trade_strategies)
    )


@router.post(
    "/",
    response_model=StandardResponse[TradeStrategyResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_trade_strategy_entry(
    payload: TradeStrategyCreate,
    current_user=Depends(get_current_user),
):
    """Create a new trade strategy.
    
    This endpoint creates a new trade strategy mapping with symbol, strategy_id, and optional timestamp.
    If timestamp is not provided, it defaults to '5m'.
    
    Args:
        payload: TradeStrategyCreate schema with symbol, strategy_id, and optional timestamp
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with TradeStrategyResponse containing the created trade strategy
        
    Raises:
        HTTPException 400: If strategy_id does not exist (foreign key constraint violation)
        HTTPException 422: If validation fails (handled by Pydantic)
        HTTPException 500: If database error occurs
    """
    try:
        record = await create_trade_strategy(
            symbol=payload.symbol,
            strategy_id=payload.strategy_id,
            timestamp=payload.timestamp
        )
    except asyncpg.ForeignKeyViolationError as e:
        # Foreign key constraint violation (strategy_id does not exist)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strategy with id {payload.strategy_id} does not exist",
        )
    except Exception as e:
        # Handle other database errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trade strategy: {str(e)}",
        )
    
    return StandardResponse(data=_serialize_trade_strategy(record))


@router.put(
    "/{trade_strategy_id}",
    response_model=StandardResponse[TradeStrategyResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def update_trade_strategy_entry(
    trade_strategy_id: int,
    payload: TradeStrategyUpdate,
    current_user=Depends(get_current_user),
):
    """Update a trade strategy.
    
    This endpoint updates a trade strategy's symbol, strategy_id, and/or timestamp.
    
    Args:
        trade_strategy_id: Trade strategy ID to update
        payload: TradeStrategyUpdate schema with optional symbol, strategy_id, and timestamp
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with TradeStrategyResponse containing the updated trade strategy
        
    Raises:
        HTTPException 400: If strategy_id does not exist (foreign key constraint violation)
        HTTPException 404: If trade strategy not found
        HTTPException 422: If validation fails (handled by Pydantic)
        HTTPException 500: If database error occurs
    """
    try:
        record = await update_trade_strategy(
            trade_strategy_id=trade_strategy_id,
            symbol=payload.symbol,
            strategy_id=payload.strategy_id,
            timestamp=payload.timestamp
        )
    except ValueError as e:
        # Trade strategy not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except asyncpg.ForeignKeyViolationError as e:
        # Foreign key constraint violation (strategy_id does not exist)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strategy with id {payload.strategy_id} does not exist",
        )
    except Exception as e:
        # Handle other database errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update trade strategy: {str(e)}",
        )
    
    return StandardResponse(data=_serialize_trade_strategy(record))


@router.delete(
    "/{trade_strategy_id}",
    response_model=StandardResponse[dict],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def delete_trade_strategy_entry(
    trade_strategy_id: int,
    current_user=Depends(get_current_user),
):
    """Soft delete a trade strategy.
    
    This endpoint soft deletes a trade strategy by setting the deleted_at timestamp.
    The record is not removed from the database.
    
    Args:
        trade_strategy_id: Trade strategy ID to soft delete
        current_user: Authenticated user record from JWT token
        
    Returns:
        StandardResponse with success message
        
    Raises:
        HTTPException 404: If trade strategy not found
        HTTPException 500: If database error occurs
    """
    try:
        record = await soft_delete_trade_strategy(trade_strategy_id)
    except ValueError as e:
        # Trade strategy not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Handle other database errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete trade strategy: {str(e)}",
        )
    
    return StandardResponse(
        data={},
        message=f"Trade strategy '{record['symbol']}' soft deleted successfully",
    )

