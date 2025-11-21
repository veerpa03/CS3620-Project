@echo off
echo ============================================================
echo StockFlow - Quick Setup Script
echo ============================================================
echo.

echo Step 1: Installing Python dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Initializing database...
python database\init_db.py
echo.

echo Step 3: Downloading datasets (this may take 5-10 minutes)...
python scripts\download_data.py
echo.

echo Step 4: Loading data into database...
python scripts\load_data.py
echo.

echo ============================================================
echo Setup complete! To run the application:
echo   cd app
echo   python app.py
echo.
echo Then open: http://localhost:5000
echo ============================================================
pause
