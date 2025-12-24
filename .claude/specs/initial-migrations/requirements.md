# Requirements: Initial Migrations - PHP Binance Sandbox to Python FastAPI

## Overview

Migrate the PHP Laravel-based Binance Sandbox application to Python FastAPI to enable seamless integration with numpy and pandas for research team workflows. This migration will preserve all existing functionality while providing a Python-native codebase that supports data science tooling.

## Background

The current PHP application (binance-sandbox) provides a trading sandbox environment with order management, balance tracking, watchlists, logging, and strategy management. The research team requires Python-based infrastructure to integrate trading logic with numpy and pandas without cross-language adjustments.

## Codebase Analysis Summary

### Existing Python Codebase (hola) - Reusable Components

**Authentication & Security:**
- JWT-based authentication system (`app/core/security.py`)
- User registration and login endpoints (`app/routers/auth.py`)
- Password hashing with bcrypt (`passlib`)
- User database operations (`app/db/database.py`)

**Database Infrastructure:**
- Async PostgreSQL connection pool using `asyncpg` (high-performance, C-based driver)
- Database initialization pattern (`init_db()`)
- Direct SQL queries with asyncpg (no ORM overhead for scalability)
- Standard response envelope (`app/schemas/common.py`)

**Project Structure:**
- FastAPI application setup with lifespan management
- Router-based organization pattern
- Pydantic schema validation
- Configuration management with `pydantic-settings`

### PHP Codebase (binance-sandbox) - Features to Migrate

**Core Features:**
- Order management (buy/sell transactions)
- User balance management
- Binance API integration for market prices
- Watchlist management
- Trading log system
- Strategy management (strategies and trade_strategies)
- Duplicate order prevention
- Transaction atomicity

**Database Schema:**
- `users` (extended: name, balance fields)
- `transact` (orders/transactions)
- `watchlists` (symbol tracking)
- `log` (trading logs)
- `strategies` (trading strategies)
- `trade_strategies` (strategy-symbol mappings)

## Requirements

### Requirement 1: Database Schema Migration
**User Story:** As a developer, I want all database tables from the PHP application migrated to PostgreSQL, so that the Python application can manage the same data structures.

#### Acceptance Criteria
1. WHEN the application starts THEN the system SHALL create all required tables if they do not exist
2. IF a table already exists THEN the system SHALL not attempt to recreate it
3. WHEN creating the `users` table THEN the system SHALL include fields: id, email, password, name, balance, created_at, updated_at
4. WHEN creating the `transact` table THEN the system SHALL include fields: id, symbol, buy_price, sell_price, status, created_at, quantity, user_id, updated_at
5. WHEN creating the `watchlists` table THEN the system SHALL include fields: id, symbol, created_at
6. WHEN creating the `log` table THEN the system SHALL include fields: id, symbol, data, created_at, updated_at, action
7. WHEN creating the `strategies` table THEN the system SHALL include fields: id, name, slug, deleted_at, created_at, updated_at
8. WHEN creating the `trade_strategies` table THEN the system SHALL include fields: id, symbol, strategy_id, timestamp, deleted_at, created_at, updated_at
9. WHEN creating numeric fields for prices and balances THEN the system SHALL use DECIMAL(30,20) to match PHP precision
10. WHEN creating foreign keys THEN the system SHALL establish proper relationships (e.g., trade_strategies.strategy_id → strategies.id)

### Requirement 2: User Model Extension
**User Story:** As a user, I want my profile to include name and balance information, so that the trading system can track my account details.

#### Acceptance Criteria
1. WHEN a user registers THEN the system SHALL accept and store a `name` field
2. WHEN a user is created THEN the system SHALL initialize `balance` to 0.00000000000000000000
3. WHEN retrieving user profile THEN the system SHALL return name and balance in the response
4. IF name is not provided during registration THEN the system SHALL return a validation error
5. WHEN updating user balance THEN the system SHALL maintain DECIMAL(30,20) precision

### Requirement 3: Binance API Integration
**User Story:** As a trading system, I want to fetch real-time market prices from Binance API, so that orders can be executed at current market rates.

#### Acceptance Criteria
1. WHEN fetching a market price THEN the system SHALL call Binance API endpoint `/api/v3/ticker/price?symbol={symbol}`
2. IF `BINANCE_USE_TESTNET` is true THEN the system SHALL use testnet API URL
3. IF `BINANCE_USE_TESTNET` is false THEN the system SHALL use production API URL
4. WHEN the API request fails THEN the system SHALL return an appropriate error message
5. WHEN the API response is invalid THEN the system SHALL return an error indicating invalid response
6. WHEN the API connection fails THEN the system SHALL return an error indicating connection failure
7. IF the response does not contain a price field THEN the system SHALL return an error
8. WHEN fetching price THEN the system SHALL use async HTTP client (httpx or aiohttp)
9. WHEN configuration is missing THEN the system SHALL use default values (production API URL)

### Requirement 4: Order Creation (Buy)
**User Story:** As a user, I want to create a buy order for a trading symbol, so that I can purchase assets at the current market price.

#### Acceptance Criteria
1. WHEN creating an order THEN the system SHALL require authentication (JWT token)
2. WHEN creating an order THEN the system SHALL validate: symbol (required, max 10 chars), quantity (required, numeric, positive)
3. WHEN creating an order THEN the system SHALL fetch current market price from Binance API
4. IF user balance is insufficient THEN the system SHALL return error "insufficient balance" with status 400
5. IF an active order (status=1) exists for the same symbol and user THEN the system SHALL return error "rejection" with status 400
6. WHEN creating an order successfully THEN the system SHALL create a transaction record with buy_price, quantity, symbol, user_id, status=1
7. WHEN creating an order successfully THEN the system SHALL subtract (price * quantity) from user balance
8. WHEN creating an order THEN the system SHALL use database transactions to ensure atomicity
9. IF order creation fails THEN the system SHALL rollback all database changes
10. WHEN order is created THEN the system SHALL return the created transaction record

### Requirement 5: Order Closing (Sell)
**User Story:** As a user, I want to close an active buy order, so that I can sell my position at the current market price.

#### Acceptance Criteria
1. WHEN closing an order THEN the system SHALL require authentication (JWT token)
2. WHEN closing an order THEN the system SHALL validate: symbol (required, max 10 chars)
3. WHEN closing an order THEN the system SHALL find the active transaction (status=1) for the symbol and authenticated user
4. IF no active order is found THEN the system SHALL return error "order not found" with status 400
5. WHEN closing an order THEN the system SHALL fetch current market price from Binance API
6. WHEN closing an order successfully THEN the system SHALL update transaction: set sell_price, set status=2
7. WHEN closing an order successfully THEN the system SHALL add (sell_price * quantity) to user balance
8. WHEN closing an order THEN the system SHALL use database transactions to ensure atomicity
9. IF order closing fails THEN the system SHALL rollback all database changes
10. WHEN order is closed THEN the system SHALL return success message "sell order complete"

### Requirement 6: Order Listing
**User Story:** As a user, I want to view my order history, so that I can track my trading activity and performance.

#### Acceptance Criteria
1. WHEN listing orders THEN the system SHALL require authentication (JWT token)
2. WHEN listing orders THEN the system SHALL return all orders for the authenticated user
3. WHEN listing orders THEN the system SHALL order by status ASC, then created_at DESC
4. IF query parameter `active=true` is provided THEN the system SHALL filter orders where status=1
5. IF query parameter `symbol` is provided THEN the system SHALL filter orders matching the symbol
6. WHEN returning orders THEN the system SHALL include calculated fields: diff (sell_price - buy_price), buyAggregate (buy_price * quantity), sellAggregate (sell_price * quantity), diffDollar (equity if status=2, else 0)
7. WHEN returning orders THEN the system SHALL include unique symbols list in the response
8. WHEN sell_price is NULL THEN the system SHALL handle calculations appropriately (use 0 or NULL)

### Requirement 7: Watchlist Management
**User Story:** As a user, I want to manage my watchlist of trading symbols, so that I can track symbols of interest.

#### Acceptance Criteria
1. WHEN viewing watchlists THEN the system SHALL return all watchlist entries
2. WHEN creating a watchlist entry THEN the system SHALL validate: symbol (required, max 10 chars)
3. WHEN creating a watchlist entry THEN the system SHALL create a new watchlist record with symbol and created_at
4. WHEN deleting a watchlist entry THEN the system SHALL validate: symbol (required)
5. WHEN deleting a watchlist entry THEN the system SHALL remove the watchlist record
6. WHEN watchlist operations are performed THEN the system SHALL require authentication (JWT token)

### Requirement 8: Logging System
**User Story:** As a trading system, I want to log trading activities and strategy data, so that users can review their trading history and analysis.

#### Acceptance Criteria
1. WHEN creating a log entry THEN the system SHALL validate: symbol (required), data (required), action (required)
2. WHEN creating a log entry THEN the system SHALL store symbol, data (as JSON text), action, created_at, updated_at
3. WHEN retrieving logs THEN the system SHALL support query parameter `symbol` for filtering (LIKE search)
4. WHEN retrieving logs THEN the system SHALL order results by created_at DESC
5. WHEN retrieving logs THEN the system SHALL support pagination (default 100 items per page)
6. WHEN returning logs THEN the system SHALL parse the data field as JSON
7. WHEN returning logs THEN the system SHALL include unique symbols list in the response
8. WHEN log operations are performed THEN the system SHALL require authentication (JWT token)

### Requirement 9: Strategy Management
**User Story:** As a user, I want to manage trading strategies, so that I can organize and track different trading approaches.

#### Acceptance Criteria
1. WHEN listing strategies THEN the system SHALL return all strategies including soft-deleted ones
2. WHEN creating a strategy THEN the system SHALL validate: name (required), slug (required or auto-generated from name)
3. WHEN creating a strategy THEN the system SHALL create a record with name, slug, created_at, updated_at
4. WHEN updating a strategy THEN the system SHALL validate: name (optional), slug (optional)
5. WHEN updating a strategy THEN the system SHALL update the strategy record
6. WHEN soft-deleting a strategy THEN the system SHALL set deleted_at timestamp instead of removing the record
7. WHEN managing strategies THEN the system SHALL require authentication (JWT token)

### Requirement 10: Trade Strategy Management
**User Story:** As a user, I want to associate trading symbols with strategies and configure timestamp intervals, so that I can track strategy performance per symbol.

#### Acceptance Criteria
1. WHEN listing trade strategies THEN the system SHALL return all trade strategy mappings
2. WHEN creating a trade strategy THEN the system SHALL validate: symbol (required, max 15 chars), strategy_id (required, exists in strategies), timestamp (required, default '5m')
3. WHEN creating a trade strategy THEN the system SHALL create a record with symbol, strategy_id, timestamp, created_at, updated_at
4. WHEN updating a trade strategy THEN the system SHALL allow updating symbol, strategy_id, and timestamp
5. WHEN soft-deleting a trade strategy THEN the system SHALL set deleted_at timestamp
6. WHEN managing trade strategies THEN the system SHALL require authentication (JWT token)
7. IF strategy_id references a deleted strategy THEN the system SHALL handle the relationship appropriately (foreign key constraint)

### Requirement 11: Error Handling and Constants
**User Story:** As a developer, I want consistent error messages and success responses, so that the API provides clear feedback to clients.

#### Acceptance Criteria
1. WHEN an error occurs THEN the system SHALL return errors using StandardResponse format with status="error"
2. WHEN an operation succeeds THEN the system SHALL return StandardResponse format with status="success"
3. WHEN returning error messages THEN the system SHALL use predefined constants for consistency
4. WHEN insufficient balance error occurs THEN the system SHALL return message "insufficient balance"
5. WHEN duplicate order error occurs THEN the system SHALL return message "rejection"
6. WHEN order not found error occurs THEN the system SHALL return message "order not found"
7. WHEN Binance API errors occur THEN the system SHALL return appropriate error messages from constants
8. WHEN log creation succeeds THEN the system SHALL return message "Log created successfully"

### Requirement 12: Authentication Integration
**User Story:** As a security requirement, I want all trading endpoints to require authentication, so that only authorized users can access trading features.

#### Acceptance Criteria
1. WHEN accessing order endpoints THEN the system SHALL require valid JWT token
2. WHEN accessing watchlist endpoints THEN the system SHALL require valid JWT token
3. WHEN accessing log endpoints THEN the system SHALL require valid JWT token
4. WHEN accessing strategy endpoints THEN the system SHALL require valid JWT token
5. WHEN token is missing or invalid THEN the system SHALL return 401 Unauthorized
6. WHEN using authenticated endpoints THEN the system SHALL use the authenticated user from token (not userEmail from request body)
7. WHEN user context is needed THEN the system SHALL use `Depends(get_current_user)` dependency

### Requirement 13: Data Validation and Type Safety
**User Story:** As a developer, I want strong type validation for all API inputs, so that invalid data is rejected before processing.

#### Acceptance Criteria
1. WHEN validating symbol THEN the system SHALL enforce max length of 10 characters (15 for trade_strategies)
2. WHEN validating quantity THEN the system SHALL ensure it is numeric and positive
3. WHEN validating email THEN the system SHALL use EmailStr type from Pydantic
4. WHEN validating prices THEN the system SHALL use Decimal type for precision
5. WHEN validating required fields THEN the system SHALL return 422 status with validation errors
6. WHEN validating data types THEN the system SHALL use Pydantic schemas for all request/response models

### Requirement 14: Database Transaction Safety
**User Story:** As a system requirement, I want all order operations to be atomic, so that data consistency is maintained even if errors occur.

#### Acceptance Criteria
1. WHEN creating an order THEN the system SHALL wrap transaction creation and balance update in a database transaction
2. WHEN closing an order THEN the system SHALL wrap transaction update and balance update in a database transaction
3. IF any operation in a transaction fails THEN the system SHALL rollback all changes
4. WHEN using transactions THEN the system SHALL use asyncpg transaction context managers
5. WHEN transaction completes successfully THEN the system SHALL commit all changes atomically

### Requirement 15: Python Ecosystem Integration
**User Story:** As a research team member, I want the codebase to be Python-native, so that I can integrate numpy and pandas without cross-language barriers.

#### Acceptance Criteria
1. WHEN implementing calculations THEN the system SHALL use Python native types (Decimal for financial calculations)
2. WHEN returning data THEN the system SHALL use Pydantic models that are compatible with pandas DataFrames
3. WHEN implementing business logic THEN the system SHALL structure code to allow easy integration with numpy/pandas
4. WHEN designing data structures THEN the system SHALL consider future data science workflows
5. WHEN implementing endpoints THEN the system SHALL return JSON that can be easily consumed by Python data science tools
6. WHEN querying database THEN the system SHALL provide helper functions to convert asyncpg records to pandas DataFrames
7. WHEN structuring database access THEN the system SHALL organize query functions in a DAO (Data Access Object) pattern for maintainability

## Technical Constraints

1. **Database:** PostgreSQL (migrated from MySQL in PHP project)
2. **Database Access:** Use `asyncpg` directly (no ORM) for maximum performance and scalability
   - Maintain existing asyncpg connection pool pattern
   - Create structured data access layer (DAO pattern) for organized query functions
   - Provide helper functions for pandas DataFrame conversion from asyncpg records
3. **Precision:** All financial calculations must use DECIMAL(30,20) to match PHP precision
4. **Async Operations:** All I/O operations (database, HTTP) must be async/await
5. **Authentication:** JWT-based authentication (existing system)
6. **Response Format:** StandardResponse envelope for all endpoints
7. **Error Handling:** Consistent error messages via constants
8. **Type Safety:** Pydantic schemas for all request/response validation
9. **Performance:** Optimize for high-traffic scenarios (1000+ requests/minute minimum)

## Out of Scope

1. Frontend/UI components (PHP project has Blade templates - not migrating)
2. Web routes (only API routes are being migrated)
3. Email verification features
4. Password reset functionality
5. Real-time WebSocket connections
6. Rate limiting implementation (can be added later)
7. Caching layer (can be added later)

## Success Criteria

The migration is considered successful when:
1. All database tables are created and match PHP schema structure
2. All API endpoints are implemented and functional
3. Binance API integration works for both testnet and production
4. Order creation and closing maintain data consistency
5. All endpoints require proper authentication
6. Response formats match StandardResponse pattern
7. Error handling is consistent and informative
8. Code is ready for numpy/pandas integration by research team

