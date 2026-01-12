#!/bin/bash
# Setup script for Mac/Linux

echo "=========================================="
echo "  Intraday Token Fetcher - Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To run the CLI version:"
echo "  python3 intraday_fetcher.py BTCUSDT"
echo ""
echo "To run the web version:"
echo "  python3 web_app.py"
echo "  Then open: http://localhost:5000"
echo ""
echo "=========================================="
