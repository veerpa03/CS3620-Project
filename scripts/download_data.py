"""
Download datasets using Wikipedia and yfinance
No Kaggle account needed!
"""

import yfinance as yf
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import requests

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def get_sp500_list():
    """Get list of S&P 500 companies from Wikipedia (Dataset 1)"""
    print("\n[1/3] Fetching S&P 500 company list from Wikipedia...")
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

        # Add headers to avoid 403 error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Use StringIO to avoid FutureWarning
        from io import StringIO
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        # The S&P 500 table is the second table (index 1)
        sp500_table = tables[1]

        # Save to CSV
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)

        output_file = os.path.join(data_dir, 'sp500_companies.csv')
        sp500_table.to_csv(output_file, index=False)

        print(f"✓ S&P 500 companies saved to: {output_file}")
        print(f"  Total companies: {len(sp500_table)}")

        return sp500_table['Symbol'].tolist(), output_file
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None

def download_stock_prices(symbols, days=365):
    """Download stock price data using yfinance (Dataset 2)"""
    print(f"\n[2/3] Downloading stock price data for {len(symbols)} stocks...")
    print("  This will take 5-10 minutes...")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    all_prices = []
    successful = 0
    failed = 0

    for i, symbol in enumerate(symbols, 1):
        try:
            # Download data for the last year
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)

            if not hist.empty:
                hist['Symbol'] = symbol
                hist['Date'] = hist.index
                all_prices.append(hist)
                successful += 1
                if i % 10 == 0:
                    print(f"  Progress: {i}/{len(symbols)} stocks ({successful} successful, {failed} failed)")
            else:
                failed += 1

        except Exception as e:
            failed += 1

    if all_prices:
        # Combine all data
        combined_df = pd.concat(all_prices, ignore_index=True)

        # Save to CSV
        output_file = os.path.join(data_dir, 'stock_prices.csv')
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Stock prices saved to: {output_file}")
        print(f"  Total records: {len(combined_df)}")
        print(f"  Successful: {successful} stocks, Failed: {failed} stocks")
        return output_file
    else:
        print("\n✗ No stock price data downloaded")
        return None

def download_company_info(symbols):
    """Download detailed company info using yfinance (Dataset 3)"""
    print(f"\n[3/3] Fetching detailed company information...")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    company_data = []
    successful = 0

    # Get info for first 50 stocks to keep it fast
    sample_symbols = symbols[:50]

    for i, symbol in enumerate(sample_symbols, 1):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            company_data.append({
                'Symbol': symbol,
                'Name': info.get('longName', ''),
                'Sector': info.get('sector', ''),
                'Industry': info.get('industry', ''),
                'MarketCap': info.get('marketCap', 0),
                'Country': info.get('country', 'USA'),
                'Website': info.get('website', ''),
                'Description': info.get('longBusinessSummary', '')[:500] if info.get('longBusinessSummary') else ''
            })
            successful += 1

            if i % 10 == 0:
                print(f"  Progress: {i}/{len(sample_symbols)} companies")

        except Exception as e:
            pass

    if company_data:
        df = pd.DataFrame(company_data)
        output_file = os.path.join(data_dir, 'company_info.csv')
        df.to_csv(output_file, index=False)
        print(f"\n✓ Company info saved to: {output_file}")
        print(f"  Total companies: {len(df)}")
        return output_file
    else:
        print("\n✗ No company info downloaded")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("StockFlow - Data Download Script")
    print("=" * 60)
    print("\nThis will download 3 datasets:")
    print("  1. S&P 500 company list (Wikipedia)")
    print("  2. Historical stock prices (Yahoo Finance)")
    print("  3. Detailed company information (Yahoo Finance)")
    print("\nEstimated time: 5-10 minutes")
    print("=" * 60)

    # Dataset 1: Get S&P 500 list from Wikipedia
    symbols, sp500_file = get_sp500_list()

    if symbols:
        # Dataset 2: Download price data for top 50 stocks (to keep it manageable)
        top_symbols = symbols[:50]
        print(f"\nDownloading price data for top {len(top_symbols)} stocks...")
        price_file = download_stock_prices(top_symbols, days=365)

        # Dataset 3: Download detailed company info
        info_file = download_company_info(top_symbols)

    print("\n" + "=" * 60)
    print("✓ Data download complete!")
    print("=" * 60)
    print("\nDownloaded files:")
    if sp500_file:
        print(f"  1. S&P 500 companies: {sp500_file}")
    if 'price_file' in locals() and price_file:
        print(f"  2. Stock prices: {price_file}")
    if 'info_file' in locals() and info_file:
        print(f"  3. Company info: {info_file}")

    print("\nNext step: Run 'python scripts/load_data.py' to load data into MySQL")
