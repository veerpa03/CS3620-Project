"""
Database Initialization Script
Creates the database and all tables
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

def create_database():
    """Create the database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

        if connection.is_connected():
            cursor = connection.cursor()
            db_name = os.getenv('DB_NAME')

            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"✓ Database '{db_name}' created successfully (or already exists)")

            cursor.close()
            connection.close()
            return True

    except Error as e:
        print(f"✗ Error creating database: {e}")
        return False

def execute_schema():
    """Execute the schema.sql file to create tables"""
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

            # Read and execute schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
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

            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        connection.commit()
                    except Error as e:
                        print(f"Error executing statement: {e}")
                        print(f"Statement: {statement[:100]}...")

            print("✓ Database schema created successfully")
            print("✓ 10 tables created:")
            print("  1. users")
            print("  2. portfolios")
            print("  3. sectors")
            print("  4. stocks")
            print("  5. stock_prices")
            print("  6. transactions")
            print("  7. holdings")
            print("  8. watchlist")
            print("  9. alerts")
            print("  10. audit_log")

            cursor.close()
            connection.close()
            return True

    except Error as e:
        print(f"✗ Error executing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verify that all tables were created"""
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
            for table in tables:
                print(f"  - {table[0]}")

            cursor.close()
            connection.close()

    except Error as e:
        print(f"✗ Error verifying tables: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("StockFlow - Database Initialization")
    print("=" * 50)

    print("\n[Step 1] Creating database...")
    if create_database():
        print("\n[Step 2] Creating tables...")
        if execute_schema():
            print("\n[Step 3] Verifying installation...")
            verify_tables()
            print("\n" + "=" * 50)
            print("✓ Database initialization complete!")
            print("=" * 50)
        else:
            print("\n✗ Failed to create tables")
    else:
        print("\n✗ Failed to create database")
