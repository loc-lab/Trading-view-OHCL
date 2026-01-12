# Installation Guide - Step by Step

This guide will help you run the Intraday Token Fetcher on your computer, both via command line and web browser.

---

## 📋 Prerequisites

Before starting, make sure you have:
- A computer with internet connection
- Windows, Mac, or Linux operating system

---

## 🐍 Step 1: Install Python

### Windows:
1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.12" (or latest version)
3. Run the installer
4. ⚠️ **IMPORTANT**: Check the box "Add Python to PATH" during installation
5. Click "Install Now"
6. Verify installation: Open Command Prompt and type:
   ```bash
   python --version
   ```
   You should see something like `Python 3.12.0`

### Mac:
1. Open Terminal (press Cmd+Space, type "Terminal")
2. Install Homebrew (if not installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Python:
   ```bash
   brew install python
   ```
4. Verify:
   ```bash
   python3 --version
   ```

### Linux:
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

---

## 📥 Step 2: Download the Tool

### Option A: Using Git (Recommended)
1. Install Git from https://git-scm.com/downloads
2. Open Terminal/Command Prompt
3. Navigate to where you want to save the project:
   ```bash
   cd Desktop
   ```
4. Clone the repository:
   ```bash
   git clone https://github.com/loc-lab/Trading-view-OHCL.git
   cd Trading-view-OHCL
   ```

### Option B: Download ZIP
1. Go to https://github.com/loc-lab/Trading-view-OHCL
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to your Desktop
5. Open Terminal/Command Prompt and navigate to the folder:
   ```bash
   cd Desktop/Trading-view-OHCL
   ```

---

## 📦 Step 3: Install Dependencies

In the Terminal/Command Prompt (make sure you're in the Trading-view-OHCL folder):

### Windows:
```bash
pip install -r requirements.txt
```

### Mac/Linux:
```bash
pip3 install -r requirements.txt
```

This will install all required packages. It may take 1-2 minutes.

---

## ✅ Step 4A: Run via Command Line

### Basic Usage:

**Windows:**
```bash
python intraday_fetcher.py BTCUSDT
```

**Mac/Linux:**
```bash
python3 intraday_fetcher.py BTCUSDT
```

This will show Bitcoin's 5-minute candles!

### More Examples:

**Ethereum with 1-hour intervals:**
```bash
python intraday_fetcher.py ETHUSDT -i 1h -l 50
```

**Solana with export to file:**
```bash
python intraday_fetcher.py SOLUSDT -i 15m -e solana_data.json
```

**List all available tokens:**
```bash
python intraday_fetcher.py --list-symbols
```

**See all options:**
```bash
python intraday_fetcher.py --help
```

---

## 🌐 Step 4B: Run in Web Browser

### Install Web Version Dependencies:

**Windows:**
```bash
pip install flask flask-cors
```

**Mac/Linux:**
```bash
pip3 install flask flask-cors
```

### Start the Web Server:

**Windows:**
```bash
python web_app.py
```

**Mac/Linux:**
```bash
python3 web_app.py
```

You'll see output like:
```
* Running on http://127.0.0.1:5000
```

### Open in Browser:

1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Go to: **http://localhost:5000**
3. You should see the Intraday Token Fetcher interface!

### Using the Web Interface:

1. Enter a token symbol (e.g., BTCUSDT, ETHUSDT)
2. Select time interval (1m, 5m, 15m, 1h, etc.)
3. Choose how many candles to fetch
4. Click "Fetch Data"
5. View the results in a beautiful table
6. Download as JSON or CSV if needed

---

## 🛠️ Troubleshooting

### Problem: "python is not recognized" (Windows)
**Solution:** Python wasn't added to PATH. Either:
- Reinstall Python and check "Add Python to PATH"
- Or use `py` instead of `python`:
  ```bash
  py intraday_fetcher.py BTCUSDT
  ```

### Problem: "pip is not recognized"
**Solution:** Try:
```bash
python -m pip install -r requirements.txt
```

### Problem: "Permission denied"
**Solution (Mac/Linux):** Add `sudo`:
```bash
sudo pip3 install -r requirements.txt
```

### Problem: Web page won't load
**Solution:**
- Check if the server is running (you should see "Running on...")
- Make sure you're using `http://localhost:5000` (not https)
- Try `http://127.0.0.1:5000` instead
- Check if port 5000 is already in use

### Problem: "Failed to fetch data"
**Solutions:**
- Check your internet connection
- Verify the token symbol is correct (use --list-symbols)
- Try a different token (BTCUSDT usually works)
- Binance might be blocked in your country (use VPN)

### Problem: Import errors
**Solution:** Make sure all dependencies are installed:
```bash
pip install requests pandas python-dateutil tabulate pytz flask flask-cors
```

---

## 🚀 Quick Start Commands

### Just want to see Bitcoin data? Copy-paste this:

**Windows:**
```bash
cd Desktop
git clone https://github.com/loc-lab/Trading-view-OHCL.git
cd Trading-view-OHCL
pip install -r requirements.txt
python intraday_fetcher.py BTCUSDT
```

**Mac/Linux:**
```bash
cd Desktop
git clone https://github.com/loc-lab/Trading-view-OHCL.git
cd Trading-view-OHCL
pip3 install -r requirements.txt
python3 intraday_fetcher.py BTCUSDT
```

### Want the web version? Copy-paste this:

**Windows:**
```bash
cd Desktop
git clone https://github.com/loc-lab/Trading-view-OHCL.git
cd Trading-view-OHCL
pip install -r requirements.txt
pip install flask flask-cors
python web_app.py
```
Then open: http://localhost:5000

**Mac/Linux:**
```bash
cd Desktop
git clone https://github.com/loc-lab/Trading-view-OHCL.git
cd Trading-view-OHCL
pip3 install -r requirements.txt
pip3 install flask flask-cors
python3 web_app.py
```
Then open: http://localhost:5000

---

## 💡 Pro Tips

1. **Keep it running**: Leave the command prompt/terminal open while using the tool
2. **Multiple tokens**: Open multiple terminal windows to monitor different tokens
3. **Bookmark**: Bookmark `http://localhost:5000` for quick access
4. **Autostart**: Create a shortcut to launch the web server automatically

---

## 📺 Video Tutorial

Can't follow written instructions? Here's what to search on YouTube:
- "How to install Python on Windows/Mac"
- "How to use pip install"
- "How to run Python scripts"

---

## 🆘 Still Need Help?

1. Check the error message carefully
2. Google the error message
3. Make sure Python is installed: `python --version`
4. Make sure you're in the right folder: `dir` (Windows) or `ls` (Mac/Linux)
5. Try the quick start commands above

---

**You're all set! Happy trading! 📈**
