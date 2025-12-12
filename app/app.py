"""
StockFlow - Flask Web Application
Portfolio management and stock tracking system
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps
import hashlib

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

# Authentication decorator
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def log_audit(user_id, action_type, table_name, record_id, action_details, ip_address):
    """Log user actions to audit_log table"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO audit_log (user_id, action_type, table_name, record_id, action_details, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, action_type, table_name, record_id, action_details, ip_address))
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            print(f"Error logging audit: {e}")

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_hash = hash_password(password)

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT user_id, email, first_name, last_name, status
                FROM users
                WHERE email = %s AND password_hash = %s
            """, (email, password_hash))
            user = cursor.fetchone()

            if user and user['status'] == 'active':
                session['user_id'] = user['user_id']
                session['user_email'] = user['email']
                session['user_name'] = f"{user['first_name']} {user['last_name']}"

                # Log session in session_logs table
                cursor.execute("""
                    INSERT INTO session_logs (user_id, ip_address, user_agent)
                    VALUES (%s, %s, %s)
                """, (user['user_id'], request.remote_addr, request.headers.get('User-Agent')))
                session['session_id'] = cursor.lastrowid

                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = NOW()
                    WHERE user_id = %s
                """, (user['user_id'],))

                connection.commit()

                # Log audit
                log_audit(user['user_id'], 'LOGIN', 'users', user['user_id'],
                         'User logged in', request.remote_addr)

                flash(f'Welcome back, {user["first_name"]}!', 'success')
                cursor.close()
                connection.close()
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')

            cursor.close()
            connection.close()

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        # Basic validation
        if not email or not password or not first_name or not last_name:
            flash('All fields are required', 'error')
            return render_template('register.html')

        password_hash = hash_password(password)

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (email, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                """, (email, password_hash, first_name, last_name))
                user_id = cursor.lastrowid

                # Create default portfolio for new user
                cursor.execute("""
                    INSERT INTO portfolios (user_id, portfolio_name, description)
                    VALUES (%s, 'Default Portfolio', 'Your main investment portfolio')
                """, (user_id,))

                # Create default preferences
                cursor.execute("""
                    INSERT INTO user_preferences (user_id)
                    VALUES (%s)
                """, (user_id,))

                connection.commit()

                # Log audit
                log_audit(user_id, 'REGISTER', 'users', user_id,
                         'New user registered', request.remote_addr)

                flash('Registration successful! Please log in.', 'success')
                cursor.close()
                connection.close()
                return redirect(url_for('login'))
            except Error as e:
                flash(f'Error: Email already exists or invalid data', 'error')
                cursor.close()
                connection.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    if 'user_id' in session:
        user_id = session['user_id']
        session_id = session.get('session_id')

        # Update session log
        if session_id:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE session_logs
                    SET logout_time = NOW(), is_active = FALSE
                    WHERE session_id = %s
                """, (session_id,))
                connection.commit()
                cursor.close()
                connection.close()

        # Log audit
        log_audit(user_id, 'LOGOUT', 'users', user_id,
                 'User logged out', request.remote_addr)

        session.clear()
        flash('You have been logged out.', 'success')

    return redirect(url_for('login'))

# ==================== PUBLIC ROUTES ====================

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
    """READ: View all stocks with FILTER"""
    sector_filter = request.args.get('sector', '')
    search = request.args.get('search', '')

    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        # Build query with filters
        query = """
            SELECT s.stock_id, s.symbol, s.company_name,
                   sec.sector_name, s.exchange
            FROM stocks s
            LEFT JOIN sectors sec ON s.sector_id = sec.sector_id
            WHERE 1=1
        """
        params = []

        if sector_filter:
            query += " AND sec.sector_name = %s"
            params.append(sector_filter)

        if search:
            query += " AND (s.symbol LIKE %s OR s.company_name LIKE %s)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        query += " ORDER BY s.symbol LIMIT 100"

        cursor.execute(query, params)
        all_stocks = cursor.fetchall()

        # Get all sectors for filter dropdown
        cursor.execute("SELECT DISTINCT sector_name FROM sectors ORDER BY sector_name")
        sectors = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('stocks.html',
                             stocks=all_stocks,
                             sectors=sectors,
                             sector_filter=sector_filter,
                             search=search)
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
@login_required
def watchlist():
    """View watchlist"""
    connection = get_db_connection()
    user_id = session.get('user_id')

    if connection:
        cursor = connection.cursor(dictionary=True)

        # Get logged-in user's watchlist
        cursor.execute("""
            SELECT w.*, s.symbol, s.company_name, sec.sector_name
            FROM watchlist w
            JOIN stocks s ON w.stock_id = s.stock_id
            LEFT JOIN sectors sec ON s.sector_id = sec.sector_id
            WHERE w.user_id = %s
            ORDER BY w.added_date DESC
        """, (user_id,))
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
@login_required
def add_to_watchlist():
    """Add stock to watchlist"""
    stock_id = request.form.get('stock_id')
    notes = request.form.get('notes', '')
    user_id = session.get('user_id')

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

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
@login_required
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

# ==================== STOCKS CRUD (Checkpoint 2) ====================

@app.route('/stock/add', methods=['GET', 'POST'])
@login_required
def add_stock():
    """CREATE: Add new stock"""
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').upper()
        company_name = request.form.get('company_name')
        sector_id = request.form.get('sector_id')
        exchange = request.form.get('exchange')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO stocks (symbol, company_name, sector_id, exchange)
                    VALUES (%s, %s, %s, %s)
                """, (symbol, company_name, sector_id, exchange))
                connection.commit()
                flash(f'Stock {symbol} added successfully!', 'success')
                return redirect(url_for('stocks'))
            except Error as e:
                flash(f'Error: {str(e)}', 'error')
            cursor.close()
            connection.close()

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sectors ORDER BY sector_name")
        sectors = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('stock_add.html', sectors=sectors)
    return redirect(url_for('stocks'))

@app.route('/stock/edit/<int:stock_id>', methods=['GET', 'POST'])
@login_required
def edit_stock(stock_id):
    """UPDATE: Edit existing stock"""
    connection = get_db_connection()

    if request.method == 'POST':
        company_name = request.form.get('company_name')
        sector_id = request.form.get('sector_id')
        exchange = request.form.get('exchange')

        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    UPDATE stocks SET company_name=%s, sector_id=%s, exchange=%s
                    WHERE stock_id=%s
                """, (company_name, sector_id, exchange, stock_id))
                connection.commit()
                flash('Stock updated successfully!', 'success')
                return redirect(url_for('stock_detail', stock_id=stock_id))
            except Error as e:
                flash(f'Error: {str(e)}', 'error')
            cursor.close()
            connection.close()

    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stocks WHERE stock_id=%s", (stock_id,))
        stock = cursor.fetchone()
        cursor.execute("SELECT * FROM sectors ORDER BY sector_name")
        sectors = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('stock_edit.html', stock=stock, sectors=sectors)
    return redirect(url_for('stocks'))

@app.route('/stock/delete/<int:stock_id>')
@login_required
def delete_stock(stock_id):
    """DELETE: Remove stock"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM stocks WHERE stock_id=%s", (stock_id,))
            connection.commit()
            flash('Stock deleted successfully!', 'success')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
        cursor.close()
        connection.close()
    return redirect(url_for('stocks'))

# ==================== TRANSACTIONS CRUD (Checkpoint 2) ====================

@app.route('/transactions')
def transactions():
    """READ: View all transactions with filter"""
    portfolio_filter = request.args.get('portfolio', '')
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT t.*, s.symbol, s.company_name, p.portfolio_name
            FROM transactions t
            JOIN stocks s ON t.stock_id=s.stock_id
            JOIN portfolios p ON t.portfolio_id=p.portfolio_id
            WHERE 1=1
        """
        params = []
        if portfolio_filter:
            query += " AND t.portfolio_id=%s"
            params.append(portfolio_filter)
        query += " ORDER BY t.transaction_date DESC LIMIT 50"

        cursor.execute(query, params)
        all_transactions = cursor.fetchall()

        cursor.execute("SELECT portfolio_id, portfolio_name FROM portfolios")
        portfolios_list = cursor.fetchall()

        cursor.close()
        connection.close()
        return render_template('transactions.html',
                             transactions=all_transactions,
                             portfolios=portfolios_list,
                             portfolio_filter=portfolio_filter)
    return "Database error", 500

@app.route('/transaction/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """CREATE: Add new transaction"""
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        stock_id = request.form.get('stock_id')
        transaction_type = request.form.get('transaction_type')
        quantity = int(request.form.get('quantity'))
        price_per_share = float(request.form.get('price_per_share'))
        fees = float(request.form.get('fees', 0))
        notes = request.form.get('notes', '')
        total_amount = (quantity * price_per_share) + fees

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO transactions
                    (portfolio_id, stock_id, transaction_type, quantity,
                     price_per_share, total_amount, fees, notes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (portfolio_id, stock_id, transaction_type, quantity,
                       price_per_share, total_amount, fees, notes))
                connection.commit()
                flash('Transaction added successfully!', 'success')
                return redirect(url_for('transactions'))
            except Error as e:
                flash(f'Error: {str(e)}', 'error')
            cursor.close()
            connection.close()

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT portfolio_id, portfolio_name FROM portfolios WHERE is_active=TRUE")
        portfolios_list = cursor.fetchall()
        cursor.execute("SELECT stock_id, symbol, company_name FROM stocks ORDER BY symbol LIMIT 200")
        stocks_list = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('transaction_add.html',
                             portfolios=portfolios_list, stocks=stocks_list)
    return redirect(url_for('transactions'))

@app.route('/transaction/delete/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    """DELETE: Remove transaction"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM transactions WHERE transaction_id=%s", (transaction_id,))
            connection.commit()
            flash('Transaction deleted successfully!', 'success')
        except Error as e:
            flash(f'Error: {str(e)}', 'error')
        cursor.close()
        connection.close()
    return redirect(url_for('transactions'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
