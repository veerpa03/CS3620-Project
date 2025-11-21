# StockFlow - Smart Portfolio Tracker

**CS3620 Database Systems - Checkpoint 1**

## Project Overview

StockFlow is a stock portfolio management and tracking system that helps users monitor investments, analyze market trends, and manage their stock watchlists.

## Goal

Create a comprehensive database-driven application for stock portfolio management that integrates multiple public datasets and provides interactive features for users to track and analyze their investments.

## Features & Interactions

### Interactive Features (Write Operations)
-  **Add stocks to watchlist** - Monitor interesting stocks
-  **Remove stocks from watchlist** - Clean up your watchlist
-  **Create user accounts** - Register and manage profiles
-  **Create portfolios** - Organize investments

### Read-Only Features
-  **View stock prices** - Historical daily price data
-  **Portfolio analytics** - Track performance and holdings
-  **Search stocks** - Browse 500+ S&P 500 companies
-  **Market analytics** - Sector distribution, volume leaders, volatility analysis

## Database Schema (10 Tables)

1. **users** - User accounts and authentication
2. **portfolios** - Investment portfolios (1 user can have multiple)
3. **sectors** - Stock industry sectors (Technology, Healthcare, etc.)
4. **stocks** - Master stock information (symbol, company name, sector)
5. **stock_prices** - Historical daily stock prices (OHLCV data)
6. **transactions** - Buy/sell transaction records
7. **holdings** - Current portfolio holdings
8. **watchlist** - Stocks users are monitoring
9. **alerts** - Price alerts set by users
10. **audit_log** - Activity tracking and audit trail

See `ER_DIAGRAM.md` for detailed entity-relationship diagram.

## Public Datasets (3 Sources)

1. **S&P 500 Companies with Financial Information**
   - Source: Kaggle (paytonfisher/sp-500-companies-with-financial-information)
   - Used for: Company information, sectors, fundamentals

2. **Stock Price Data**
   - Source: Yahoo Finance (via yfinance Python library)
   - Used for: Historical daily OHLCV prices

3. **S&P 500 Company List**
   - Source: Wikipedia
   - Used for: Current S&P 500 constituent companies

## Technology Stack

- **Backend:** Python 3.x, Flask
- **Database:** MySQL 8.x
- **Frontend:** HTML5, CSS3
- **Data Processing:** pandas, yfinance, kagglehub
- **Database Connector:** mysql-connector-python

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher (running on localhost:3306)
- Git

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd CS3620-Project
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
# Create database and tables
python database/init_db.py
```

You should see:
```
 Database 'stock_portfolio' created successfully
 Database schema created successfully
 10 tables created
```

### Step 4: Download and Load Data

```bash
# Download datasets (this may take 5-10 minutes)
python scripts/download_data.py

# Load data into database
python scripts/load_data.py
```

Expected output:
```
 Loaded 500+ companies into stocks table
 Loaded 10,000+ price records into stock_prices table
 Created demo user and portfolio
```

### Step 5: Run the Application

```bash
cd app
python app.py
```

The application will start at: **http://localhost:5000**



## ER Diagram

See `ER_DIAGRAM.md` for the complete entity-relationship diagram with:
- All 10 tables
- Primary keys and foreign keys
- Relationships and cardinality
- Column details

## Team Members

- Viraj Parmar
- Dhruv Patel

## License

This project is for educational purposes only.
