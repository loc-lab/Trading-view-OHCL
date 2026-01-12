#!/usr/bin/env python3
"""
Intraday Token Data Fetcher - CoinGecko Edition
Fetches OHLC (Open, High, Low, Close) data with volume for crypto tokens
using CoinGecko's free public API.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import argparse
from tabulate import tabulate
import time


class CoinGeckoFetcher:
    """Fetches intraday token data from CoinGecko API"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.coin_map = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'SOLUSDT': 'solana',
            'XRPUSDT': 'ripple',
            'DOTUSDT': 'polkadot',
            'DOGEUSDT': 'dogecoin',
            'MATICUSDT': 'matic-network',
            'LINKUSDT': 'chainlink',
            'AVAXUSDT': 'avalanche-2',
            'UNIUSDT': 'uniswap',
            'ATOMUSDT': 'cosmos',
            'LTCUSDT': 'litecoin',
            'ALGOUSDT': 'algorand',
        }

    def get_coin_id(self, symbol):
        """Convert trading pair symbol to CoinGecko coin ID"""
        symbol = symbol.upper()

        # Direct lookup
        if symbol in self.coin_map:
            return self.coin_map[symbol]

        # Try without USDT suffix
        base_symbol = symbol.replace('USDT', '').replace('USD', '').lower()

        # Search CoinGecko for the coin
        try:
            url = f"{self.base_url}/search"
            params = {'query': base_symbol}
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('coins'):
                    return data['coins'][0]['id']
        except:
            pass

        return base_symbol

    def fetch_ohlc_data(self, coin_id, days=1):
        """
        Fetch OHLC data from CoinGecko

        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
            days: Number of days (1, 7, 14, 30, 90, 180, 365, max)

        Returns:
            pandas DataFrame with OHLC data
        """
        url = f"{self.base_url}/coins/{coin_id}/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days
        }

        print(f"Fetching from: {url}")
        print(f"Parameters: {params}")

        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch OHLC data: {response.status_code} - {response.text}")

        data = response.json()

        if not data:
            raise Exception("No data returned from CoinGecko")

        # CoinGecko returns: [timestamp, open, high, low, close]
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Calculate additional metrics
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = ((df['close'] - df['open']) / df['open'] * 100)
        df['high_low_range'] = df['high'] - df['low']
        df['range_pct'] = ((df['high'] - df['low']) / df['open'] * 100)

        return df

    def get_current_price(self, coin_id):
        """Get current price for a coin"""
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true'
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch current price: {response.text}")

        data = response.json()

        if coin_id not in data:
            raise Exception(f"Coin {coin_id} not found")

        return data[coin_id]

    def get_market_data(self, coin_id):
        """Get detailed market data for a coin"""
        url = f"{self.base_url}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch market data: {response.text}")

        data = response.json()
        market_data = data.get('market_data', {})

        return {
            'name': data.get('name', ''),
            'symbol': data.get('symbol', '').upper(),
            'current_price': market_data.get('current_price', {}).get('usd', 0),
            'price_change_24h': market_data.get('price_change_24h', 0),
            'price_change_pct_24h': market_data.get('price_change_percentage_24h', 0),
            'high_24h': market_data.get('high_24h', {}).get('usd', 0),
            'low_24h': market_data.get('low_24h', {}).get('usd', 0),
            'total_volume': market_data.get('total_volume', {}).get('usd', 0),
            'market_cap': market_data.get('market_cap', {}).get('usd', 0),
        }

    def format_summary(self, coin_id, df, market_data):
        """Format a summary of the intraday data"""
        latest = df.iloc[-1]
        oldest = df.iloc[0]

        summary = {
            'Coin': f"{market_data['name']} ({market_data['symbol']})",
            'Current Price': f"${market_data['current_price']:,.2f}",
            'Period Change': f"${latest['close'] - oldest['open']:,.2f} ({((latest['close'] - oldest['open']) / oldest['open'] * 100):.2f}%)",
            '24h Change': f"${market_data['price_change_24h']:,.2f} ({market_data['price_change_pct_24h']:.2f}%)",
            '24h High': f"${market_data['high_24h']:,.2f}",
            '24h Low': f"${market_data['low_24h']:,.2f}",
            '24h Volume': f"${market_data['total_volume']:,.0f}",
            'Market Cap': f"${market_data['market_cap']:,.0f}",
            'Candles': len(df),
            'Time Range': f"{df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}"
        }

        return summary

    def calculate_daily_moves(self, df):
        """
        Calculate intraday moves for each day

        Returns:
            DataFrame with daily statistics
        """
        # Add date column
        df_copy = df.copy()
        df_copy['date'] = df_copy['timestamp'].dt.date

        # Group by date and calculate daily metrics
        daily_stats = []

        for date, group in df_copy.groupby('date'):
            day_high = group['high'].max()
            day_low = group['low'].min()
            day_open = group.iloc[0]['open']
            day_close = group.iloc[-1]['close']

            # Calculate intraday move (high-low range)
            intraday_range = day_high - day_low
            intraday_range_pct = (intraday_range / day_open) * 100

            # Calculate open-to-close move
            open_close_move = day_close - day_open
            open_close_pct = (open_close_move / day_open) * 100

            daily_stats.append({
                'date': date,
                'open': day_open,
                'high': day_high,
                'low': day_low,
                'close': day_close,
                'intraday_range': intraday_range,
                'intraday_range_pct': intraday_range_pct,
                'open_close_move': open_close_move,
                'open_close_pct': open_close_pct,
                'num_candles': len(group)
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
        }

    def export_to_tradingview_format(self, df):
        """Export data in TradingView datafeed format"""
        tv_data = []

        for _, row in df.iterrows():
            tv_data.append({
                'time': int(row['timestamp'].timestamp() * 1000),
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
            })

        return tv_data


def display_table(df, num_rows=20):
    """Display OHLC data in a formatted table"""
    display_df = df[['timestamp', 'open', 'high', 'low', 'close', 'price_change_pct']].tail(num_rows).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['price_change_pct'] = display_df['price_change_pct'].apply(lambda x: f"{x:.2f}%")

    for col in ['open', 'high', 'low', 'close']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")

    print("\n" + tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def display_daily_moves(daily_df):
    """Display daily intraday moves in a formatted table"""
    display_df = daily_df.copy()
    display_df['date'] = display_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    for col in ['open', 'high', 'low', 'close', 'intraday_range', 'open_close_move']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")

    display_df['intraday_range_pct'] = display_df['intraday_range_pct'].apply(lambda x: f"{x:.2f}%")
    display_df['open_close_pct'] = display_df['open_close_pct'].apply(lambda x: f"{x:+.2f}%")

    # Select columns to display
    display_cols = ['date', 'open', 'high', 'low', 'close', 'intraday_range', 'intraday_range_pct', 'open_close_pct']
    display_df = display_df[display_cols]

    print("\n" + tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def main():
    parser = argparse.ArgumentParser(
        description='Fetch intraday OHLC data for crypto tokens using CoinGecko API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 1-day data for Bitcoin
  python intraday_fetcher_coingecko.py BTCUSDT

  # Fetch 7-day data for Ethereum with export
  python intraday_fetcher_coingecko.py ETHUSDT -d 7 -e output.json

  # Fetch 30-day data and filter for specific date range (Jan 1-7)
  python intraday_fetcher_coingecko.py BTCUSDT -d 30 --start-date 2026-01-01 --end-date 2026-01-07

  # Fetch max data and filter for a week
  python intraday_fetcher_coingecko.py BTCUSDT -d 90 --start-date 2025-12-15 --end-date 2025-12-21

Supported days: 1, 7, 14, 30, 90, 180, 365, or 'max'
Note: Use --start-date and --end-date to filter to specific date ranges
        """
    )

    parser.add_argument('symbol', nargs='?', help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)')
    parser.add_argument('-d', '--days', default='1',
                       help='Number of days (1, 7, 14, 30, 90, 180, 365, max) - default: 1')
    parser.add_argument('-r', '--rows', type=int, default=20,
                       help='Number of rows to display (default: 20)')
    parser.add_argument('-e', '--export', help='Export data to JSON file (TradingView format)')
    parser.add_argument('--csv', help='Export data to CSV file')
    parser.add_argument('--coin-id', help='Use CoinGecko coin ID directly (e.g., bitcoin, ethereum)')
    parser.add_argument('--start-date', help='Start date for filtering (format: YYYY-MM-DD, e.g., 2026-01-01)')
    parser.add_argument('--end-date', help='End date for filtering (format: YYYY-MM-DD, e.g., 2026-01-07)')

    args = parser.parse_args()

    fetcher = CoinGeckoFetcher()

    try:
        if not args.symbol and not args.coin_id:
            parser.print_help()
            return

        # Determine coin ID
        if args.coin_id:
            coin_id = args.coin_id
            symbol = coin_id.upper()
        else:
            symbol = args.symbol.upper()
            coin_id = fetcher.get_coin_id(symbol)

        print(f"\n{'='*80}")
        print(f"Fetching OHLC data for {symbol} (CoinGecko ID: {coin_id})")
        print(f"Period: {args.days} day(s)")
        print(f"{'='*80}")

        # Fetch data
        df = fetcher.fetch_ohlc_data(coin_id, args.days)
        market_data = fetcher.get_market_data(coin_id)

        # Filter by date range if specified
        original_df = df.copy()
        if args.start_date or args.end_date:
            from datetime import datetime as dt

            if args.start_date:
                start_dt = pd.to_datetime(args.start_date)
                df = df[df['timestamp'] >= start_dt]
                print(f"Filtering from: {args.start_date}")

            if args.end_date:
                end_dt = pd.to_datetime(args.end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df = df[df['timestamp'] <= end_dt]
                print(f"Filtering to: {args.end_date}")

            if len(df) == 0:
                print(f"\n❌ No data found in the specified date range")
                return 1

        # Display summary
        summary = fetcher.format_summary(coin_id, df, market_data)
        print("\n📊 SUMMARY")
        print("-" * 80)
        for key, value in summary.items():
            print(f"{key:.<25} {value}")

        # Calculate daily moves if more than 1 day or date range is specified
        try:
            days_int = int(args.days)
            show_daily_analysis = days_int > 1
        except ValueError:
            show_daily_analysis = True  # For 'max' or other string values

        # Always show daily analysis if date range is specified
        if args.start_date or args.end_date:
            show_daily_analysis = True

        if show_daily_analysis:
            daily_df = fetcher.calculate_daily_moves(df)
            avg_moves = fetcher.calculate_average_moves(daily_df)

            # Display daily moves
            print(f"\n📊 DAILY INTRADAY MOVES")
            print("-" * 80)
            display_daily_moves(daily_df)

            # Display average moves
            print(f"\n📈 AVERAGE DAILY MOVES")
            print("-" * 80)
            print(f"{'Avg Intraday Range':.<35} ${avg_moves['avg_intraday_range']:,.2f} ({avg_moves['avg_intraday_range_pct']:.2f}%)")
            print(f"{'Avg Open-Close Move':.<35} ${avg_moves['avg_open_close_move']:,.2f} ({avg_moves['avg_open_close_pct']:+.2f}%)")
            print(f"{'Max Intraday Range':.<35} ${avg_moves['max_intraday_range']:,.2f} ({avg_moves['max_intraday_range_pct']:.2f}%)")
            print(f"{'Min Intraday Range':.<35} ${avg_moves['min_intraday_range']:,.2f} ({avg_moves['min_intraday_range_pct']:.2f}%)")
            print(f"{'Number of Days':.<35} {len(daily_df)}")

        # Display table
        print(f"\n📈 OHLC DATA (Last {min(args.rows, len(df))} candles)")
        print("-" * 80)
        display_table(df, args.rows)

        # Export if requested
        if args.export:
            tv_data = fetcher.export_to_tradingview_format(df)
            with open(args.export, 'w') as f:
                json.dump(tv_data, f, indent=2)
            print(f"\n✅ Data exported to {args.export} (TradingView format)")

        if args.csv:
            df.to_csv(args.csv, index=False)
            print(f"✅ Data exported to {args.csv} (CSV format)")

        print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
