# Migration Todo List: PHP Binance Sandbox → Python FastAPI

## Overview
Migration from PHP Laravel-based Binance Sandbox to Python FastAPI to enable numpy/pandas integration for research team workflows.

## Database & Schema Migration

### 1. Database Schema Migration
- [ ] Create PostgreSQL migration scripts for all tables based on MySQL schema from PHP project
- [ ] Tables to migrate:
  - `users` (extend existing: add `name`, `balance`)
  - `transact` (orders: buy/sell transactions)
  - `watchlists` (symbol tracking)
  - `log` (trading logs)
  - `strategies` (trading strategies)
  - `trade_strategies` (strategy-symbol mappings with timestamps)

### 2. Update User Model
- [ ] Extend users table schema to include:
  - `name` (VARCHAR/TEXT)
  - `balance` (DECIMAL(30,20), default 0)
- [ ] Update database initialization in `app/db/database.py`

## Data Models & Schemas

### 3. Create Pydantic Schemas
- [ ] `TransactSchema` (Order model):
  - symbol, buy_price, sell_price, quantity, user_id, status, strategy
  - Response models with calculated fields (diff, aggregates, equity)
- [ ] `WatchlistSchema`:
  - symbol, created_at
- [ ] `LogSchema`:
  - symbol, data (JSON), action, created_at, updated_at
- [ ] `StrategySchema`:
  - name, slug, deleted_at, created_at, updated_at
- [ ] `TradeStrategySchema`:
  - symbol, strategy_id, timestamp, deleted_at, created_at, updated_at

### 4. Create Database Models/DAO Layer
- [ ] Implement async database functions for `transact` table:
  - `create_transaction()`, `get_transaction_by_id()`, `get_user_transactions()`, `update_transaction()`, `get_active_transaction()`
- [ ] Implement async database functions for `watchlists` table:
  - `create_watchlist()`, `get_all_watchlists()`, `delete_watchlist()`, `get_watchlist_by_symbol()`
- [ ] Implement async database functions for `log` table:
  - `create_log()`, `get_logs()`, `get_logs_by_symbol()`, `get_unique_symbols()`
- [ ] Implement async database functions for `strategies` table:
  - `create_strategy()`, `get_all_strategies()`, `get_strategy_by_id()`, `update_strategy()`, `soft_delete_strategy()`
- [ ] Implement async database functions for `trade_strategies` table:
  - `create_trade_strategy()`, `get_trade_strategies()`, `get_trade_strategy_by_id()`, `update_trade_strategy()`, `soft_delete_trade_strategy()`

## External API Integration

### 5. Binance API Integration
- [ ] Create `app/services/binance.py` service module
- [ ] Implement async HTTP client (httpx or aiohttp)
- [ ] Implement `get_current_price(symbol: str)` function
- [ ] Support testnet/mainnet switching via configuration
- [ ] Error handling for API failures (connection errors, invalid responses)
- [ ] Add Binance API configuration to `app/core/config.py`:
  - `BINANCE_API_URL`
  - `BINANCE_TESTNET_API_URL`
  - `BINANCE_USE_TESTNET`

## API Endpoints - Order Management

### 6. Order Creation (POST /order)
- [ ] Create `app/routers/order.py` router
- [ ] Implement POST `/order` endpoint:
  - Validate: userEmail, symbol (max 10 chars), quantity (numeric)
  - Fetch current price from Binance API
  - Check user balance (sufficient funds)
  - Prevent duplicate orders (same symbol, status=1, same user)
  - Create transaction record
  - Update user balance (subtract)
  - Use database transactions for atomicity
  - Return created transaction

### 7. Order Closing (DELETE /order)
- [ ] Implement DELETE `/order` endpoint:
  - Validate: userEmail, symbol
  - Find active transaction (status=1)
  - Fetch current price from Binance API
  - Update transaction (set sell_price, status=2)
  - Update user balance (add back)
  - Use database transactions for atomicity
  - Return success message

### 8. Order Listing (GET /order)
- [ ] Implement GET `/order` endpoint:
  - Get all user orders (ordered by status ASC, created_at DESC)
  - Support query params: `active` (filter by status=1), `symbol` (filter by symbol)
  - Calculate computed fields:
    - `diff` = sell_price - buy_price
    - `buyAggregate` = buy_price * quantity
    - `sellAggregate` = sell_price * quantity
    - `diffDollar` = equity if status=2, else 0
  - Return list with unique symbols

## API Endpoints - Watchlists

### 9. Watchlist Viewing (GET /watchlists)
- [ ] Create `app/routers/watchlists.py` router
- [ ] Implement GET `/watchlists` endpoint:
  - Retrieve all watchlist items
  - Return list of symbols

### 10. Watchlist Creation (POST /watchlists)
- [ ] Implement POST `/watchlists` endpoint:
  - Validate: symbol (required, max 10 chars)
  - Create watchlist entry
  - Return created watchlist

### 11. Watchlist Deletion (DELETE /watchlists)
- [ ] Implement DELETE `/watchlists` endpoint:
  - Validate: symbol (required)
  - Delete watchlist entry
  - Return success message

## API Endpoints - Logging

### 12. Log Creation (POST /log)
- [ ] Create `app/routers/log.py` router
- [ ] Implement POST `/log` endpoint:
  - Validate: symbol, data, action
  - Create log entry
  - Return created log with ID

### 13. Log Retrieval (GET /log)
- [ ] Implement GET `/log` endpoint:
  - Support query params: `symbol` (LIKE search), pagination
  - Order by created_at DESC
  - Parse JSON data field
  - Return paginated results with unique symbols list

## API Endpoints - Trade Strategies

### 14. Strategy Listing (GET /trade-strategies)
- [ ] Create `app/routers/strategy.py` router
- [ ] Implement GET `/trade-strategies` endpoint:
  - Retrieve all trade strategies (including soft-deleted)
  - Return list of strategies

### 15. Strategy Creation (POST /trade-strategies)
- [ ] Implement POST `/trade-strategies` endpoint:
  - Validate: name, slug (or generate from name)
  - Create strategy record
  - Return created strategy

### 16. Strategy Update (PUT/PATCH /trade-strategies/{id})
- [ ] Implement PUT/PATCH `/trade-strategies/{id}` endpoint:
  - Validate: name, slug (optional)
  - Update strategy record
  - Return updated strategy

### 17. Strategy Soft Delete (DELETE /trade-strategies/{id})
- [ ] Implement DELETE `/trade-strategies/{id}` endpoint:
  - Soft delete strategy (set deleted_at timestamp)
  - Return success message

## Configuration & Constants

### 18. Error Handling & Constants
- [ ] Create `app/constants/messages.py` module
- [ ] Define error constants:
  - ERROR_INSUFFICIENT_BALANCE
  - ERROR_ORDER_REJECTION
  - ERROR_ORDER_NOT_FOUND
  - ERROR_FAILED_TO_CREATE_ORDER
  - ERROR_FAILED_TO_CLOSE_ORDER
  - ERROR_FAILED_TO_FETCH_MARKET_PRICE
  - ERROR_INVALID_MARKET_API_RESPONSE
  - ERROR_FAILED_TO_CONNECT_MARKET_API
  - ERROR_FETCHING_MARKET_PRICE
- [ ] Define success constants:
  - SUCCESS_SELL_ORDER_COMPLETE
  - SUCCESS_LOG_CREATED

### 19. Configuration Updates
- [ ] Add Binance API settings to `app/core/config.py`:
  - `BINANCE_API_URL: str = "https://api.binance.com"`
  - `BINANCE_TESTNET_API_URL: str = "https://testnet.binance.vision"`
  - `BINANCE_USE_TESTNET: bool = False`
- [ ] Update `.env` example with Binance configuration

## Business Logic

### 20. Transaction Management
- [ ] Implement database transaction wrapper for order creation
- [ ] Implement database transaction wrapper for order closing
- [ ] Ensure atomicity: transaction creation + balance update

### 21. Duplicate Order Prevention
- [ ] Implement check for existing open orders (status=1) for same symbol/user
- [ ] Return appropriate error if duplicate detected

### 22. Balance Management
- [ ] Implement balance validation before order creation
- [ ] Implement balance subtraction on buy (with decimal precision)
- [ ] Implement balance addition on sell (with decimal precision)
- [ ] Use DECIMAL(30,20) for precision matching PHP project

## Authentication & Authorization

### 23. Authentication Updates
- [ ] Update all new endpoints to require JWT authentication
- [ ] Use `Depends(get_current_user)` dependency
- [ ] Ensure user context is available in all protected routes
- [ ] Update order endpoints to use authenticated user (not userEmail from request)

## User Management

### 24. User Registration Updates
- [ ] Update `UserCreate` schema to include `name` field
- [ ] Update registration endpoint to accept and store `name`
- [ ] Initialize `balance` to 0.0 on user creation
- [ ] Update `UserResponse` schema to include `name` and `balance`

## Validation & Response Format

### 25. Request Validation
- [ ] Add validation for all endpoints matching PHP rules:
  - Symbol: max 10 characters
  - Quantity: numeric, positive
  - Email: valid email format
  - Required fields validation

### 26. Response Format Consistency
- [ ] Ensure all endpoints return `StandardResponse` format
- [ ] Maintain consistent error response structure
- [ ] Include appropriate HTTP status codes

## Database Initialization

### 27. Database Initialization Updates
- [ ] Update `init_db()` in `app/db/database.py` to create all tables:
  - Extend users table (add name, balance)
  - Create transact table
  - Create watchlists table
  - Create log table
  - Create strategies table
  - Create trade_strategies table
- [ ] Add proper indexes and foreign keys
- [ ] Support soft deletes for strategies and trade_strategies

## Testing

### 28. Integration Tests
- [ ] Create tests for order creation flow
- [ ] Create tests for order closing flow
- [ ] Create tests for balance management
- [ ] Create tests for Binance API integration (mocked)
- [ ] Create tests for duplicate order prevention
- [ ] Create tests for watchlist CRUD operations
- [ ] Create tests for logging operations
- [ ] Create tests for strategy management

## Documentation

### 29. Documentation Updates
- [ ] Update `README.md` with:
  - New endpoints documentation
  - Binance integration details
  - Environment variables for Binance
  - Migration notes from PHP project
  - Database schema overview
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Document response formats and error codes

## Dependencies

### 30. Python Dependencies
- [ ] Add `httpx` or `aiohttp` to `requirements.txt` for async HTTP client
- [ ] Consider `python-binance` library if available (or implement custom)
- [ ] Ensure all existing dependencies are compatible
- [ ] Test dependency installation and compatibility

## Notes

- All endpoints should use async/await patterns
- Database operations should use asyncpg connection pool
- Binance API calls should be async
- Maintain backward compatibility with existing auth endpoints
- Consider adding rate limiting for Binance API calls
- Consider adding caching for frequently accessed Binance data
- Decimal precision is critical for financial calculations (use Decimal type, not float)

