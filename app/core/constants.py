"""Constants for error messages and success messages.

This module provides centralized constants for consistent error and success
messages across the application. All error messages and success messages used
in API responses should be defined here.

Error Constants:
    ERROR_INSUFFICIENT_BALANCE: Error message when user balance is insufficient
    ERROR_DUPLICATE_ORDER: Error message when duplicate active order exists
    ERROR_ORDER_NOT_FOUND: Error message when order is not found
    ERROR_BINANCE_CONNECTION: Error message when Binance API connection fails
    ERROR_BINANCE_INVALID_RESPONSE: Error message when Binance API returns invalid response

Success Constants:
    SUCCESS_LOG_CREATED: Success message when log entry is created
    SUCCESS_ORDER_CLOSED: Success message when order is closed successfully
"""

# Error message constants
ERROR_INSUFFICIENT_BALANCE = "insufficient balance"
ERROR_DUPLICATE_ORDER = "rejection"
ERROR_ORDER_NOT_FOUND = "order not found"
ERROR_BINANCE_CONNECTION = "Binance API connection failed"
ERROR_BINANCE_INVALID_RESPONSE = "Invalid response from Binance API"

# Success message constants
SUCCESS_LOG_CREATED = "Log created successfully"
SUCCESS_ORDER_CLOSED = "sell order complete"

