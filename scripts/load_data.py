"""
Load CSV data into MySQL database
Works with your 3 downloaded CSV files
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"✗ Error connecting to database: {e}")
        return None

def load_sp500_companies():
    """Load S&P 500 companies into stocks table (Dataset 1)"""
    print("\n[1/3] Loading S&P 500 companies...")

    csv_file = os.path.join('data', 'sp500_companies.csv')

    if not os.path.exists(csv_file):
        print(f"✗ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file)
        connection = get_db_connection()

        if connection:
            cursor = connection.cursor()

            # Get sector mapping
            sector_map = {}
            cursor.execute("SELECT sector_id, sector_name FROM sectors")
            for sector_id, sector_name in cursor.fetchall():
                sector_map[sector_name] = sector_id

            inserted = 0
            for _, row in df.iterrows():
                try:
                    # Map GICS Sector to our sector_id
                    gics_sector = row.get('GICS Sector', 'Technology')
                    sector_id = sector_map.get(gics_sector, 1)  # Default to Technology

                    sql = """
                    INSERT INTO stocks (symbol, company_name, sector_id, exchange)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        company_name = VALUES(company_name),
                        sector_id = VALUES(sector_id)
                    """

                    values = (
                        row.get('Symbol', ''),
                        row.get('Security', ''),
                        sector_id,
                        'NYSE/NASDAQ'
                    )

                    cursor.execute(sql, values)
                    inserted += 1

                except Exception as e:
                    pass

            connection.commit()
            print(f"✓ Loaded {inserted} S&P 500 companies")

            cursor.close()
            connection.close()
            return True

    except Exception as e:
        print(f"✗ Error loading S&P 500 companies: {e}")
        return False

def load_nasdaq_companies():
    """Load NASDAQ companies into stocks table (Dataset 2)"""
    print("\n[2/3] Loading NASDAQ companies...")

    csv_file = os.path.join('data', 'nasdaq_companies.csv')

    if not os.path.exists(csv_file):
        print(f"✗ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file)
        connection = get_db_connection()

        if connection:
            cursor = connection.cursor()

            inserted = 0
            # Load first 100 NASDAQ companies
            for _, row in df.head(100).iterrows():
                try:
                    sql = """
                    INSERT INTO stocks (symbol, company_name, sector_id, exchange)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        company_name = VALUES(company_name)
                    """

                    values = (
                        row.get('Symbol', ''),
                        row.get('Security Name', ''),
                        1,  # Default to Technology sector
                        'NASDAQ'
                    )

                    cursor.execute(sql, values)
                    inserted += 1

                except Exception as e:
                    pass

            connection.commit()
            print(f"✓ Loaded {inserted} NASDAQ companies")

            cursor.close()
            connection.close()
            return True

    except Exception as e:
        print(f"✗ Error loading NASDAQ companies: {e}")
        return False

def load_stock_prices():
    """Load AAPL stock prices into stock_prices table (Dataset 3)"""
    print("\n[3/3] Loading stock prices (AAPL)...")

    csv_file = os.path.join('data', 'stock_prices.csv')

    if not os.path.exists(csv_file):
        print(f"✗ File not found: {csv_file}")
        return False

    try:
        df = pd.read_csv(csv_file)
        connection = get_db_connection()

        if connection:
            cursor = connection.cursor()

            # Get AAPL stock_id
            cursor.execute("SELECT stock_id FROM stocks WHERE symbol = 'AAPL'")
            result = cursor.fetchone()

            if not result:
                # Insert AAPL if it doesn't exist
                cursor.execute("""
                    INSERT INTO stocks (symbol, company_name, sector_id, exchange)
                    VALUES ('AAPL', 'Apple Inc.', 1, 'NASDAQ')
                """)
                connection.commit()
                stock_id = cursor.lastrowid
            else:
                stock_id = result[0]

            inserted = 0
            for _, row in df.iterrows():
                try:
                    # Parse date
                    date_str = row.get('Date', '')
                    if pd.isna(date_str):
                        continue

                    price_date = pd.to_datetime(date_str).date()

                    sql = """
                    INSERT INTO stock_prices
                    (stock_id, price_date, open_price, close_price, high_price, low_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        open_price = VALUES(open_price),
                        close_price = VALUES(close_price)
                    """

                    values = (
                        stock_id,
                        price_date,
                        float(row.get('AAPL.Open', 0)) if not pd.isna(row.get('AAPL.Open')) else None,
                        float(row.get('AAPL.Close', 0)) if not pd.isna(row.get('AAPL.Close')) else None,
                        float(row.get('AAPL.High', 0)) if not pd.isna(row.get('AAPL.High')) else None,
                        float(row.get('AAPL.Low', 0)) if not pd.isna(row.get('AAPL.Low')) else None,
                        int(row.get('AAPL.Volume', 0)) if not pd.isna(row.get('AAPL.Volume')) else None
                    )

                    cursor.execute(sql, values)
                    inserted += 1

                    if inserted % 100 == 0:
                        print(f"  Progress: {inserted} price records...", end='\r')

                except Exception as e:
                    continue

            connection.commit()
            print(f"\n✓ Loaded {inserted} price records for AAPL")

            cursor.close()
            connection.close()
            return True

    except Exception as e:
        print(f"✗ Error loading stock prices: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_user():
    """Create a sample user and portfolio for demo"""
    print("\n[4/4] Creating demo user and portfolio...")

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            # Create demo user
            sql_user = """
            INSERT INTO users (email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE user_id=LAST_INSERT_ID(user_id)
            """
            cursor.execute(sql_user, ('demo@stockflow.com', 'demo123', 'Demo', 'User'))
            user_id = cursor.lastrowid if cursor.lastrowid else 1

            # Create demo portfolio
            cursor.execute("SELECT portfolio_id FROM portfolios WHERE user_id = %s", (user_id,))
            if not cursor.fetchone():
                sql_portfolio = """
                INSERT INTO portfolios (user_id, portfolio_name, description, initial_cash, current_cash)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_portfolio, (
                    user_id,
                    'My First Portfolio',
                    'Demo portfolio for testing',
                    100000.00,
                    100000.00
                ))

            connection.commit()
            print(f"✓ Created demo user and portfolio")

            cursor.close()
            connection.close()
            return True

    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False

def show_summary():
    """Show summary of loaded data"""
    print("\n" + "=" * 60)
    print("Database Summary")
    print("=" * 60)

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()

            tables = [
                ('users', 'Users'),
                ('portfolios', 'Portfolios'),
                ('sectors', 'Sectors'),
                ('stocks', 'Stocks'),
                ('stock_prices', 'Price Records'),
            ]

            print("\n  Table Name          | Row Count")
            print("  " + "-" * 40)

            for table, label in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {label:18} | {count:>8}")

            cursor.close()
            connection.close()

    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("StockFlow - Data Loading Script")
    print("=" * 60)
    print("\nLoading data from 3 public CSV files:")
    print("  1. sp500_companies.csv (Wikipedia S&P 500)")
    print("  2. nasdaq_companies.csv (NASDAQ listings)")
    print("  3. stock_prices.csv (AAPL historical prices)")
    print("=" * 60)

    load_sp500_companies()
    load_nasdaq_companies()
    load_stock_prices()
    create_sample_user()
    show_summary()

    print("\n" + "=" * 60)
    print("✓ Data loading complete!")
    print("=" * 60)
    print("\nNext step: Run the Flask app")
    print("  cd app")
    print("  python app.py")
