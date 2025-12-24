"""Unit tests for configuration settings.

Tests for task 4: Extend configuration with Binance API settings.
"""
import os
import pytest
from unittest.mock import patch

from app.core.config import Settings


def test_binance_api_url_defaults():
    """Test BINANCE_API_URL defaults to 'https://api.binance.com'."""
    # Create a new Settings instance without environment overrides
    with patch.dict(os.environ, {}, clear=True):
        # Clear any existing env vars that might affect the test
        os.environ.pop("BINANCE_API_URL", None)
        
        settings = Settings()
        assert settings.BINANCE_API_URL == "https://api.binance.com"
        assert isinstance(settings.BINANCE_API_URL, str)


def test_settings_can_be_overridden_via_env_vars():
    """Test settings can be overridden via environment variables."""
    with patch.dict(
        os.environ,
        {
            "BINANCE_API_URL": "https://custom-api.example.com",
        },
        clear=False,
    ):
        settings = Settings()
        assert settings.BINANCE_API_URL == "https://custom-api.example.com"


def test_settings_are_type_safe():
    """Test settings are type-safe (str for URL)."""
    with patch.dict(
        os.environ,
        {
            "BINANCE_API_URL": "https://api.example.com",
        },
        clear=False,
    ):
        settings = Settings()
        
        # Test URL field is string
        assert isinstance(settings.BINANCE_API_URL, str)
        assert settings.BINANCE_API_URL == "https://api.example.com"


def test_binance_api_url_can_use_testnet():
    """Test that BINANCE_API_URL can be configured to use testnet."""
    with patch.dict(
        os.environ,
        {
            "BINANCE_API_URL": "https://testnet.binance.vision",
        },
        clear=False,
    ):
        settings = Settings()
        assert settings.BINANCE_API_URL == "https://testnet.binance.vision"
        assert isinstance(settings.BINANCE_API_URL, str)
