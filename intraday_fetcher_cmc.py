#!/usr/bin/env python3
"""
Intraday Token Data Fetcher - CoinMarketCap Edition
Fetches OHLC (Open, High, Low, Close) data with volume for crypto tokens
using CoinMarketCap API.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import argparse
from tabulate import tabulate
import os


class CoinMarketCapFetcher:
    """Fetches intraday token data from CoinMarketCap API"""

    def __init__(self, api_key=None):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.api_key = api_key or os.getenv('CMC_API_KEY')

        if not self.api_key:
            raise Exception("CoinMarketCap API key is required. Set CMC_API_KEY environment variable or pass --api-key")

        self.headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }

        # Map common symbols
        self.symbol_map = {
            'BTCUSDT': 'BTC',
            'ETHUSDT': 'ETH',
            'BNBUSDT': 'BNB',
            'ADAUSDT': 'ADA',
            'SOLUSDT': 'SOL',
            'XRPUSDT': 'XRP',
            'DOTUSDT': 'DOT',
            'DOGEUSDT': 'DOGE',
            'MATICUSDT': 'MATIC',
            'LINKUSDT': 'LINK',
            'AVAXUSDT': 'AVAX',
            'UNIUSDT': 'UNI',
            'ATOMUSDT': 'ATOM',
            'LTCUSDT': 'LTC',
            'ALGOUSDT': 'ALGO',
        }

    def get_symbol(self, symbol):
        """Convert trading pair to CMC symbol"""
        symbol_upper = symbol.upper()

        if symbol_upper in self.symbol_map:
            return self.symbol_map[symbol_upper]

        # Remove USDT/USD suffix
        return symbol_upper.replace('USDT', '').replace('USD', '')

    def fetch_ohlcv_data(self, symbol, time_start, time_end):
        """
        Fetch OHLCV data from CoinMarketCap

        Args:
            symbol: CMC symbol (e.g., 'BTC', 'ETH', 'YOOLDO')
            time_start: Start datetime
            time_end: End datetime

        Returns:
            pandas DataFrame with OHLCV data
        """
        url = f"{self.base_url}/cryptocurrency/quotes/historical"

        # Format dates to ISO format
        params = {
            'symbol': symbol,
            'time_start': time_start.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'time_end': time_end.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'interval': '1d',  # Daily OHLCV
            'convert': 'USD'
        }

        print(f"Fetching OHLC from CMC: {url}")
        print(f"Symbol: {symbol}")
        print(f"Date range: {time_start.date()} to {time_end.date()}")

        response = requests.get(url, headers=self.headers, params=params, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch CMC data: {response.status_code} - {response.text}")

        data = response.json()

        if data['status']['error_code'] != 0:
            raise Exception(f"CMC API error: {data['status']['error_message']}")

        quotes = data['data']['quotes']

        if not quotes:
            raise Exception("No data returned from CoinMarketCap")

        # Parse CMC response into OHLCV format
        ohlcv_data = []
        for quote in quotes:
            timestamp = pd.to_datetime(quote['timestamp'])
            usd_quote = quote['quote']['USD']

            ohlcv_data.append({
                'timestamp': timestamp,
                'open': usd_quote.get('open', usd_quote['price']),
                'high': usd_quote.get('high', usd_quote['price']),
                'low': usd_quote.get('low', usd_quote['price']),
                'close': usd_quote['price'],
                'volume': usd_quote.get('volume_24h', 0)
            })

        df = pd.DataFrame(ohlcv_data)

        # Calculate additional metrics
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = ((df['close'] - df['open']) / df['open'] * 100)
        df['high_low_range'] = df['high'] - df['low']
        df['range_pct'] = ((df['high'] - df['low']) / df['open'] * 100)

        return df

    def get_latest_quote(self, symbol):
        """Get latest quote data for a symbol"""
        url = f"{self.base_url}/cryptocurrency/quotes/latest"
        params = {
            'symbol': symbol,
            'convert': 'USD'
        }

        response = requests.get(url, headers=self.headers, params=params, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch CMC quote: {response.text}")

        data = response.json()

        if data['status']['error_code'] != 0:
            raise Exception(f"CMC API error: {data['status']['error_message']}")

        quote_data = data['data'][symbol]['quote']['USD']
        coin_data = data['data'][symbol]

        return {
            'name': coin_data['name'],
            'symbol': coin_data['symbol'],
            'current_price': quote_data['price'],
            'price_change_24h': quote_data.get('price_change_24h', 0),
            'price_change_pct_24h': quote_data.get('percent_change_24h', 0),
            'high_24h': 0,  # CMC doesn't provide this
            'low_24h': 0,   # CMC doesn't provide this
            'total_volume': quote_data.get('volume_24h', 0),
            'market_cap': quote_data.get('market_cap', 0),
        }

    def calculate_daily_moves(self, df):
        """Calculate intraday moves for each day"""
        df_copy = df.copy()
        df_copy['date'] = df_copy['timestamp'].dt.date

        daily_stats = []

        for date, group in df_copy.groupby('date'):
            day_high = group['high'].max()
            day_low = group['low'].min()
            day_open = group.iloc[0]['open']
            day_close = group.iloc[-1]['close']

            intraday_range = day_high - day_low
            intraday_range_pct = (intraday_range / day_open) * 100

            open_close_move = day_close - day_open
            open_close_pct = (open_close_move / day_open) * 100

            day_volume = group['volume'].sum() if 'volume' in group.columns else 0

            daily_stats.append({
                'date': date,
                'open': day_open,
                'high': day_high,
                'low': day_low,
                'close': day_close,
                'volume': day_volume,
                'intraday_range': intraday_range,
                'intraday_range_pct': intraday_range_pct,
                'open_close_move': open_close_move,
                'open_close_pct': open_close_pct,
            })

        return pd.DataFrame(daily_stats)

    def calculate_average_moves(self, daily_df):
        """Calculate average daily moves"""
        return {
            'avg_intraday_range': daily_df['intraday_range'].mean(),
            'avg_intraday_range_pct': daily_df['intraday_range_pct'].mean(),
            'avg_open_close_move': daily_df['open_close_move'].mean(),
            'avg_open_close_pct': daily_df['open_close_pct'].mean(),
            'max_intraday_range': daily_df['intraday_range'].max(),
            'max_intraday_range_pct': daily_df['intraday_range_pct'].max(),
            'min_intraday_range': daily_df['intraday_range'].min(),
            'min_intraday_range_pct': daily_df['intraday_range_pct'].min(),
            'avg_volume': daily_df['volume'].mean(),
            'max_volume': daily_df['volume'].max(),
            'min_volume': daily_df['volume'].min(),
            'total_volume': daily_df['volume'].sum(),
        }


def display_daily_moves(daily_df):
    """Display daily intraday moves in a formatted table"""
    display_df = daily_df.copy()
    display_df['date'] = display_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Determine decimal places
    avg_price = daily_df['close'].mean()
    if avg_price < 0.01:
        decimals = 6
    elif avg_price < 1:
        decimals = 4
    else:
        decimals = 2

    for col in ['open', 'high', 'low', 'close', 'intraday_range', 'open_close_move']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.{decimals}f}")

    display_df['intraday_range_pct'] = display_df['intraday_range_pct'].apply(lambda x: f"{x:.2f}%")
    display_df['open_close_pct'] = display_df['open_close_pct'].apply(lambda x: f"{x:+.2f}%")

    def format_volume(vol):
        if vol >= 1_000_000_000:
            return f"${vol/1_000_000_000:.2f}B"
        elif vol >= 1_000_000:
            return f"${vol/1_000_000:.2f}M"
        elif vol >= 1_000:
            return f"${vol/1_000:.2f}K"
        else:
            return f"${vol:.2f}"

    display_df['volume'] = display_df['volume'].apply(format_volume)

    display_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'intraday_range', 'intraday_range_pct', 'open_close_pct']
    display_df = display_df[display_cols]

    print("\n" + tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def main():
    parser = argparse.ArgumentParser(
        description='Fetch intraday OHLC data for crypto tokens using CoinMarketCap API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variable (recommended)
  export CMC_API_KEY=your_api_key_here
  python3 intraday_fetcher_cmc.py BTCUSDT --start-date 2026-01-01 --end-date 2026-01-07

  # Using command line parameter
  python3 intraday_fetcher_cmc.py BTCUSDT --api-key YOUR_KEY --start-date 2026-01-01 --end-date 2026-01-07

  # Fetch Yooldo Games data
  python3 intraday_fetcher_cmc.py YOOLDO --start-date 2026-01-01 --end-date 2026-01-11

  # With export
  python3 intraday_fetcher_cmc.py BTCUSDT --start-date 2026-01-01 --end-date 2026-01-07 --csv btc_cmc.csv

Note:
  - Start and end dates are REQUIRED
  - Get your free API key at: https://coinmarketcap.com/api/ (10,000 calls/month)
  - Free tier updates daily, not real-time
        """
    )

    parser.add_argument('symbol', help='Trading pair (BTCUSDT) or CMC symbol (BTC, YOOLDO)')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--api-key', help='CoinMarketCap API key (or set CMC_API_KEY env variable)')
    parser.add_argument('--csv', help='Export data to CSV file')
    parser.add_argument('-e', '--export', help='Export data to JSON file')

    args = parser.parse_args()

    try:
        # Initialize fetcher
        fetcher = CoinMarketCapFetcher(args.api_key)

        # Get symbol
        cmc_symbol = fetcher.get_symbol(args.symbol)

        # Parse dates
        start_date = pd.to_datetime(args.start_date)
        end_date = pd.to_datetime(args.end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        print(f"\n{'='*80}")
        print(f"Fetching data from CoinMarketCap")
        print(f"Symbol: {args.symbol.upper()} → CMC: {cmc_symbol}")
        print(f"Date range: {args.start_date} to {args.end_date}")
        print(f"{'='*80}")

        # Fetch OHLCV data
        df = fetcher.fetch_ohlcv_data(cmc_symbol, start_date, end_date)

        # Get latest quote
        try:
            quote = fetcher.get_latest_quote(cmc_symbol)
        except:
            quote = {
                'name': cmc_symbol,
                'symbol': cmc_symbol,
                'current_price': df.iloc[-1]['close'],
                'price_change_pct_24h': 0,
                'total_volume': 0,
                'market_cap': 0,
            }

        # Display summary
        avg_price = df['close'].mean()
        if avg_price < 0.01:
            decimals = 6
        elif avg_price < 1:
            decimals = 4
        else:
            decimals = 2

        print("\n📊 SUMMARY (CoinMarketCap Data)")
        print("-" * 80)
        print(f"{'Coin':.<25} {quote['name']} ({quote['symbol']})")
        print(f"{'Current Price':.<25} ${quote['current_price']:,.{decimals}f}")
        print(f"{'Period Change':.<25} ${df.iloc[-1]['close'] - df.iloc[0]['open']:,.{decimals}f} ({((df.iloc[-1]['close'] - df.iloc[0]['open']) / df.iloc[0]['open'] * 100):.2f}%)")
        print(f"{'24h Change %':.<25} {quote['price_change_pct_24h']:.2f}%")
        print(f"{'24h Volume':.<25} ${quote['total_volume']:,.0f}")
        print(f"{'Market Cap':.<25} ${quote['market_cap']:,.0f}")
        print(f"{'Data Points':.<25} {len(df)}")

        # Calculate and display daily moves
        daily_df = fetcher.calculate_daily_moves(df)
        avg_moves = fetcher.calculate_average_moves(daily_df)

        print(f"\n📊 DAILY INTRADAY MOVES (CoinMarketCap)")
        print("-" * 80)
        display_daily_moves(daily_df)

        print(f"\n📈 AVERAGE DAILY MOVES (CoinMarketCap)")
        print("-" * 80)
        print(f"{'Avg Intraday Range':.<35} ${avg_moves['avg_intraday_range']:,.{decimals}f} ({avg_moves['avg_intraday_range_pct']:.2f}%)")
        print(f"{'Avg Open-Close Move':.<35} ${avg_moves['avg_open_close_move']:,.{decimals}f} ({avg_moves['avg_open_close_pct']:+.2f}%)")
        print(f"{'Max Intraday Range':.<35} ${avg_moves['max_intraday_range']:,.{decimals}f} ({avg_moves['max_intraday_range_pct']:.2f}%)")
        print(f"{'Min Intraday Range':.<35} ${avg_moves['min_intraday_range']:,.{decimals}f} ({avg_moves['min_intraday_range_pct']:.2f}%)")

        def format_vol(vol):
            if vol >= 1_000_000_000:
                return f"${vol/1_000_000_000:.2f}B"
            elif vol >= 1_000_000:
                return f"${vol/1_000_000:.2f}M"
            elif vol >= 1_000:
                return f"${vol/1_000:.2f}K"
            else:
                return f"${vol:,.2f}"

        print(f"{'Avg Daily Volume':.<35} {format_vol(avg_moves['avg_volume'])}")
        print(f"{'Max Daily Volume':.<35} {format_vol(avg_moves['max_volume'])}")
        print(f"{'Min Daily Volume':.<35} {format_vol(avg_moves['min_volume'])}")
        print(f"{'Total Volume':.<35} {format_vol(avg_moves['total_volume'])}")
        print(f"{'Number of Days':.<35} {len(daily_df)}")

        # Export if requested
        if args.csv:
            df.to_csv(args.csv, index=False)
            print(f"\n✅ Data exported to {args.csv}")

        if args.export:
            df.to_json(args.export, orient='records', date_format='iso', indent=2)
            print(f"✅ Data exported to {args.export}")

        print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
