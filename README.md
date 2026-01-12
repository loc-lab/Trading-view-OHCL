# Trading View OHLC - Intraday Token Data Fetcher

A powerful tool to fetch intraday OHLC (Open, High, Low, Close) data with volume for cryptocurrency tokens using the Binance API. Perfect for analyzing intraday moves, volume patterns, and price action.

## 🚀 Features

- **Real-time Intraday Data**: Fetch OHLC data with multiple time intervals (1m, 5m, 15m, 1h, etc.)
- **Volume Analysis**: Track trading volume and quote volume
- **Price Metrics**: Calculate price changes, percentage moves, and high-low ranges
- **24-Hour Statistics**: Get comprehensive 24h stats including highs, lows, and total volume
- **Multiple Export Formats**: Export to JSON (TradingView compatible) or CSV
- **Beautiful CLI Interface**: Formatted tables with color-coded output
- **No Authentication Required**: Uses free Binance public API

## 📋 Requirements

- Python 3.7 or higher
- Internet connection

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Trading-view-OHCL
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable (optional):
```bash
chmod +x intraday_fetcher.py
```

## 📖 Usage

### Basic Usage

Fetch 5-minute candles for Bitcoin:
```bash
python intraday_fetcher.py BTCUSDT
```

### Advanced Usage

**Fetch specific interval:**
```bash
python intraday_fetcher.py ETHUSDT -i 1h -l 100
```

**Export to JSON (TradingView format):**
```bash
python intraday_fetcher.py BTCUSDT -i 15m -l 200 -e btc_data.json
```

**Export to CSV:**
```bash
python intraday_fetcher.py SOLUSDT -i 5m --csv sol_data.csv
```

**List available trading pairs:**
```bash
python intraday_fetcher.py --list-symbols
```

**Display more/fewer rows:**
```bash
python intraday_fetcher.py BTCUSDT -r 50
```

## ⚙️ Supported Intervals

- `1m` - 1 minute
- `3m` - 3 minutes
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `2h` - 2 hours
- `4h` - 4 hours
- `6h` - 6 hours
- `8h` - 8 hours
- `12h` - 12 hours
- `1d` - 1 day

## 📊 Output Format

The tool displays:

1. **Summary Section**:
   - Current price
   - Intraday price change and percentage
   - 24-hour statistics (high, low, volume)
   - Time range of data

2. **OHLC Table**:
   - Timestamp
   - Open, High, Low, Close prices
   - Volume
   - Price change percentage

## 🔌 TradingView Integration

The tool can export data in TradingView's Datafeed API format. Use the `-e` flag to export JSON data that can be integrated with TradingView's charting library.

### JSON Format

```json
[
  {
    "time": 1704967200000,
    "open": 42500.50,
    "high": 42650.75,
    "low": 42450.25,
    "close": 42600.00,
    "volume": 1250.5
  },
  ...
]
```

## 💡 Examples

### Monitor Bitcoin's 5-minute moves
```bash
python intraday_fetcher.py BTCUSDT -i 5m -l 50
```

### Track Ethereum's hourly trends
```bash
python intraday_fetcher.py ETHUSDT -i 1h -l 24
```

### Analyze Solana with full data export
```bash
python intraday_fetcher.py SOLUSDT -i 15m -l 200 -e solana_data.json --csv solana_data.csv
```

### Quick check on multiple tokens
```bash
python intraday_fetcher.py BTCUSDT -r 10
python intraday_fetcher.py ETHUSDT -r 10
python intraday_fetcher.py BNBUSDT -r 10
```

## 🎯 Use Cases

- **Day Trading**: Monitor intraday price movements and volume
- **Technical Analysis**: Export data for further analysis in TradingView or other tools
- **Algorithmic Trading**: Integrate with trading bots for real-time market data
- **Market Research**: Study volume patterns and price action across different timeframes
- **Portfolio Tracking**: Monitor your token holdings in real-time

## 🔒 API Limits

The tool uses Binance's public API with the following limits:
- **Weight**: 1 per request
- **Rate Limit**: 1200 requests per minute
- **Max Candles**: 1000 per request

## 🛠️ Troubleshooting

**"Failed to fetch data" error:**
- Check if the symbol is valid (use `--list-symbols`)
- Ensure you have internet connection
- Verify the symbol format (e.g., BTCUSDT, not BTC-USDT)

**"No module named 'X'" error:**
- Run `pip install -r requirements.txt`

## 📝 License

MIT License - Feel free to use this tool for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Happy Trading! 📈**
