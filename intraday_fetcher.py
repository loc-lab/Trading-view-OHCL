#!/usr/bin/env python3
"""
Intraday Token Data Fetcher
Fetches OHLC (Open, High, Low, Close) data with volume for crypto tokens
using public APIs (Binance) and formats it for analysis.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import argparse
from tabulate import tabulate
import pytz


class IntradayTokenFetcher:
    """Fetches intraday token data from Binance API"""

    def __init__(self):
        self.binance_base_url = "https://api.binance.com/api/v3"

    def get_available_symbols(self, base_currency="USDT", limit=20):
        """Get available trading pairs for a base currency"""
        url = f"{self.binance_base_url}/exchangeInfo"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch symbols: {response.text}")

        data = response.json()
        symbols = [s['symbol'] for s in data['symbols']
                  if s['symbol'].endswith(base_currency) and s['status'] == 'TRADING']

        return symbols[:limit]

    def fetch_intraday_data(self, symbol, interval="5m", limit=100):
        """
        Fetch intraday OHLC data for a token

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
            interval: Candle interval - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d
            limit: Number of candles to fetch (max 1000)

        Returns:
            pandas DataFrame with OHLC data
        """
        url = f"{self.binance_base_url}/klines"
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': limit
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.text}")

        data = response.json()

        # Parse Binance klines data
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        # Convert price and volume columns to float
        for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
            df[col] = df[col].astype(float)

        # Calculate additional metrics
        df['price_change'] = df['close'] - df['open']
        df['price_change_pct'] = ((df['close'] - df['open']) / df['open'] * 100)
        df['high_low_range'] = df['high'] - df['low']
        df['range_pct'] = ((df['high'] - df['low']) / df['open'] * 100)

        return df

    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        url = f"{self.binance_base_url}/ticker/price"
        params = {'symbol': symbol.upper()}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch current price: {response.text}")

        data = response.json()
        return float(data['price'])

    def get_24h_stats(self, symbol):
        """Get 24-hour statistics for a symbol"""
        url = f"{self.binance_base_url}/ticker/24hr"
        params = {'symbol': symbol.upper()}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch 24h stats: {response.text}")

        data = response.json()
        return {
            'price_change': float(data['priceChange']),
            'price_change_pct': float(data['priceChangePercent']),
            'high': float(data['highPrice']),
            'low': float(data['lowPrice']),
            'volume': float(data['volume']),
            'quote_volume': float(data['quoteVolume']),
            'trades': int(data['count'])
        }

    def format_summary(self, symbol, df, stats_24h):
        """Format a summary of the intraday data"""
        latest = df.iloc[-1]
        oldest = df.iloc[0]

        summary = {
            'Symbol': symbol,
            'Current Price': f"${latest['close']:.8f}",
            'Intraday Change': f"${latest['close'] - oldest['open']:.8f} ({((latest['close'] - oldest['open']) / oldest['open'] * 100):.2f}%)",
            '24h Change': f"${stats_24h['price_change']:.8f} ({stats_24h['price_change_pct']:.2f}%)",
            '24h High': f"${stats_24h['high']:.8f}",
            '24h Low': f"${stats_24h['low']:.8f}",
            '24h Volume': f"{stats_24h['volume']:,.2f}",
            '24h Quote Volume': f"${stats_24h['quote_volume']:,.2f}",
            'Candles': len(df),
            'Time Range': f"{df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}"
        }

        return summary

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
                'volume': row['volume']
            })

        return tv_data


def display_table(df, num_rows=20):
    """Display OHLC data in a formatted table"""
    display_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'price_change_pct']].tail(num_rows).copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.2f}")
    display_df['price_change_pct'] = display_df['price_change_pct'].apply(lambda x: f"{x:.2f}%")

    for col in ['open', 'high', 'low', 'close']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.8f}")

    print("\n" + tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def main():
    parser = argparse.ArgumentParser(
        description='Fetch intraday OHLC data for crypto tokens',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 5-minute candles for Bitcoin
  python intraday_fetcher.py BTCUSDT -i 5m -l 50

  # Fetch 1-hour candles for Ethereum with export
  python intraday_fetcher.py ETHUSDT -i 1h -l 100 -e output.json

  # List available trading pairs
  python intraday_fetcher.py --list-symbols

Supported intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d
        """
    )

    parser.add_argument('symbol', nargs='?', help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)')
    parser.add_argument('-i', '--interval', default='5m',
                       help='Candle interval (default: 5m)')
    parser.add_argument('-l', '--limit', type=int, default=50,
                       help='Number of candles to fetch (default: 50, max: 1000)')
    parser.add_argument('-r', '--rows', type=int, default=20,
                       help='Number of rows to display (default: 20)')
    parser.add_argument('-e', '--export', help='Export data to JSON file (TradingView format)')
    parser.add_argument('--list-symbols', action='store_true',
                       help='List available trading pairs')
    parser.add_argument('--csv', help='Export data to CSV file')

    args = parser.parse_args()

    fetcher = IntradayTokenFetcher()

    try:
        if args.list_symbols:
            print("\nFetching available trading pairs...")
            symbols = fetcher.get_available_symbols(limit=50)
            print(f"\nTop 50 USDT trading pairs:\n")
            for i, symbol in enumerate(symbols, 1):
                print(f"{i}. {symbol}")
            return

        if not args.symbol:
            parser.print_help()
            return

        symbol = args.symbol.upper()
        print(f"\n{'='*80}")
        print(f"Fetching intraday data for {symbol}")
        print(f"Interval: {args.interval} | Limit: {args.limit} candles")
        print(f"{'='*80}")

        # Fetch data
        df = fetcher.fetch_intraday_data(symbol, args.interval, args.limit)
        stats_24h = fetcher.get_24h_stats(symbol)

        # Display summary
        summary = fetcher.format_summary(symbol, df, stats_24h)
        print("\n📊 SUMMARY")
        print("-" * 80)
        for key, value in summary.items():
            print(f"{key:.<25} {value}")

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
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
