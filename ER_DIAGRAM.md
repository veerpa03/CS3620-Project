# StockFlow - Entity Relationship Diagram

## Database Schema Overview (10 Tables)

This document describes the complete database schema with all tables, relationships, and constraints.

---

## Tables

### 1. USERS
**Purpose:** Store user account information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| first_name | VARCHAR(100) | | User's first name |
| last_name | VARCHAR(100) | | User's last name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| last_login | TIMESTAMP | NULL | Last login timestamp |
| status | ENUM | DEFAULT 'active' | Account status (active/inactive/suspended) |

**Indexes:**
- email (UNIQUE)
- status

**Relationships:**
- 1:N with portfolios (one user can have multiple portfolios)
- 1:N with watchlist (one user can watch multiple stocks)
- 1:N with alerts (one user can set multiple alerts)

---

### 2. PORTFOLIOS
**Purpose:** Store investment portfolios

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| portfolio_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique portfolio identifier |
| user_id | INT | FOREIGN KEY → users.user_id, NOT NULL | Owner of the portfolio |
| portfolio_name | VARCHAR(100) | NOT NULL | Portfolio name |
| description | TEXT | | Portfolio description |
| initial_cash | DECIMAL(15,2) | DEFAULT 10000.00 | Starting cash amount |
| current_cash | DECIMAL(15,2) | DEFAULT 10000.00 | Current available cash |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

**Relationships:**
- N:1 with users (many portfolios belong to one user)
- 1:N with transactions (one portfolio has many transactions)
- 1:N with holdings (one portfolio has many holdings)

---

### 3. SECTORS
**Purpose:** Stock industry sector classification

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sector_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique sector identifier |
| sector_name | VARCHAR(100) | UNIQUE, NOT NULL | Sector name (e.g., Technology) |
| description | TEXT | | Sector description |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Default Sectors:**
- Technology
- Healthcare
- Financials
- Consumer Cyclical
- Industrials
- Energy
- Communication Services
- Consumer Defensive
- Real Estate
- Utilities
- Basic Materials

**Relationships:**
- 1:N with stocks (one sector contains many stocks)

---

### 4. STOCKS
**Purpose:** Master stock information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| stock_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique stock identifier |
| symbol | VARCHAR(10) | UNIQUE, NOT NULL | Stock ticker symbol (e.g., AAPL) |
| company_name | VARCHAR(255) | NOT NULL | Full company name |
| sector_id | INT | FOREIGN KEY → sectors.sector_id | Industry sector |
| exchange | VARCHAR(50) | | Exchange (NYSE/NASDAQ) |
| market_cap | BIGINT | | Market capitalization |
| ipo_year | INT | | Initial public offering year |
| country | VARCHAR(100) | DEFAULT 'USA' | Country of origin |
| website | VARCHAR(255) | | Company website |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:**
- symbol (UNIQUE)
- sector_id

**Relationships:**
- N:1 with sectors (many stocks belong to one sector)
- 1:N with stock_prices (one stock has many price records)
- 1:N with transactions (one stock appears in many transactions)
- 1:N with holdings (one stock appears in many holdings)
- N:M with users via watchlist (many-to-many relationship)

---

### 5. STOCK_PRICES
**Purpose:** Historical daily stock price data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| price_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique price record identifier |
| stock_id | INT | FOREIGN KEY → stocks.stock_id, NOT NULL | Reference to stock |
| price_date | DATE | NOT NULL | Trading date |
| open_price | DECIMAL(10,2) | | Opening price |
| close_price | DECIMAL(10,2) | NOT NULL | Closing price |
| high_price | DECIMAL(10,2) | | Highest price of the day |
| low_price | DECIMAL(10,2) | | Lowest price of the day |
| volume | BIGINT | | Trading volume |
| adjusted_close | DECIMAL(10,2) | | Adjusted closing price |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Constraints:**
- UNIQUE (stock_id, price_date) - one price record per stock per day

**Indexes:**
- (stock_id, price_date)
- price_date

**Relationships:**
- N:1 with stocks (many price records belong to one stock)

---

### 6. TRANSACTIONS
**Purpose:** Buy and sell transaction records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| transaction_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique transaction identifier |
| portfolio_id | INT | FOREIGN KEY → portfolios.portfolio_id, NOT NULL | Portfolio reference |
| stock_id | INT | FOREIGN KEY → stocks.stock_id, NOT NULL | Stock reference |
| transaction_type | ENUM | NOT NULL | Type: 'buy' or 'sell' |
| quantity | INT | NOT NULL, CHECK (quantity > 0) | Number of shares |
| price_per_share | DECIMAL(10,2) | NOT NULL, CHECK (price_per_share > 0) | Price per share |
| total_amount | DECIMAL(15,2) | NOT NULL | Total transaction amount |
| fees | DECIMAL(10,2) | DEFAULT 0.00 | Transaction fees |
| transaction_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Transaction timestamp |
| notes | TEXT | | Transaction notes |

**Indexes:**
- portfolio_id
- stock_id
- transaction_date

**Relationships:**
- N:1 with portfolios (many transactions in one portfolio)
- N:1 with stocks (many transactions for one stock)

---

### 7. HOLDINGS
**Purpose:** Current stock holdings per portfolio

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| holding_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique holding identifier |
| portfolio_id | INT | FOREIGN KEY → portfolios.portfolio_id, NOT NULL | Portfolio reference |
| stock_id | INT | FOREIGN KEY → stocks.stock_id, NOT NULL | Stock reference |
| quantity | INT | NOT NULL, DEFAULT 0, CHECK (quantity >= 0) | Current number of shares |
| average_cost_basis | DECIMAL(10,2) | NOT NULL | Average purchase price per share |
| total_invested | DECIMAL(15,2) | NOT NULL | Total amount invested |
| last_updated | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update time |

**Constraints:**
- UNIQUE (portfolio_id, stock_id) - one holding per stock per portfolio

**Indexes:**
- portfolio_id

**Relationships:**
- N:1 with portfolios (many holdings in one portfolio)
- N:1 with stocks (many holdings for one stock)

---

### 8. WATCHLIST
**Purpose:** Stocks users are monitoring (many-to-many bridge table)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| watchlist_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique watchlist entry identifier |
| user_id | INT | FOREIGN KEY → users.user_id, NOT NULL | User reference |
| stock_id | INT | FOREIGN KEY → stocks.stock_id, NOT NULL | Stock reference |
| added_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date added to watchlist |
| notes | TEXT | | User notes about the stock |

**Constraints:**
- UNIQUE (user_id, stock_id) - one entry per user per stock

**Indexes:**
- user_id

**Relationships:**
- N:1 with users (many watchlist entries belong to one user)
- N:1 with stocks (many watchlist entries for one stock)
- Creates N:M relationship between users and stocks

---

### 9. ALERTS
**Purpose:** Price alerts set by users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| alert_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique alert identifier |
| user_id | INT | FOREIGN KEY → users.user_id, NOT NULL | User who set the alert |
| stock_id | INT | FOREIGN KEY → stocks.stock_id, NOT NULL | Stock to monitor |
| condition_type | ENUM | NOT NULL | Alert type: 'above' or 'below' |
| target_price | DECIMAL(10,2) | NOT NULL, CHECK (target_price > 0) | Target price threshold |
| is_active | BOOLEAN | DEFAULT TRUE | Alert active status |
| triggered_at | TIMESTAMP | NULL | When alert was triggered |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Alert creation time |

**Indexes:**
- user_id
- (stock_id, is_active)

**Relationships:**
- N:1 with users (many alerts belong to one user)
- N:1 with stocks (many alerts for one stock)

---

### 10. AUDIT_LOG
**Purpose:** Track important user actions and changes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| log_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique log entry identifier |
| user_id | INT | FOREIGN KEY → users.user_id | User who performed action |
| action_type | VARCHAR(50) | NOT NULL | Type of action performed |
| table_name | VARCHAR(50) | | Affected table name |
| record_id | INT | | Affected record ID |
| action_details | TEXT | | JSON or text details |
| ip_address | VARCHAR(45) | | User's IP address |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Log timestamp |

**Indexes:**
- user_id
- action_type
- created_at

**Relationships:**
- N:1 with users (many log entries per user)

---

## Relationships Summary

### One-to-Many (1:N)
- users → portfolios
- users → watchlist
- users → alerts
- users → audit_log
- portfolios → transactions
- portfolios → holdings
- sectors → stocks
- stocks → stock_prices
- stocks → transactions
- stocks → holdings
- stocks → watchlist
- stocks → alerts

### Many-to-Many (N:M)
- users ↔ stocks (via watchlist bridge table)

---

## ER Diagram (Crow's Foot Notation)

```
USERS ||--o{ PORTFOLIOS : owns
USERS ||--o{ WATCHLIST : monitors
USERS ||--o{ ALERTS : sets
USERS ||--o{ AUDIT_LOG : generates

PORTFOLIOS ||--o{ TRANSACTIONS : contains
PORTFOLIOS ||--o{ HOLDINGS : contains

SECTORS ||--o{ STOCKS : categorizes

STOCKS ||--o{ STOCK_PRICES : has
STOCKS ||--o{ TRANSACTIONS : traded_in
STOCKS ||--o{ HOLDINGS : held_in
STOCKS ||--o{ WATCHLIST : watched_in
STOCKS ||--o{ ALERTS : monitored_in
```

**Legend:**
- `||` = One
- `o{` = Many
- `--` = Relationship line

---

## Data Flow

### Read Operations
1. **View Stocks** → stocks + sectors + stock_prices
2. **View Portfolio** → portfolios + holdings + stocks
3. **View Watchlist** → watchlist + stocks + users
4. **View Analytics** → Aggregate queries on stock_prices, stocks, sectors

### Write Operations
1. **Add to Watchlist** → INSERT into watchlist table
2. **Remove from Watchlist** → DELETE from watchlist table
3. **Create Transaction** → INSERT into transactions + UPDATE holdings
4. **Create Alert** → INSERT into alerts table

---

## Normalization

All tables are in **Third Normal Form (3NF)**:

- **1NF:** All attributes contain atomic values (no repeating groups)
- **2NF:** No partial dependencies (all non-key attributes fully depend on primary key)
- **3NF:** No transitive dependencies (no non-key attribute depends on another non-key attribute)

Example of normalization:
- **stocks** and **sectors** are separated (not storing sector_name in stocks table)
- **stock_prices** are separate from **stocks** (historical data in separate table)
- **holdings** are derived from **transactions** but materialized for performance

---

## Indexes Strategy

### Performance Indexes
- Foreign keys are indexed for JOIN performance
- Frequently queried columns (email, symbol) have indexes
- Date columns (price_date, transaction_date) indexed for range queries

### Unique Indexes
- Business keys that must be unique (email, symbol, stock+date combination)

---

## Constraints Summary

### Data Integrity
- **Primary Keys:** All tables have AUTO_INCREMENT primary keys
- **Foreign Keys:** All relationships enforced with FOREIGN KEY constraints
- **CHECK Constraints:** Quantity, price must be positive
- **UNIQUE Constraints:** Prevent duplicate emails, stock symbols
- **NOT NULL:** Critical fields cannot be null

### Referential Integrity
- **ON DELETE CASCADE:** User deletion cascades to portfolios, watchlist
- **ON DELETE SET NULL:** Sector deletion sets stock.sector_id to NULL

---

This schema provides a solid foundation for Checkpoint 1 and can be easily extended to 20+ tables for the final project.
