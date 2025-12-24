-- Initial schema migration - create all tables
-- Flyway migration: V1__initial_schema

-- Create or update users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    balance DECIMAL(30,20) NOT NULL DEFAULT 0.00000000000000000000,
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);

-- Add name and balance columns if they don't exist (for existing tables)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='users' AND column_name='name') THEN
        ALTER TABLE users ADD COLUMN name TEXT;
        UPDATE users SET name = '' WHERE name IS NULL;
        ALTER TABLE users ALTER COLUMN name SET NOT NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='users' AND column_name='balance') THEN
        ALTER TABLE users ADD COLUMN balance DECIMAL(30,20) NOT NULL DEFAULT 0.00000000000000000000;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='users' AND column_name='updated_at') THEN
        ALTER TABLE users ADD COLUMN updated_at TIMESTAMPTZ DEFAULT timezone('utc', now());
    END IF;
END $$;

-- Create transact table
CREATE TABLE IF NOT EXISTS transact (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    buy_price DECIMAL(30,20) NOT NULL,
    sell_price DECIMAL(30,20),
    status INTEGER NOT NULL DEFAULT 1,
    quantity DECIMAL(30,20) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);

-- Create watchlists table
CREATE TABLE IF NOT EXISTS watchlists (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);

-- Create log table
CREATE TABLE IF NOT EXISTS log (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    data TEXT NOT NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);

-- Create strategies table
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);

-- Create trade_strategies table
CREATE TABLE IF NOT EXISTS trade_strategies (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    strategy_id INTEGER NOT NULL REFERENCES strategies(id),
    timestamp TEXT NOT NULL DEFAULT '5m',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ DEFAULT timezone('utc', now())
);

