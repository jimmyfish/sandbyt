"""Unit tests for constants module.

Tests for task 5: Create constants module for error messages.
"""
import pytest

from app.core import constants


def test_all_error_constants_are_defined():
    """Test all error constants are defined."""
    assert hasattr(constants, "ERROR_INSUFFICIENT_BALANCE")
    assert hasattr(constants, "ERROR_DUPLICATE_ORDER")
    assert hasattr(constants, "ERROR_ORDER_NOT_FOUND")
    assert hasattr(constants, "ERROR_BINANCE_CONNECTION")
    assert hasattr(constants, "ERROR_BINANCE_INVALID_RESPONSE")


def test_all_success_constants_are_defined():
    """Test all success constants are defined."""
    assert hasattr(constants, "SUCCESS_LOG_CREATED")
    assert hasattr(constants, "SUCCESS_ORDER_CLOSED")


def test_error_constants_are_string_values():
    """Test constants are string values (not None)."""
    assert constants.ERROR_INSUFFICIENT_BALANCE is not None
    assert isinstance(constants.ERROR_INSUFFICIENT_BALANCE, str)
    
    assert constants.ERROR_DUPLICATE_ORDER is not None
    assert isinstance(constants.ERROR_DUPLICATE_ORDER, str)
    
    assert constants.ERROR_ORDER_NOT_FOUND is not None
    assert isinstance(constants.ERROR_ORDER_NOT_FOUND, str)
    
    assert constants.ERROR_BINANCE_CONNECTION is not None
    assert isinstance(constants.ERROR_BINANCE_CONNECTION, str)
    
    assert constants.ERROR_BINANCE_INVALID_RESPONSE is not None
    assert isinstance(constants.ERROR_BINANCE_INVALID_RESPONSE, str)


def test_success_constants_are_string_values():
    """Test success constants are string values (not None)."""
    assert constants.SUCCESS_LOG_CREATED is not None
    assert isinstance(constants.SUCCESS_LOG_CREATED, str)
    
    assert constants.SUCCESS_ORDER_CLOSED is not None
    assert isinstance(constants.SUCCESS_ORDER_CLOSED, str)


def test_constants_can_be_imported_from_app_core_constants():
    """Test constants can be imported from app.core.constants."""
    from app.core.constants import (
        ERROR_INSUFFICIENT_BALANCE,
        ERROR_DUPLICATE_ORDER,
        ERROR_ORDER_NOT_FOUND,
        ERROR_BINANCE_CONNECTION,
        ERROR_BINANCE_INVALID_RESPONSE,
        SUCCESS_LOG_CREATED,
        SUCCESS_ORDER_CLOSED,
    )
    
    assert ERROR_INSUFFICIENT_BALANCE == "insufficient balance"
    assert ERROR_DUPLICATE_ORDER == "rejection"
    assert ERROR_ORDER_NOT_FOUND == "order not found"
    assert ERROR_BINANCE_CONNECTION == "Binance API connection failed"
    assert ERROR_BINANCE_INVALID_RESPONSE == "Invalid response from Binance API"
    assert SUCCESS_LOG_CREATED == "Log created successfully"
    assert SUCCESS_ORDER_CLOSED == "sell order complete"


def test_error_constants_have_correct_values():
    """Test error constants have the correct values as per requirements."""
    assert constants.ERROR_INSUFFICIENT_BALANCE == "insufficient balance"
    assert constants.ERROR_DUPLICATE_ORDER == "rejection"
    assert constants.ERROR_ORDER_NOT_FOUND == "order not found"
    assert constants.ERROR_BINANCE_CONNECTION == "Binance API connection failed"
    assert constants.ERROR_BINANCE_INVALID_RESPONSE == "Invalid response from Binance API"


def test_success_constants_have_correct_values():
    """Test success constants have the correct values as per requirements."""
    assert constants.SUCCESS_LOG_CREATED == "Log created successfully"
    assert constants.SUCCESS_ORDER_CLOSED == "sell order complete"

