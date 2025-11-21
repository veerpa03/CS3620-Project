"""
StockFlow - Flask Web Application
Portfolio management and stock tracking system
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'stockflow_secret_key_2024'

# Database connection
def get_db_connection():
    """Create and return database connection"""
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
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def index():
    """Home page - Dashboard"""
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        # Get total stocks
        cursor.execute("SELECT COUNT(*) as count FROM stocks")
        total_stocks = cursor.fetchone()['count']

        # Get total price records
        cursor.execute("SELECT COUNT(*) as count FROM stock_prices")
        total_prices = cursor.fetchone()['count']

        # Get total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']

        # Get total portfolios
        cursor.execute("SELECT COUNT(*) as count FROM portfolios")
        total_portfolios = cursor.fetchone()['count']

        # Get stocks that have price data (AAPL in our case)
        cursor.execute("""
            SELECT s.symbol, s.company_name, sec.sector_name,
                   sp.close_price, sp.price_date
            FROM stocks s
            INNER JOIN sectors sec ON s.sector_id = sec.sector_id
            INNER JOIN (
                SELECT stock_id, close_price, price_date
                FROM stock_prices sp1
                WHERE price_date = (
                    SELECT MAX(price_date)
                    FROM stock_prices sp2
                    WHERE sp2.stock_id = sp1.stock_id
                )
            ) sp ON s.stock_id = sp.stock_id
            ORDER BY sp.price_date DESC
            LIMIT 20
        """)
        stocks = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('index.html',
                             total_stocks=total_stocks,
                             total_prices=total_prices,
                             total_users=total_users,
                             total_portfolios=total_portfolios,
                             stocks=stocks)
    else:
        return "Database connection error", 500

@app.route('/stocks')
def stocks():
    """View all stocks"""
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT s.stock_id, s.symbol, s.company_name,
                   sec.sector_name, s.exchange
            FROM stocks s
            LEFT JOIN sectors sec ON s.sector_id = sec.sector_id
            ORDER BY s.symbol
        """)
        all_stocks = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('stocks.html', stocks=all_stocks)
    else:
        return "Database connection error", 500

@app.route('/stock/<int:stock_id>')
def stock_detail(stock_id):
    """View detailed stock information"""
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        # Get stock info
        cursor.execute("""
            SELECT s.*, sec.sector_name
            FROM stocks s
            LEFT JOIN sectors sec ON s.sector_id = sec.sector_id
            WHERE s.stock_id = %s
        """, (stock_id,))
        stock = cursor.fetchone()

        # Get price history (last 30 days)
        cursor.execute("""
            SELECT price_date, open_price, close_price, high_price, low_price, volume
            FROM stock_prices
            WHERE stock_id = %s
            ORDER BY price_date DESC
            LIMIT 30
        """, (stock_id,))
        prices = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('stock_detail.html', stock=stock, prices=prices)
    else:
        return "Database connection error", 500

@app.route('/portfolios')
def portfolios():
    """View all portfolios"""
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT p.*, u.email, u.first_name, u.last_name,
                   (SELECT COUNT(*) FROM holdings h WHERE h.portfolio_id = p.portfolio_id) as holdings_count
            FROM portfolios p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.created_at DESC
        """)
        all_portfolios = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('portfolios.html', portfolios=all_portfolios)
    else:
        return "Database connection error", 500

@app.route('/watchlist')
def watchlist():
    """View watchlist"""
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        # Get demo user's watchlist
        cursor.execute("""
            SELECT w.*, s.symbol, s.company_name, sec.sector_name
            FROM watchlist w
            JOIN stocks s ON w.stock_id = s.stock_id
            LEFT JOIN sectors sec ON s.sector_id = sec.sector_id
            ORDER BY w.added_date DESC
        """)
        watchlist_items = cursor.fetchall()

        # Get all stocks for adding to watchlist
        cursor.execute("""
            SELECT stock_id, symbol, company_name
            FROM stocks
            ORDER BY symbol
        """)
        all_stocks = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('watchlist.html',
                             watchlist=watchlist_items,
                             stocks=all_stocks)
    else:
        return "Database connection error", 500

@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    stock_id = request.form.get('stock_id')
    notes = request.form.get('notes', '')

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

        # Get demo user ID
        cursor.execute("SELECT user_id FROM users WHERE email = 'demo@stockflow.com'")
        result = cursor.fetchone()
        user_id = result[0] if result else 1

        try:
            cursor.execute("""
                INSERT INTO watchlist (user_id, stock_id, notes)
                VALUES (%s, %s, %s)
            """, (user_id, stock_id, notes))

            connection.commit()
            flash('Stock added to watchlist!', 'success')
        except Error as e:
            flash(f'Error: Stock already in watchlist or invalid stock', 'error')

        cursor.close()
        connection.close()

    return redirect(url_for('watchlist'))

@app.route('/remove_from_watchlist/<int:watchlist_id>')
def remove_from_watchlist(watchlist_id):
    """Remove stock from watchlist"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM watchlist WHERE watchlist_id = %s", (watchlist_id,))
        connection.commit()

        cursor.close()
        connection.close()

        flash('Stock removed from watchlist!', 'success')

    return redirect(url_for('watchlist'))

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        # Sector distribution
        cursor.execute("""
            SELECT sec.sector_name, COUNT(*) as count
            FROM stocks s
            JOIN sectors sec ON s.sector_id = sec.sector_id
            GROUP BY sec.sector_name
            ORDER BY count DESC
        """)
        sector_distribution = cursor.fetchall()

        # Top stocks by trading volume (recent)
        cursor.execute("""
            SELECT s.symbol, s.company_name, AVG(sp.volume) as avg_volume
            FROM stock_prices sp
            JOIN stocks s ON sp.stock_id = s.stock_id
            WHERE sp.price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY s.stock_id, s.symbol, s.company_name
            ORDER BY avg_volume DESC
            LIMIT 10
        """)
        top_volume_stocks = cursor.fetchall()

        # Price volatility (stocks with highest price variance)
        cursor.execute("""
            SELECT s.symbol, s.company_name,
                   MAX(sp.high_price) - MIN(sp.low_price) as price_range,
                   AVG(sp.close_price) as avg_price
            FROM stock_prices sp
            JOIN stocks s ON sp.stock_id = s.stock_id
            WHERE sp.price_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY s.stock_id, s.symbol, s.company_name
            HAVING avg_price > 0
            ORDER BY price_range DESC
            LIMIT 10
        """)
        volatile_stocks = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('analytics.html',
                             sector_distribution=sector_distribution,
                             top_volume_stocks=top_volume_stocks,
                             volatile_stocks=volatile_stocks)
    else:
        return "Database connection error", 500

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
