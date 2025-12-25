"""Unit tests for watchlist schema validation.

Tests for task 14: Create watchlist schemas (WatchlistCreate, WatchlistResponse, WatchlistListResponse).
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistResponse,
    WatchlistListResponse
)


def test_watchlist_create_validates_symbol_required():
    """Test WatchlistCreate validates symbol (required, max 10 chars)."""
    watchlist = WatchlistCreate(symbol="BTCUSDT")
    assert watchlist.symbol == "BTCUSDT"


def test_watchlist_create_rejects_symbol_exceeding_10_characters():
    """Test WatchlistCreate rejects symbol exceeding 10 characters."""
    with pytest.raises(ValidationError) as exc_info:
        WatchlistCreate(symbol="BTCUSDTEXTRA")  # 13 characters
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_long"
        for error in errors
    )


def test_watchlist_response_includes_id_symbol_created_at():
    """Test WatchlistResponse includes id, symbol, created_at."""
    watchlist = WatchlistResponse(
        id=1,
        symbol="BTCUSDT",
        created_at=datetime.now()
    )
    
    assert watchlist.id == 1
    assert watchlist.symbol == "BTCUSDT"
    assert isinstance(watchlist.created_at, datetime)


def test_watchlist_list_response_includes_watchlists_list():
    """Test WatchlistListResponse includes watchlists list and unique_symbols."""
    watchlist1 = WatchlistResponse(
        id=1,
        symbol="BTCUSDT",
        created_at=datetime.now()
    )
    
    watchlist2 = WatchlistResponse(
        id=2,
        symbol="ETHUSDT",
        created_at=datetime.now()
    )
    
    watchlist_list = WatchlistListResponse(
        watchlists=[watchlist1, watchlist2],
        unique_symbols=["BTCUSDT", "ETHUSDT"]
    )
    
    assert len(watchlist_list.watchlists) == 2
    assert watchlist_list.watchlists[0].symbol == "BTCUSDT"
    assert watchlist_list.watchlists[1].symbol == "ETHUSDT"
    assert len(watchlist_list.unique_symbols) == 2
    assert "BTCUSDT" in watchlist_list.unique_symbols
    assert "ETHUSDT" in watchlist_list.unique_symbols


def test_watchlist_list_response_empty_lists():
    """Test WatchlistListResponse handles empty lists correctly."""
    watchlist_list = WatchlistListResponse()
    
    assert watchlist_list.watchlists == []
    assert watchlist_list.unique_symbols == []


def test_watchlist_create_symbol_max_length_boundary():
    """Test WatchlistCreate accepts symbol at exactly 10 characters."""
    watchlist = WatchlistCreate(symbol="1234567890")  # Exactly 10 characters
    assert watchlist.symbol == "1234567890"


def test_watchlist_create_symbol_min_length():
    """Test WatchlistCreate accepts symbol with minimum length (1 character)."""
    watchlist = WatchlistCreate(symbol="A")
    assert watchlist.symbol == "A"


def test_watchlist_create_rejects_empty_symbol():
    """Test WatchlistCreate rejects empty symbol."""
    with pytest.raises(ValidationError) as exc_info:
        WatchlistCreate(symbol="")
    
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("symbol",) and error["type"] == "string_too_short"
        for error in errors
    )

