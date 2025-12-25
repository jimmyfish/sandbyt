# Product Overview: goblin API

## Product Description

goblin is a FastAPI-based REST API service that provides a complete trading sandbox platform with user authentication, order management, market data integration, and strategy management. It serves as a Python-native trading infrastructure that enables seamless integration with data science tooling (numpy, pandas) for research team workflows.

The application has been migrated from a PHP Laravel-based Binance Sandbox to provide Python-native capabilities while preserving all existing trading functionality.

## Core Features

### Authentication & User Management
- **User Registration**: Create new user accounts with email and password validation
- **User Authentication**: Secure login with JWT token-based authentication
- **User Profile Management**: Retrieve authenticated user profile information including balance
- **Balance Management**: User balance tracking with atomic transaction support

### Trading Operations
- **Order Management**: Create buy orders and close sell orders with atomic database transactions
- **Transaction Tracking**: Full transaction history with computed fields (profit/loss, aggregates)
- **Balance Operations**: Atomic balance updates during order creation and closure
- **Duplicate Prevention**: Prevents duplicate active orders for the same symbol per user

### Market Data Integration
- **Bybit Integration**: Real-time market price fetching from Bybit API (supports testnet and mainnet)
- **Price Queries**: Query current symbol prices across different market categories (spot, linear, inverse, option)
- **Market Category Support**: Flexible market category selection for price queries

### Watchlist Management
- **Symbol Tracking**: Add trading symbols to watchlist for monitoring
- **Watchlist Operations**: Create, list, and delete watchlist entries
- **Symbol Management**: Track symbols of interest across the platform

### Strategy Management
- **Strategy CRUD**: Create, read, update, and soft-delete trading strategies
- **Strategy Slugs**: Auto-generated URL-friendly slugs for strategies
- **Trade Strategy Mapping**: Link trading symbols to specific strategies with time intervals
- **Soft Deletion**: Strategies and trade strategies support soft deletion (deleted_at timestamp)

### Logging & Observability
- **Trading Logs**: Store trading actions and analysis data as JSON
- **Log Filtering**: Filter logs by symbol with LIKE pattern matching
- **Log Pagination**: Paginated log retrieval with offset/limit support
- **Symbol Discovery**: Get unique symbols from log entries

### System Features
- **Health Monitoring**: Health check endpoint for API and database connectivity monitoring
- **Database Migrations**: Flyway-based versioned database migrations with checksum verification
- **Connection Pooling**: High-performance asyncpg connection pool management

## Target Use Cases

- **Trading Sandbox Platform**: Complete trading environment for testing strategies and order execution
- **Research & Analysis**: Python-native infrastructure for integrating trading logic with numpy/pandas workflows
- **Strategy Development**: Platform for developing, testing, and managing trading strategies
- **Backend API Foundation**: Starting point for applications requiring user authentication and trading capabilities
- **Microservice Architecture**: Trading service component in a distributed system
- **Learning/Prototyping**: Educational project demonstrating FastAPI, async PostgreSQL, JWT authentication, and trading patterns

## Key Value Propositions

- **Modern Async Architecture**: Built with FastAPI and asyncpg for high-performance async I/O operations
- **Python-Native Trading Platform**: Seamless integration with data science tooling (numpy, pandas) without cross-language overhead
- **Security-First Design**: Password hashing with bcrypt, JWT-based authentication, and secure credential handling
- **Atomic Transaction Guarantees**: Database transactions ensure data consistency for order operations and balance updates
- **Developer-Friendly**: Automatic API documentation (Swagger/ReDoc), clear project structure, and comprehensive error handling
- **Production-Ready Patterns**: Connection pooling, environment-based configuration, standardized response envelopes, and migration management
- **Direct SQL Access**: High-performance asyncpg driver with direct SQL queries (no ORM overhead)
- **Flexible Market Integration**: Bybit API integration with testnet/mainnet support and multiple market categories

## API Response Standard

All endpoints use a consistent response envelope:

```json
{
  "status": "success" | "error",
  "message": "optional string",
  "meta": { "optional": "object" },
  "data": { "endpoint-specific": "payload" }
}
```

This ensures predictable API behavior and simplifies client-side error handling.

## API Documentation

- **OpenAPI Specification**: `swagger.yaml` (OpenAPI 3.0.3) provides complete API schema definition
- **Interactive Docs**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when server is running
- **Schema Definitions**: All request/response models are defined in both Pydantic schemas (`app/schemas/`) and OpenAPI spec

## Current API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Create a new user account
- `POST /auth/login` - Authenticate and receive JWT token
- `GET /auth/profile` - Get authenticated user profile

### Users (`/users`)
- `GET /users/me` - Get authenticated user profile with balance

### Market Data (`/market`)
- `GET /market/price` - Get current symbol price from Bybit

### Orders (`/order`)
- `POST /order` - Create a buy order (atomic transaction)
- `DELETE /order` - Close a sell order (atomic transaction)
- `GET /order` - List user transactions with filtering options

### Watchlist (`/watchlist`)
- `GET /watchlist` - List all watchlist entries
- `POST /watchlist` - Create a watchlist entry
- `DELETE /watchlist/{symbol}` - Delete a watchlist entry

### Strategies (`/strategy`)
- `GET /strategy` - List all strategies
- `POST /strategy` - Create a new strategy
- `PUT /strategy/{strategy_id}` - Update a strategy
- `DELETE /strategy/{strategy_id}` - Soft delete a strategy

### Trade Strategies (`/trade-strategy`)
- `GET /trade-strategy` - List all trade strategies
- `POST /trade-strategy` - Create a trade strategy mapping
- `PUT /trade-strategy/{trade_strategy_id}` - Update a trade strategy
- `DELETE /trade-strategy/{trade_strategy_id}` - Soft delete a trade strategy

### Logs (`/log`)
- `GET /log` - Get logs with optional symbol filtering and pagination
- `POST /log` - Create a log entry
- `GET /log/symbols` - Get unique symbols from log entries

### System
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

