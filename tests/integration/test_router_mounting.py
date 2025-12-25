"""Integration tests for router mounting.

Tests for task 25: Mount all new routers in main.py.

This test suite validates that all routers are properly mounted and accessible
via the API, and that they appear in OpenAPI documentation.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client for endpoint testing."""
    return TestClient(app)


def test_order_router_is_mounted_and_accessible(client):
    """Test order router is mounted and accessible at /order endpoints."""
    # Test that the order router is accessible (will return 401 without auth, but that's expected)
    response = client.get("/order")
    # Should return 401 (unauthorized) not 404 (not found), proving router is mounted
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify POST endpoint exists
    response = client.post("/order", json={"symbol": "BTCUSDT", "quantity": "0.1"})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify DELETE endpoint exists by checking OpenAPI schema
    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == status.HTTP_200_OK
    openapi_schema = openapi_response.json()
    paths = openapi_schema.get("paths", {})
    # Check if any path starts with /order
    order_paths = [path for path in paths.keys() if path.startswith("/order")]
    assert len(order_paths) > 0, f"Order router paths not found in OpenAPI schema. Available paths: {list(paths.keys())[:10]}"
    # Check if DELETE method exists in any order path
    has_delete = any("delete" in paths[path] for path in order_paths)
    assert has_delete, "DELETE method not found for /order endpoints"


def test_watchlist_router_is_mounted_and_accessible(client):
    """Test watchlist router is mounted and accessible at /watchlist endpoints."""
    # Test that the watchlist router is accessible
    response = client.get("/watchlist")
    # Should return 401 (unauthorized) not 404 (not found), proving router is mounted
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify POST endpoint exists
    response = client.post("/watchlist", json={"symbol": "BTCUSDT"})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify DELETE endpoint exists
    response = client.delete("/watchlist/BTCUSDT")
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


def test_log_router_is_mounted_and_accessible(client):
    """Test log router is mounted and accessible at /log endpoints."""
    # Test that the log router is accessible
    response = client.get("/log")
    # Should return 401 (unauthorized) not 404 (not found), proving router is mounted
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify POST endpoint exists
    response = client.post("/log", json={"symbol": "BTCUSDT", "data": {}, "action": "test"})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_strategy_router_is_mounted_and_accessible(client):
    """Test strategy router is mounted and accessible at /strategy endpoints."""
    # Test that the strategy router is accessible
    response = client.get("/strategy")
    # Should return 401 (unauthorized) not 404 (not found), proving router is mounted
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify POST endpoint exists
    response = client.post("/strategy", json={"name": "Test Strategy"})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify PUT endpoint exists
    response = client.put("/strategy/1", json={"name": "Updated Strategy"})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify DELETE endpoint exists
    response = client.delete("/strategy/1")
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_trade_strategy_router_is_mounted_and_accessible(client):
    """Test trade_strategy router is mounted and accessible at /trade-strategy endpoints."""
    # Test that the trade_strategy router is accessible
    response = client.get("/trade-strategy")
    # Should return 401 (unauthorized) not 404 (not found), proving router is mounted
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify POST endpoint exists
    response = client.post("/trade-strategy", json={"symbol": "BTCUSDT", "strategy_id": 1})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify PUT endpoint exists
    response = client.put("/trade-strategy/1", json={"symbol": "ETHUSDT"})
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    # Verify DELETE endpoint exists
    response = client.delete("/trade-strategy/1")
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_all_routers_appear_in_openapi_documentation(client):
    """Test all routers appear in OpenAPI documentation (/docs)."""
    # Fetch OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    
    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})
    
    # Verify all router paths exist in OpenAPI schema
    router_paths = [
        "/order",
        "/watchlist",
        "/log",
        "/strategy",
        "/trade-strategy",
    ]
    
    for router_path in router_paths:
        # Check if any path starts with the router prefix
        found = any(path.startswith(router_path) for path in paths.keys())
        assert found, f"Router path '{router_path}' not found in OpenAPI schema. Available paths: {list(paths.keys())}"


def test_router_tags_are_properly_set_in_openapi_documentation(client):
    """Test router tags are properly set for API documentation grouping."""
    # Fetch OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    
    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})
    
    # Verify that paths are tagged correctly
    # Check a sample path from each router
    path_tag_mapping = {
        "/order": "Orders",
        "/watchlist": "Watchlist",
        "/log": "Log",
        "/strategy": "Strategy",
        "/trade-strategy": "Trade Strategy",
    }
    
    for path_prefix, expected_tag in path_tag_mapping.items():
        # Find a path that starts with the prefix
        matching_paths = [path for path in paths.keys() if path.startswith(path_prefix)]
        assert len(matching_paths) > 0, f"No paths found for router prefix '{path_prefix}'"
        
        # Check the first matching path
        sample_path = matching_paths[0]
        path_info = paths[sample_path]
        # Get tags from any HTTP method in the path
        path_tags = []
        for method_info in path_info.values():
            if isinstance(method_info, dict) and "tags" in method_info:
                path_tags.extend(method_info["tags"])
        
        assert expected_tag in path_tags, (
            f"Path '{sample_path}' should have tag '{expected_tag}'. "
            f"Found tags: {path_tags}. Path info: {path_info}"
        )

