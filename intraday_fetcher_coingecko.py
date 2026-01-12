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
        """Convert trading pair symbol to CoinGecko coin ID or use direct coin ID"""

        # Check if it's already a coin ID (lowercase with hyphens, no USDT suffix)
        # Examples: bitcoin, ethereum, orochi-network
        if symbol.islower() or '-' in symbol:
            # Likely already a CoinGecko coin ID
            return symbol.lower()

        symbol_upper = symbol.upper()

        # Direct lookup in coin map
        if symbol_upper in self.coin_map:
            return self.coin_map[symbol_upper]

        # Try without USDT suffix
        base_symbol = symbol_upper.replace('USDT', '').replace('USD', '')

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

        return base_symbol.lower()

    def fetch_volume_data(self, coin_id, days=1):
        """
        Fetch volume data from CoinGecko market_chart endpoint

        Args:
            coin_id: CoinGecko coin ID
            days: Number of days

        Returns:
            pandas DataFrame with timestamp and volume
        """
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days
        }

        response = requests.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch volume data: {response.status_code} - {response.text}")

        data = response.json()

        if not data or 'total_volumes' not in data:
            return pd.DataFrame(columns=['timestamp', 'volume'])

        # Extract volume data: [[timestamp, volume], ...]
        volumes = data['total_volumes']
        df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        return df

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

        print(f"Fetching OHLC from: {url}")
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

        # Fetch and merge volume data
        print(f"Fetching volume data...")
        volume_df = self.fetch_volume_data(coin_id, days)

        if not volume_df.empty:
            # Merge on timestamp with tolerance (volume data might have slightly different timestamps)
            df = pd.merge_asof(df.sort_values('timestamp'),
                              volume_df.sort_values('timestamp'),
                              on='timestamp',
                              direction='nearest',
                              tolerance=pd.Timedelta('1h'))
        else:
            df['volume'] = 0

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

        # Determine decimal places based on price magnitude
        current_price = market_data['current_price']
        if current_price < 0.01:
            decimals = 6
        elif current_price < 1:
            decimals = 4
        else:
            decimals = 2

        summary = {
            'Coin': f"{market_data['name']} ({market_data['symbol']})",
            'Current Price': f"${market_data['current_price']:,.{decimals}f}",
            'Period Change': f"${latest['close'] - oldest['open']:,.{decimals}f} ({((latest['close'] - oldest['open']) / oldest['open'] * 100):.2f}%)",
            '24h Change': f"${market_data['price_change_24h']:,.{decimals}f} ({market_data['price_change_pct_24h']:.2f}%)",
            '24h High': f"${market_data['high_24h']:,.{decimals}f}",
            '24h Low': f"${market_data['low_24h']:,.{decimals}f}",
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

            # Calculate daily volume (sum of all volumes for that day)
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
            'avg_volume': daily_df['volume'].mean(),
            'max_volume': daily_df['volume'].max(),
            'min_volume': daily_df['volume'].min(),
            'total_volume': daily_df['volume'].sum(),
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

    # Determine decimal places based on price magnitude
    avg_price = df['close'].mean()
    if avg_price < 0.01:
        decimals = 6
    elif avg_price < 1:
        decimals = 4
    else:
        decimals = 2

    for col in ['open', 'high', 'low', 'close']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.{decimals}f}")

    print("\n" + tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def display_daily_moves(daily_df):
    """Display daily intraday moves in a formatted table"""
    display_df = daily_df.copy()
    display_df['date'] = display_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    # Determine decimal places based on price magnitude
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

    # Format volume with K, M, B suffixes
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

    # Select columns to display
    display_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'intraday_range', 'intraday_range_pct', 'open_close_pct']
    display_df = display_df[display_cols]

    print("\n" + tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def main():
    parser = argparse.ArgumentParser(
        description='Fetch intraday OHLC data for crypto tokens using CoinGecko API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 1-day data for Bitcoin (using trading pair)
  python intraday_fetcher_coingecko.py BTCUSDT

  # Fetch 1-day data for Bitcoin (using CoinGecko ID)
  python intraday_fetcher_coingecko.py bitcoin

  # Fetch 7-day data for Ethereum with export
  python intraday_fetcher_coingecko.py ethereum -d 7 -e output.json

  # Fetch data for Orochi Network (use CoinGecko ID for specific tokens)
  python intraday_fetcher_coingecko.py orochi-network -d 30 --start-date 2026-01-01 --end-date 2026-01-12

  # Fetch 30-day data and filter for specific date range (Jan 1-7)
  python intraday_fetcher_coingecko.py BTCUSDT -d 30 --start-date 2026-01-01 --end-date 2026-01-07

  # Combine date and price filters
  python intraday_fetcher_coingecko.py BTCUSDT -d 90 --start-date 2025-12-01 --end-date 2025-12-31 --min-price 92000

Supported days: 1, 7, 14, 30, 90, 180, 365, or 'max'
Note:
  - Symbol can be either a trading pair (BTCUSDT) or CoinGecko coin ID (bitcoin, orochi-network)
  - Find CoinGecko IDs at: https://www.coingecko.com (look at the URL)
  - Use --start-date/--end-date for date filtering, --min-price/--max-price for price filtering
        """
    )

    parser.add_argument('symbol', nargs='?', help='Trading pair (BTCUSDT) or CoinGecko coin ID (bitcoin, orochi-network)')
    parser.add_argument('-d', '--days', default='1',
                       help='Number of days (1, 7, 14, 30, 90, 180, 365, max) - default: 1')
    parser.add_argument('-r', '--rows', type=int, default=20,
                       help='Number of rows to display (default: 20)')
    parser.add_argument('-e', '--export', help='Export data to JSON file (TradingView format)')
    parser.add_argument('--csv', help='Export data to CSV file')
    parser.add_argument('--coin-id', help='Use CoinGecko coin ID directly (e.g., bitcoin, ethereum)')
    parser.add_argument('--start-date', help='Start date for filtering (format: YYYY-MM-DD, e.g., 2026-01-01)')
    parser.add_argument('--end-date', help='End date for filtering (format: YYYY-MM-DD, e.g., 2026-01-07)')
    parser.add_argument('--min-price', type=float, help='Minimum price filter (e.g., 90000)')
    parser.add_argument('--max-price', type=float, help='Maximum price filter (e.g., 100000)')

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

        # Filter by price range if specified
        if args.min_price or args.max_price:
            if args.min_price:
                # Filter to keep candles where the price touched or went above min_price
                df = df[df['high'] >= args.min_price]
                print(f"Filtering min price: ${args.min_price:,.2f}")

            if args.max_price:
                # Filter to keep candles where the price touched or went below max_price
                df = df[df['low'] <= args.max_price]
                print(f"Filtering max price: ${args.max_price:,.2f}")

            if len(df) == 0:
                print(f"\n❌ No data found in the specified price range")
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

        # Always show daily analysis if date range or price range is specified
        if args.start_date or args.end_date or args.min_price or args.max_price:
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

            # Determine decimal places based on price magnitude
            avg_price = df['close'].mean()
            if avg_price < 0.01:
                decimals = 6
            elif avg_price < 1:
                decimals = 4
            else:
                decimals = 2

            print(f"{'Avg Intraday Range':.<35} ${avg_moves['avg_intraday_range']:,.{decimals}f} ({avg_moves['avg_intraday_range_pct']:.2f}%)")
            print(f"{'Avg Open-Close Move':.<35} ${avg_moves['avg_open_close_move']:,.{decimals}f} ({avg_moves['avg_open_close_pct']:+.2f}%)")
            print(f"{'Max Intraday Range':.<35} ${avg_moves['max_intraday_range']:,.{decimals}f} ({avg_moves['max_intraday_range_pct']:.2f}%)")
            print(f"{'Min Intraday Range':.<35} ${avg_moves['min_intraday_range']:,.{decimals}f} ({avg_moves['min_intraday_range_pct']:.2f}%)")

            # Format volume with K, M, B suffixes
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
