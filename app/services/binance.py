"""Binance API integration service.

This module provides functions for interacting with the Binance API to fetch
real-time market prices. The API URL is configurable via BINANCE_API_URL setting,
allowing use of either production or testnet endpoints.

Example:
    >>> from app.services.binance import get_current_price
    >>> price = await get_current_price("BTCUSDT")
    >>> print(price)
    Decimal('50000.50')
"""

from decimal import Decimal

import httpx

from app.core.config import settings
from app.core.constants import (
    ERROR_BINANCE_CONNECTION,
    ERROR_BINANCE_INVALID_RESPONSE,
)


class BinanceAPIError(Exception):
    """Base exception for all Binance API errors."""

    pass


class BinanceConnectionError(BinanceAPIError):
    """Raised when connection to Binance API fails."""

    pass


class BinanceInvalidResponseError(BinanceAPIError):
    """Raised when Binance API returns an invalid response."""

    pass


class BinancePriceNotFoundError(BinanceAPIError):
    """Raised when price field is missing from Binance API response."""

    pass


async def get_current_price(symbol: str) -> Decimal:
    """Fetch the current market price for a trading symbol from Binance API.

    This function makes an async HTTP request to the Binance API to retrieve
    the current price for the specified trading symbol. The API URL is configured
    via BINANCE_API_URL setting.

    Args:
        symbol: Trading symbol (e.g., "BTCUSDT", "ETHUSDT"). Must be uppercase.

    Returns:
        Decimal: Current market price with full precision.

    Raises:
        BinanceConnectionError: When connection to Binance API fails (timeout,
            network errors, HTTP 503, etc.).
        BinanceInvalidResponseError: When API returns invalid response (HTTP
            error status codes, malformed JSON, etc.).
        BinancePriceNotFoundError: When price field is missing from response.

    Example:
        >>> price = await get_current_price("BTCUSDT")
        >>> print(f"Current BTC price: {price}")
        Current BTC price: 50000.50
    """
    # Construct the API endpoint URL using configured base URL
    url = f"{settings.BINANCE_API_URL}/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}

    try:
        # Use httpx.AsyncClient for async HTTP requests
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)

            # Handle HTTP error status codes
            if response.status_code >= 400:
                # Check for specific error status codes
                if response.status_code in (503, 502, 504):
                    raise BinanceConnectionError(
                        f"{ERROR_BINANCE_CONNECTION}: HTTP {response.status_code}"
                    )
                else:
                    raise BinanceInvalidResponseError(
                        f"{ERROR_BINANCE_INVALID_RESPONSE}: HTTP {response.status_code}"
                    )

            # Parse JSON response
            try:
                data = response.json()
            except ValueError as e:
                raise BinanceInvalidResponseError(
                    f"{ERROR_BINANCE_INVALID_RESPONSE}: Invalid JSON - {str(e)}"
                )

            # Check if price field exists in response
            if "price" not in data:
                raise BinancePriceNotFoundError(
                    f"Price field not found in Binance API response for symbol {symbol}"
                )

            # Convert price string to Decimal for precision
            try:
                price = Decimal(str(data["price"]))
            except (ValueError, TypeError) as e:
                raise BinanceInvalidResponseError(
                    f"{ERROR_BINANCE_INVALID_RESPONSE}: Invalid price value - {str(e)}"
                )

            return price

    except httpx.TimeoutException as e:
        raise BinanceConnectionError(
            f"{ERROR_BINANCE_CONNECTION}: Request timeout - {str(e)}"
        )
    except httpx.ConnectError as e:
        raise BinanceConnectionError(
            f"{ERROR_BINANCE_CONNECTION}: Connection failed - {str(e)}"
        )
    except httpx.RequestError as e:
        raise BinanceConnectionError(
            f"{ERROR_BINANCE_CONNECTION}: Request error - {str(e)}"
        )
    except BinanceAPIError:
        # Re-raise Binance API errors as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise BinanceInvalidResponseError(
            f"{ERROR_BINANCE_INVALID_RESPONSE}: Unexpected error - {str(e)}"
        )

