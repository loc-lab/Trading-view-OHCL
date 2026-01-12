# Implementation Details

## Overview

This tool fetches intraday OHLC (Open, High, Low, Close) data for cryptocurrency tokens using the Binance public API. It's designed to be TradingView-compatible and provides comprehensive market data analysis.

## Architecture

### Core Components

1. **IntradayTokenFetcher Class** (`intraday_fetcher.py`)
   - Main class handling all data fetching operations
   - Uses Binance API v3 endpoints
   - No authentication required (public endpoints)

2. **Data Fetching Methods**:
   - `fetch_intraday_data()`: Fetches OHLC candle data
   - `get_current_price()`: Gets real-time price
   - `get_24h_stats()`: Retrieves 24-hour statistics
   - `get_available_symbols()`: Lists trading pairs

3. **Data Processing**:
   - Converts timestamps to datetime objects
   - Calculates price changes and percentages
   - Computes high-low ranges
   - Formats volume data

4. **Export Functions**:
   - `export_to_tradingview_format()`: TradingView JSON format
   - CSV export via pandas
   - Formatted table output

### API Endpoints Used

1. **Klines (Candlestick Data)**
   - Endpoint: `/api/v3/klines`
   - Returns: OHLC data with volume
   - Max limit: 1000 candles per request

2. **Ticker Price**
   - Endpoint: `/api/v3/ticker/price`
   - Returns: Current price for symbol

3. **24h Ticker**
   - Endpoint: `/api/v3/ticker/24hr`
   - Returns: 24-hour statistics

4. **Exchange Info**
   - Endpoint: `/api/v3/exchangeInfo`
   - Returns: Available trading pairs

## Data Structure

### Binance Klines Response Format
```
[
  timestamp,        // Open time (ms)
  open,            // Open price
  high,            // High price
  low,             // Low price
  close,           // Close price
  volume,          // Base asset volume
  close_time,      // Close time (ms)
  quote_volume,    // Quote asset volume
  trades,          // Number of trades
  taker_buy_base,  // Taker buy base volume
  taker_buy_quote, // Taker buy quote volume
  ignore           // Unused field
]
```

### Internal DataFrame Columns
- `timestamp`: DateTime of candle open
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `quote_volume`: Quote asset volume
- `price_change`: Absolute price change (close - open)
- `price_change_pct`: Percentage price change
- `high_low_range`: Price range (high - low)
- `range_pct`: Range as percentage of open

### TradingView Export Format
```json
{
  "time": 1704967200000,     // Unix timestamp (ms)
  "open": 42500.50,
  "high": 42650.75,
  "low": 42450.25,
  "close": 42600.00,
  "volume": 1250.5
}
```

## Supported Intervals

The tool supports all Binance intervals:
- Minutes: 1m, 3m, 5m, 15m, 30m
- Hours: 1h, 2h, 4h, 6h, 8h, 12h
- Days: 1d, 3d
- Weeks: 1w
- Months: 1M

## CLI Interface

### Command Structure
```bash
python intraday_fetcher.py [SYMBOL] [OPTIONS]
```

### Arguments
- `symbol`: Trading pair (e.g., BTCUSDT)
- `-i, --interval`: Candle interval (default: 5m)
- `-l, --limit`: Number of candles (default: 50, max: 1000)
- `-r, --rows`: Display rows (default: 20)
- `-e, --export`: Export to JSON (TradingView format)
- `--csv`: Export to CSV
- `--list-symbols`: List available pairs

## Features

### 1. Real-time Data Fetching
- Fetches latest candle data from Binance
- Supports multiple time intervals
- Up to 1000 candles per request

### 2. Price Analysis
- Intraday price changes
- 24-hour statistics
- High-low ranges
- Percentage moves

### 3. Volume Analysis
- Base asset volume
- Quote asset volume
- Average volume calculations

### 4. Data Export
- JSON (TradingView Datafeed format)
- CSV (full data with all columns)
- Formatted table output

### 5. Symbol Discovery
- List available trading pairs
- Filter by quote currency
- Show active trading pairs only

## Error Handling

The tool includes error handling for:
- Invalid symbols
- Network failures
- API rate limits
- Invalid parameters
- Missing dependencies

## Rate Limits

Binance API limits:
- 1200 requests per minute
- Weight: 1 per klines request
- Weight: 1 per ticker request
- Weight: 10 per exchangeInfo request

## Dependencies

- **requests**: HTTP requests to Binance API
- **pandas**: Data manipulation and analysis
- **python-dateutil**: Date/time parsing
- **tabulate**: Pretty table formatting
- **pytz**: Timezone handling

## Future Enhancements

Possible improvements:
1. Support for multiple exchanges (Coinbase, Kraken, etc.)
2. Real-time WebSocket streaming
3. Technical indicators (RSI, MACD, EMA)
4. Alert system for price movements
5. Historical data caching
6. Database storage
7. Web dashboard
8. Trading signals
9. Portfolio tracking
10. TradingView Datafeed API server implementation

## TradingView Integration

To integrate with TradingView's Charting Library:

1. **Export Data**: Use `-e` flag to export JSON
2. **Create Datafeed**: Implement UDF (Universal Data Feed) protocol
3. **Serve Data**: Host data on web server
4. **Connect Library**: Point TradingView library to your datafeed

### Sample Datafeed Implementation
```javascript
// Example datafeed configuration
const datafeed = {
  onReady: (callback) => {
    // Return exchange configuration
  },
  resolveSymbol: (symbolName, onResolve, onError) => {
    // Return symbol info
  },
  getBars: (symbolInfo, resolution, from, to, onResult, onError) => {
    // Return OHLC data from your fetcher
    fetch(`/api/data?symbol=${symbolInfo.name}&interval=${resolution}`)
      .then(res => res.json())
      .then(data => onResult(data, { noData: false }));
  }
};
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check internet connection
   - Verify Binance API is accessible
   - Check for proxy/firewall issues

2. **Symbol Not Found**
   - Use `--list-symbols` to see available pairs
   - Ensure correct symbol format (BTCUSDT not BTC-USDT)
   - Check if symbol is actively trading

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.7+)

4. **Rate Limit Errors**
   - Reduce request frequency
   - Implement request throttling
   - Cache data locally

## License

MIT License - Free for personal and commercial use.
