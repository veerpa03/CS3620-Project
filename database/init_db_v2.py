"""
Database Initialization Script v2.0 - Checkpoint 2
Creates 20 tables
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from dotenv import load_dotenv

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def execute_schema_v2():
    """Execute the schema_v2.sql file to create all 20 tables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Read and execute schema_v2.sql
            schema_path = os.path.join(os.path.dirname(__file__), 'schema_v2.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Remove comments and split by semicolon
            lines = []
            for line in sql_script.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    lines.append(line)

            sql_clean = ' '.join(lines)
            statements = sql_clean.split(';')

            print("Creating 20 tables...")
            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        connection.commit()
                    except Error as e:
                        if 'already exists' not in str(e):
                            print(f"Warning: {e}")

            print("\n✓ Database schema created successfully")
            print("\n✓ 20 tables created:")
            print("  Checkpoint 1 Tables (1-10):")
            print("    1. users")
            print("    2. portfolios")
            print("    3. sectors")
            print("    4. stocks")
            print("    5. stock_prices")
            print("    6. transactions")
            print("    7. holdings")
            print("    8. watchlist")
            print("    9. alerts")
            print("    10. audit_log")
            print("\n  Checkpoint 2 Tables (11-20):")
            print("    11. user_preferences")
            print("    12. dividends")
            print("    13. stock_splits")
            print("    14. portfolio_history")
            print("    15. notifications")
            print("    16. transaction_fees")
            print("    17. market_indices")
            print("    18. stock_fundamentals")
            print("    19. trade_orders")
            print("    20. session_logs")

            cursor.close()
            connection.close()
            return True

    except Error as e:
        print(f"✗ Error executing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verify that all 20 tables were created"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            print(f"\n✓ Found {len(tables)} tables in database:")
            for table in sorted(tables):
                print(f"  - {table[0]}")

            cursor.close()
            connection.close()

    except Error as e:
        print(f"✗ Error verifying tables: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("StockFlow - Database Initialization v2.0")
    print("Checkpoint 2: Creating 20 Tables")
    print("=" * 60)

    print("\nExecuting schema...")
    if execute_schema_v2():
        print("\nVerifying installation...")
        verify_tables()
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        print("\nNext: Load data with 'python scripts/load_data.py'")
    else:
        print("\n✗ Failed to create tables")
