-- StockFlow Database Schema v2.0 - CHECKPOINT 2
-- 20 Tables Total (10 existing + 10 new)

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS session_logs;
DROP TABLE IF EXISTS trade_orders;
DROP TABLE IF EXISTS stock_fundamentals;
DROP TABLE IF EXISTS market_indices;
DROP TABLE IF EXISTS transaction_fees;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS portfolio_history;
DROP TABLE IF EXISTS stock_splits;
DROP TABLE IF EXISTS dividends;
DROP TABLE IF EXISTS user_preferences;
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

-- ============================================================
-- EXISTING TABLES (1-10) - From Checkpoint 1
-- ============================================================

-- 1. USERS TABLE
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

-- 2. PORTFOLIOS TABLE
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

-- 3. SECTORS TABLE
CREATE TABLE sectors (
    sector_id INT PRIMARY KEY AUTO_INCREMENT,
    sector_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. STOCKS TABLE
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

-- 5. STOCK_PRICES TABLE
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

-- 6. TRANSACTIONS TABLE
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

-- 7. HOLDINGS TABLE
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

-- 8. WATCHLIST TABLE
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

-- 9. ALERTS TABLE
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

-- 10. AUDIT_LOG TABLE
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

-- ============================================================
-- NEW TABLES (11-20) - For Checkpoint 2
-- ============================================================

-- 11. USER_PREFERENCES TABLE
CREATE TABLE user_preferences (
    preference_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    theme VARCHAR(20) DEFAULT 'light',
    currency VARCHAR(10) DEFAULT 'USD',
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    email_notifications BOOLEAN DEFAULT TRUE,
    price_alert_emails BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'en',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. DIVIDENDS TABLE
CREATE TABLE dividends (
    dividend_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    ex_date DATE NOT NULL,
    payment_date DATE,
    amount DECIMAL(10, 4) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    frequency VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_date (stock_id, ex_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. STOCK_SPLITS TABLE
CREATE TABLE stock_splits (
    split_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    split_date DATE NOT NULL,
    split_ratio VARCHAR(20) NOT NULL,
    split_from INT NOT NULL,
    split_to INT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_stock_date (stock_id, split_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. PORTFOLIO_HISTORY TABLE
CREATE TABLE portfolio_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT NOT NULL,
    snapshot_date DATE NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    cash_balance DECIMAL(15, 2) NOT NULL,
    total_invested DECIMAL(15, 2) NOT NULL,
    total_gain_loss DECIMAL(15, 2),
    gain_loss_percentage DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_date (portfolio_id, snapshot_date),
    INDEX idx_portfolio_date (portfolio_id, snapshot_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. NOTIFICATIONS TABLE
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    notification_type ENUM('alert', 'transaction', 'system', 'dividend') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 16. TRANSACTION_FEES TABLE
CREATE TABLE transaction_fees (
    fee_id INT PRIMARY KEY AUTO_INCREMENT,
    fee_name VARCHAR(100) NOT NULL,
    fee_type ENUM('flat', 'percentage', 'tiered') NOT NULL,
    amount DECIMAL(10, 2),
    percentage DECIMAL(5, 4),
    min_amount DECIMAL(10, 2),
    max_amount DECIMAL(10, 2),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 17. MARKET_INDICES TABLE
CREATE TABLE market_indices (
    index_id INT PRIMARY KEY AUTO_INCREMENT,
    index_name VARCHAR(100) NOT NULL,
    index_symbol VARCHAR(20) UNIQUE NOT NULL,
    index_date DATE NOT NULL,
    open_value DECIMAL(10, 2),
    close_value DECIMAL(10, 2) NOT NULL,
    high_value DECIMAL(10, 2),
    low_value DECIMAL(10, 2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_index_date (index_symbol, index_date),
    INDEX idx_symbol_date (index_symbol, index_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 18. STOCK_FUNDAMENTALS TABLE
CREATE TABLE stock_fundamentals (
    fundamental_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    report_date DATE NOT NULL,
    pe_ratio DECIMAL(10, 2),
    eps DECIMAL(10, 2),
    market_cap BIGINT,
    revenue BIGINT,
    net_income BIGINT,
    dividend_yield DECIMAL(5, 2),
    beta DECIMAL(10, 2),
    fifty_two_week_high DECIMAL(10, 2),
    fifty_two_week_low DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    UNIQUE KEY unique_stock_report (stock_id, report_date),
    INDEX idx_stock_date (stock_id, report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 19. TRADE_ORDERS TABLE
CREATE TABLE trade_orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT NOT NULL,
    stock_id INT NOT NULL,
    order_type ENUM('market', 'limit', 'stop', 'stop_limit') NOT NULL,
    action ENUM('buy', 'sell') NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    limit_price DECIMAL(10, 2),
    stop_price DECIMAL(10, 2),
    status ENUM('pending', 'executed', 'cancelled', 'expired') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    INDEX idx_portfolio_status (portfolio_id, status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 20. SESSION_LOGS TABLE
CREATE TABLE session_logs (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_token VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_active (user_id, is_active),
    INDEX idx_login (login_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default sectors
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

-- Insert default transaction fees
INSERT INTO transaction_fees (fee_name, fee_type, amount, description, is_active) VALUES
('Standard Trading Fee', 'flat', 9.99, 'Standard fee for buy/sell transactions', TRUE),
('Premium Trading Fee', 'flat', 4.99, 'Reduced fee for premium members', TRUE),
('Zero Commission', 'flat', 0.00, 'No commission trading', TRUE);
