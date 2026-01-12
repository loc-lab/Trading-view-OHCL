# Quick Start Guide 🚀

Get up and running in 3 minutes!

---

## For Beginners (Windows)

### Step 1: Install Python
1. Go to https://www.python.org/downloads/
2. Download and run the installer
3. ✅ **CHECK THE BOX** "Add Python to PATH"
4. Click "Install Now"

### Step 2: Download This Tool
1. Download ZIP from GitHub
2. Extract to Desktop
3. Open folder "Trading-view-OHCL"

### Step 3: Run Setup
1. Double-click `setup.bat`
2. Wait for installation to complete

### Step 4: Launch Web Interface
1. Double-click `run_web.bat`
2. Open browser to: http://localhost:5000
3. Done! 🎉

---

## For Beginners (Mac)

### Step 1: Install Python
1. Open Terminal (Cmd+Space, type "Terminal")
2. Install Homebrew:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Python:
   ```bash
   brew install python
   ```

### Step 2: Download This Tool
```bash
cd Desktop
git clone https://github.com/loc-lab/Trading-view-OHCL.git
cd Trading-view-OHCL
```

### Step 3: Run Setup
```bash
chmod +x setup.sh
./setup.sh
```

### Step 4: Launch Web Interface
```bash
./run_web.sh
```
Then open: http://localhost:5000

---

## One-Line Install (Advanced Users)

### Windows:
```bash
git clone https://github.com/loc-lab/Trading-view-OHCL.git && cd Trading-view-OHCL && pip install -r requirements.txt && python web_app.py
```

### Mac/Linux:
```bash
git clone https://github.com/loc-lab/Trading-view-OHCL.git && cd Trading-view-OHCL && pip3 install -r requirements.txt && python3 web_app.py
```

---

## Using the Web Interface

1. **Enter Symbol**: Type token pair (e.g., BTCUSDT)
2. **Select Interval**: Choose time period (5m, 1h, etc.)
3. **Set Candles**: How many data points (50-1000)
4. **Click Fetch**: Get real-time data!

### Popular Symbols:
- `BTCUSDT` - Bitcoin
- `ETHUSDT` - Ethereum
- `BNBUSDT` - Binance Coin
- `SOLUSDT` - Solana
- `ADAUSDT` - Cardano
- `DOGEUSDT` - Dogecoin

---

## Command Line Usage (Optional)

### Basic:
```bash
python intraday_fetcher.py BTCUSDT
```

### With Options:
```bash
python intraday_fetcher.py ETHUSDT -i 1h -l 100
```

### Export to File:
```bash
python intraday_fetcher.py BTCUSDT -e bitcoin.json
```

---

## Troubleshooting

### "python is not recognized" (Windows)
**Fix**: Reinstall Python with "Add to PATH" checked

### "Permission denied" (Mac/Linux)
**Fix**: Use `chmod +x` on the script:
```bash
chmod +x run_web.sh
```

### "Port 5000 already in use"
**Fix**: Change port in web_app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Can't connect to Binance
**Fix**:
- Check internet connection
- Try VPN if Binance is blocked in your country
- Use different token symbol

---

## What Can You Do?

✅ Monitor real-time crypto prices
✅ Analyze intraday price movements
✅ Track volume and trading activity
✅ Export data for Excel/analysis
✅ Integrate with TradingView charts
✅ Build trading strategies

---

## Need More Help?

- 📖 Full Guide: See `INSTALLATION_GUIDE.md`
- 💻 Technical Docs: See `IMPLEMENTATION.md`
- 🐛 Report Issues: GitHub Issues
- ❓ Questions: Check README.md

---

**Happy Trading! 📈**

*Remember: This tool is for educational purposes. Always do your own research before making investment decisions.*
