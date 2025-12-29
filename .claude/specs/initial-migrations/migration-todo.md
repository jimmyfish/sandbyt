# Migration Todo List: PHP Binance Sandbox → Python FastAPI

## Overview
Migration from PHP Laravel-based Binance Sandbox to Python FastAPI to enable numpy/pandas integration for research team workflows.

## Status Summary
**Last Updated:** Based on actual implementation verification
- **Overall Progress:** ~95% Complete
- **Completed:** 28/30 major sections fully implemented
- **Partial:** 1 section (some documentation)
- **Remaining:** Strategy integration tests (optional), comprehensive documentation

### Key Gaps
1. **Integration Tests:** Missing `test_strategy_endpoints.py` and `test_trade_strategy_endpoints.py` (marked as not needed)
2. **Documentation:** README.md needs more comprehensive endpoint documentation and migration notes

### Note on Dynamic Environment Modeling
Binance testnet/mainnet switching is handled via dynamic environment variable `BINANCE_API_URL` (set to either `https://api.binance.com` or `https://testnet.binance.vision`). No separate testnet flag needed.

## Database & Schema Migration

### 1. Database Schema Migration
- [x] Create PostgreSQL migration scripts for all tables based on MySQL schema from PHP project
- [x] Tables to migrate:
  - [x] `users` (extend existing: add `name`, `balance`)
  - [x] `transact` (orders: buy/sell transactions)
  - [x] `watchlists` (symbol tracking)
  - [x] `log` (trading logs)
  - [x] `strategies` (trading strategies)
  - [x] `trade_strategies` (strategy-symbol mappings with timestamps)

### 2. Update User Model
- [x] Extend users table schema to include:
  - [x] `name` (VARCHAR/TEXT)
  - [x] `balance` (DECIMAL(30,20), default 0)
- [x] Update database initialization in `app/db/database.py`

## Data Models & Schemas

### 3. Create Pydantic Schemas
- [x] `TransactSchema` (Order model):
  - [x] symbol, buy_price, sell_price, quantity, user_id, status, strategy
  - [x] Response models with calculated fields (diff, aggregates, equity)
- [x] `WatchlistSchema`:
  - [x] symbol, created_at
- [x] `LogSchema`:
  - [x] symbol, data (JSON), action, created_at, updated_at
- [x] `StrategySchema`:
  - [x] name, slug, deleted_at, created_at, updated_at
- [x] `TradeStrategySchema`:
  - [x] symbol, strategy_id, timestamp, deleted_at, created_at, updated_at

### 4. Create Database Models/DAO Layer
- [x] Implement async database functions for `transact` table:
  - [x] `create_transaction()`, `get_user_transactions()`, `update_transaction()`, `get_active_transaction()`
  - [ ] `get_transaction_by_id()` (not implemented, may not be needed)
- [x] Implement async database functions for `watchlists` table:
  - [x] `create_watchlist()`, `get_all_watchlists()`, `delete_watchlist()`
  - [ ] `get_watchlist_by_symbol()` (not implemented, may not be needed)
- [x] Implement async database functions for `log` table:
  - [x] `create_log()`, `get_logs()`, `get_unique_symbols()`
  - [x] Symbol filtering via `get_logs()` with symbol parameter (LIKE search)
- [x] Implement async database functions for `strategies` table:
  - [x] `create_strategy()`, `get_all_strategies()`, `get_strategy_by_id()`, `update_strategy()`, `soft_delete_strategy()`
- [x] Implement async database functions for `trade_strategies` table:
  - [x] `create_trade_strategy()`, `get_trade_strategies()`, `get_trade_strategy_by_id()`, `update_trade_strategy()`, `soft_delete_trade_strategy()`

## External API Integration

### 5. Binance API Integration
- [x] Create `app/services/binance.py` service module
- [x] Implement async HTTP client (httpx or aiohttp)
- [x] Implement `get_current_price(symbol: str)` function
- [x] Support testnet/mainnet switching via configuration (handled via dynamic `BINANCE_API_URL` env var, not needed)
- [x] Error handling for API failures (connection errors, invalid responses)
- [x] Add Binance API configuration to `app/core/config.py`:
  - [x] `BINANCE_API_URL`
  - [x] `BINANCE_TESTNET_API_URL` (not needed)
  - [x] `BINANCE_USE_TESTNET` (not needed)

## API Endpoints - Order Management

### 6. Order Creation (POST /order)
- [x] Create `app/routers/order.py` router
- [x] Implement POST `/order` endpoint:
  - [x] Validate: symbol (max 10 chars), quantity (numeric, positive)
  - [x] Fetch current price from Binance API
  - [x] Check user balance (sufficient funds)
  - [x] Prevent duplicate orders (same symbol, status=1, same user)
  - [x] Create transaction record
  - [x] Update user balance (subtract)
  - [x] Use database transactions for atomicity
  - [x] Return created transaction
  - Note: Uses authenticated user from JWT (not userEmail from request body)

### 7. Order Closing (DELETE /order)
- [x] Implement DELETE `/order` endpoint:
  - [x] Validate: symbol (max 10 chars)
  - [x] Find active transaction (status=1)
  - [x] Fetch current price from Binance API
  - [x] Update transaction (set sell_price, status=2)
  - [x] Update user balance (add back)
  - [x] Use database transactions for atomicity
  - [x] Return success message
  - Note: Uses authenticated user from JWT (not userEmail from request body)

### 8. Order Listing (GET /order)
- [x] Implement GET `/order` endpoint:
  - [x] Get all user orders (ordered by status ASC, created_at DESC)
  - [x] Support query params: `active` (filter by status=1), `symbol` (filter by symbol)
  - [x] Calculate computed fields:
    - [x] `diff` = sell_price - buy_price
    - [x] `buyAggregate` = buy_price * quantity
    - [x] `sellAggregate` = sell_price * quantity
    - [x] `diffDollar` = equity if status=2, else 0
  - [x] Return list with unique symbols

## API Endpoints - Watchlists

### 9. Watchlist Viewing (GET /watchlists)
- [x] Create `app/routers/watchlist.py` router (note: singular, not plural)
- [x] Implement GET `/watchlist` endpoint:
  - [x] Retrieve all watchlist items
  - [x] Return list of symbols with unique symbols list

### 10. Watchlist Creation (POST /watchlists)
- [x] Implement POST `/watchlist` endpoint:
  - [x] Validate: symbol (required, max 10 chars)
  - [x] Create watchlist entry
  - [x] Return created watchlist

### 11. Watchlist Deletion (DELETE /watchlists)
- [x] Implement DELETE `/watchlist/{symbol}` endpoint:
  - [x] Validate: symbol (required)
  - [x] Delete watchlist entry
  - [x] Return success message

## API Endpoints - Logging

### 12. Log Creation (POST /log)
- [x] Create `app/routers/log.py` router
- [x] Implement POST `/log` endpoint:
  - [x] Validate: symbol, data (dict), action
  - [x] Create log entry
  - [x] Return created log with ID

### 13. Log Retrieval (GET /log)
- [x] Implement GET `/log` endpoint:
  - [x] Support query params: `symbol` (LIKE search), pagination (limit, offset)
  - [x] Order by created_at DESC
  - [x] Parse JSON data field
  - [x] Return paginated results with unique symbols list

## API Endpoints - Trade Strategies

### 14. Strategy Listing (GET /strategy)
- [x] Create `app/routers/strategy.py` router
- [x] Implement GET `/strategy` endpoint:
  - [x] Retrieve all strategies (including soft-deleted)
  - [x] Return list of strategies

### 15. Strategy Creation (POST /strategy)
- [x] Implement POST `/strategy` endpoint:
  - [x] Validate: name, slug (optional, auto-generated from name)
  - [x] Create strategy record
  - [x] Return created strategy

### 16. Strategy Update (PUT /strategy/{id})
- [x] Implement PUT `/strategy/{strategy_id}` endpoint:
  - [x] Validate: name, slug (optional)
  - [x] Update strategy record
  - [x] Return updated strategy

### 17. Strategy Soft Delete (DELETE /strategy/{id})
- [x] Implement DELETE `/strategy/{strategy_id}` endpoint:
  - [x] Soft delete strategy (set deleted_at timestamp)
  - [x] Return success message

### Trade Strategy Endpoints (separate router)
- [x] Create `app/routers/trade_strategy.py` router
- [x] Implement GET `/trade-strategy` endpoint
- [x] Implement POST `/trade-strategy` endpoint
- [x] Implement PUT `/trade-strategy/{trade_strategy_id}` endpoint
- [x] Implement DELETE `/trade-strategy/{trade_strategy_id}` endpoint

## Configuration & Constants

### 18. Error Handling & Constants
- [x] Create constants module (located at `app/core/constants.py`, not `app/constants/messages.py`)
- [x] Define error constants:
  - [x] ERROR_INSUFFICIENT_BALANCE
  - [x] ERROR_DUPLICATE_ORDER (named "rejection" in constants)
  - [x] ERROR_ORDER_NOT_FOUND
  - [x] ERROR_BINANCE_CONNECTION
  - [x] ERROR_BINANCE_INVALID_RESPONSE
  - [ ] ERROR_FAILED_TO_CREATE_ORDER (not needed, using generic error handling)
  - [ ] ERROR_FAILED_TO_CLOSE_ORDER (not needed, using generic error handling)
  - [ ] ERROR_FAILED_TO_FETCH_MARKET_PRICE (covered by ERROR_BINANCE_CONNECTION)
  - [ ] ERROR_INVALID_MARKET_API_RESPONSE (covered by ERROR_BINANCE_INVALID_RESPONSE)
  - [ ] ERROR_FAILED_TO_CONNECT_MARKET_API (covered by ERROR_BINANCE_CONNECTION)
  - [ ] ERROR_FETCHING_MARKET_PRICE (covered by ERROR_BINANCE_CONNECTION)
- [x] Define success constants:
  - [x] SUCCESS_ORDER_CLOSED (named "sell order complete" in constants)
  - [x] SUCCESS_LOG_CREATED

### 19. Configuration Updates
- [x] Add Binance API settings to `app/core/config.py`:
  - [x] `BINANCE_API_URL: str = "https://api.binance.com"`
  - [x] `BINANCE_TESTNET_API_URL: str = "https://testnet.binance.vision"` (not needed)
  - [x] `BINANCE_USE_TESTNET: bool = False` (not needed)
- [x] Update `.env` example with Binance configuration (README.md includes Binance config)

## Business Logic

### 20. Transaction Management
- [x] Implement database transaction wrapper for order creation (`create_order_atomic()`)
- [x] Implement database transaction wrapper for order closing (`close_order_atomic()`)
- [x] Ensure atomicity: transaction creation + balance update

### 21. Duplicate Order Prevention
- [x] Implement check for existing open orders (status=1) for same symbol/user
- [x] Return appropriate error if duplicate detected (ERROR_DUPLICATE_ORDER)

### 22. Balance Management
- [x] Implement balance validation before order creation
- [x] Implement balance subtraction on buy (with decimal precision)
- [x] Implement balance addition on sell (with decimal precision)
- [x] Use DECIMAL(30,20) for precision matching PHP project

## Authentication & Authorization

### 23. Authentication Updates
- [x] Update all new endpoints to require JWT authentication
- [x] Use `Depends(get_current_user)` dependency
- [x] Ensure user context is available in all protected routes
- [x] Update order endpoints to use authenticated user (not userEmail from request)

## User Management

### 24. User Registration Updates
- [x] Update `UserCreate` schema to include `name` field
- [x] Update registration endpoint to accept and store `name`
- [x] Initialize `balance` to 0.0 on user creation (DECIMAL(30,20) with default 0.00000000000000000000)
- [x] Update `UserResponse` schema to include `name` and `balance`

## Validation & Response Format

### 25. Request Validation
- [x] Add validation for all endpoints matching PHP rules:
  - [x] Symbol: max 10 characters (15 for trade_strategies)
  - [x] Quantity: numeric, positive (Decimal type with gt=0)
  - [x] Email: valid email format (EmailStr from Pydantic)
  - [x] Required fields validation (Pydantic Field validations)

### 26. Response Format Consistency
- [x] Ensure all endpoints return `StandardResponse` format
- [x] Maintain consistent error response structure
- [x] Include appropriate HTTP status codes

## Database Initialization

### 27. Database Initialization Updates
- [x] Database schema managed via Flyway migrations (`db/migration/V1__initial_schema.sql`)
- [x] Update `init_db()` in `app/db/database.py` to handle users table:
  - [x] Extend users table (add name, balance) with backward-compatible migration
  - [x] Create users table if not exists
- [x] Tables created via Flyway migration:
  - [x] Extend users table (add name, balance)
  - [x] Create transact table
  - [x] Create watchlists table
  - [x] Create log table
  - [x] Create strategies table
  - [x] Create trade_strategies table
- [x] Add proper indexes and foreign keys (in migration file)
- [x] Support soft deletes for strategies and trade_strategies (deleted_at column)

## Testing

### 28. Integration Tests
- [x] Create tests for order creation flow (`test_order_endpoints.py`)
- [x] Create tests for order closing flow (`test_order_endpoints.py`)
- [x] Create tests for balance management (unit tests in `test_database_user_balance.py`)
- [x] Create tests for Binance API integration (mocked) (unit tests)
- [x] Create tests for duplicate order prevention (`test_order_endpoints.py`)
- [x] Create tests for watchlist CRUD operations (`test_watchlist_endpoints.py`)
- [x] Create tests for logging operations (`test_log_endpoints.py`)
- [ ] Create tests for strategy management (missing `test_strategy_endpoints.py`) - (not needed)
- [ ] Create tests for trade strategy management (missing `test_trade_strategy_endpoints.py`) - (not needed)

## Documentation

### 29. Documentation Updates
- [x] Update `README.md` with:
  - [x] Binance integration details (basic)
  - [x] Environment variables for Binance (BINANCE_API_URL)
  - [ ] New endpoints documentation (not comprehensive)
  - [ ] Migration notes from PHP project (not documented)
  - [ ] Database schema overview (not documented)
- [x] Update API documentation (Swagger/OpenAPI) - OpenAPI spec exists (`openapi.yaml`)
- [x] Document response formats and error codes (via OpenAPI spec and StandardResponse)

## Dependencies

### 30. Python Dependencies
- [x] Add `httpx` or `aiohttp` to `requirements.txt` for async HTTP client (`httpx==0.28.1`)
- [x] Consider `python-binance` library if available (or implement custom) - custom implementation using httpx
- [x] Ensure all existing dependencies are compatible
- [x] Test dependency installation and compatibility
- [x] Pandas included in requirements.txt (for DataFrame helpers)

## Notes

- All endpoints should use async/await patterns
- Database operations should use asyncpg connection pool
- Binance API calls should be async
- Maintain backward compatibility with existing auth endpoints
- Consider adding rate limiting for Binance API calls
- Consider adding caching for frequently accessed Binance data
- Decimal precision is critical for financial calculations (use Decimal type, not float)

