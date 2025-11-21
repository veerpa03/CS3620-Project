-- StockFlow Database Schema
-- 10 Tables for Checkpoint 1

-- Drop existing tables if they exist
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS watchlist;
DROP TABLE IF EXISTS holdings;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS sectors;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS users;

-- 1. USERS TABLE - User accounts and authentication
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    INDEX idx_email (email),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. PORTFOLIOS TABLE - User portfolios (1 user can have multiple)
CREATE TABLE portfolios (
    portfolio_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    portfolio_name VARCHAR(100) NOT NULL,
    description TEXT,
    initial_cash DECIMAL(15, 2) DEFAULT 10000.00,
    current_cash DECIMAL(15, 2) DEFAULT 10000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. SECTORS TABLE - Stock industry sectors
CREATE TABLE sectors (
    sector_id INT PRIMARY KEY AUTO_INCREMENT,
    sector_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. STOCKS TABLE - Master stock information
CREATE TABLE stocks (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector_id INT,
    exchange VARCHAR(50),
    market_cap BIGINT,
    ipo_year INT,
    country VARCHAR(100) DEFAULT 'USA',
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id) ON DELETE SET NULL,
    INDEX idx_symbol (symbol),
    INDEX idx_sector (sector_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. STOCK_PRICES TABLE - Historical daily stock prices
CREATE TABLE stock_prices (
    price_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2) NOT NULL,
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    volume BIGINT,
    adjusted_close DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_stock_date (stock_id, price_date),
    INDEX idx_stock_date (stock_id, price_date),
    INDEX idx_date (price_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. TRANSACTIONS TABLE - Buy/Sell transaction records
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_per_share DECIMAL(10, 2) NOT NULL CHECK (price_per_share > 0),
    total_amount DECIMAL(15, 2) NOT NULL,
    fees DECIMAL(10, 2) DEFAULT 0.00,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_portfolio (portfolio_id),
    INDEX idx_stock (stock_id),
    INDEX idx_date (transaction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. HOLDINGS TABLE - Current stock holdings per portfolio
CREATE TABLE holdings (
    holding_id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    average_cost_basis DECIMAL(10, 2) NOT NULL,
    total_invested DECIMAL(15, 2) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_stock (portfolio_id, stock_id),
    INDEX idx_portfolio (portfolio_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. WATCHLIST TABLE - Stocks users are monitoring
CREATE TABLE watchlist (
    watchlist_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_stock (user_id, stock_id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. ALERTS TABLE - Price alerts set by users
CREATE TABLE alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    condition_type ENUM('above', 'below') NOT NULL,
    target_price DECIMAL(10, 2) NOT NULL CHECK (target_price > 0),
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_stock_active (stock_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. AUDIT_LOG TABLE - Track important user actions
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INT,
    action_details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action_type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert some default sectors
INSERT INTO sectors (sector_name, description) VALUES
('Technology', 'Technology and software companies'),
('Healthcare', 'Healthcare and pharmaceutical companies'),
('Financials', 'Banks, insurance, and financial services'),
('Consumer Cyclical', 'Retail and consumer discretionary'),
('Industrials', 'Manufacturing and industrial companies'),
('Energy', 'Oil, gas, and renewable energy'),
('Communication Services', 'Telecommunications and media'),
('Consumer Defensive', 'Food, beverage, and consumer staples'),
('Real Estate', 'Real estate investment trusts and property'),
('Utilities', 'Electric, gas, and water utilities'),
('Basic Materials', 'Mining, chemicals, and raw materials');
