#!/usr/bin/env python3
"""
Example usage of the IntradayTokenFetcher class
"""

import sys
sys.path.append('..')

from intraday_fetcher import IntradayTokenFetcher
import json


def example_basic_fetch():
    """Example: Basic data fetch"""
    print("\n=== Example 1: Basic Fetch ===")
    fetcher = IntradayTokenFetcher()

    # Fetch 5-minute candles for Bitcoin
    df = fetcher.fetch_intraday_data('BTCUSDT', interval='5m', limit=20)

    print(f"Fetched {len(df)} candles")
    print(f"Latest price: ${df.iloc[-1]['close']:.2f}")
    print(f"Price change: {df.iloc[-1]['price_change_pct']:.2f}%")


def example_24h_stats():
    """Example: Get 24-hour statistics"""
    print("\n=== Example 2: 24-Hour Statistics ===")
    fetcher = IntradayTokenFetcher()

    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

    for symbol in symbols:
        stats = fetcher.get_24h_stats(symbol)
        current_price = fetcher.get_current_price(symbol)

        print(f"\n{symbol}:")
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  24h Change: {stats['price_change_pct']:.2f}%")
        print(f"  24h High: ${stats['high']:.2f}")
        print(f"  24h Low: ${stats['low']:.2f}")
        print(f"  24h Volume: {stats['volume']:,.2f}")


def example_multiple_intervals():
    """Example: Compare different time intervals"""
    print("\n=== Example 3: Multiple Time Intervals ===")
    fetcher = IntradayTokenFetcher()

    symbol = 'ETHUSDT'
    intervals = ['5m', '15m', '1h']

    for interval in intervals:
        df = fetcher.fetch_intraday_data(symbol, interval=interval, limit=10)
        first_price = df.iloc[0]['open']
        last_price = df.iloc[-1]['close']
        change_pct = ((last_price - first_price) / first_price * 100)

        print(f"\n{interval} interval:")
        print(f"  Change: {change_pct:.2f}%")
        print(f"  Avg Volume: {df['volume'].mean():,.2f}")


def example_export_data():
    """Example: Export data to different formats"""
    print("\n=== Example 4: Export Data ===")
    fetcher = IntradayTokenFetcher()

    # Fetch data
    df = fetcher.fetch_intraday_data('SOLUSDT', interval='15m', limit=50)

    # Export to TradingView format
    tv_data = fetcher.export_to_tradingview_format(df)
    with open('sol_tradingview.json', 'w') as f:
        json.dump(tv_data, f, indent=2)
    print("Exported to sol_tradingview.json (TradingView format)")

    # Export to CSV
    df.to_csv('sol_data.csv', index=False)
    print("Exported to sol_data.csv")


def example_analyze_volatility():
    """Example: Analyze volatility"""
    print("\n=== Example 5: Volatility Analysis ===")
    fetcher = IntradayTokenFetcher()

    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

    for symbol in symbols:
        df = fetcher.fetch_intraday_data(symbol, interval='1h', limit=24)

        avg_range = df['range_pct'].mean()
        max_range = df['range_pct'].max()
        volatility = df['price_change_pct'].std()

        print(f"\n{symbol} (24h, 1h candles):")
        print(f"  Avg Range: {avg_range:.2f}%")
        print(f"  Max Range: {max_range:.2f}%")
        print(f"  Volatility (std): {volatility:.2f}%")


if __name__ == '__main__':
    try:
        example_basic_fetch()
        example_24h_stats()
        example_multiple_intervals()
        example_export_data()
        example_analyze_volatility()

        print("\n" + "="*50)
        print("All examples completed successfully!")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
