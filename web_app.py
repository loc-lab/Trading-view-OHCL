#!/usr/bin/env python3
"""
Web interface for Intraday Token Fetcher
Run this file and open http://localhost:5000 in your browser
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from intraday_fetcher import IntradayTokenFetcher
import json
import io
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

fetcher = IntradayTokenFetcher()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    """Get available trading symbols"""
    try:
        limit = int(request.args.get('limit', 50))
        symbols = fetcher.get_available_symbols(limit=limit)
        return jsonify({
            'success': True,
            'symbols': symbols
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fetch', methods=['POST'])
def fetch_data():
    """Fetch intraday data for a symbol"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        interval = data.get('interval', '5m')
        limit = int(data.get('limit', 50))

        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400

        # Fetch data
        df = fetcher.fetch_intraday_data(symbol, interval, limit)
        stats_24h = fetcher.get_24h_stats(symbol)
        current_price = fetcher.get_current_price(symbol)

        # Calculate summary
        latest = df.iloc[-1]
        oldest = df.iloc[0]
        intraday_change = latest['close'] - oldest['open']
        intraday_change_pct = (intraday_change / oldest['open'] * 100)

        # Prepare OHLC data for display
        ohlc_data = []
        for _, row in df.iterrows():
            ohlc_data.append({
                'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'open': round(row['open'], 8),
                'high': round(row['high'], 8),
                'low': round(row['low'], 8),
                'close': round(row['close'], 8),
                'volume': round(row['volume'], 2),
                'price_change_pct': round(row['price_change_pct'], 2)
            })

        # Prepare TradingView format data
        tv_data = fetcher.export_to_tradingview_format(df)

        response_data = {
            'success': True,
            'symbol': symbol,
            'interval': interval,
            'summary': {
                'current_price': round(current_price, 8),
                'intraday_change': round(intraday_change, 8),
                'intraday_change_pct': round(intraday_change_pct, 2),
                'price_change_24h': round(stats_24h['price_change'], 8),
                'price_change_pct_24h': round(stats_24h['price_change_pct'], 2),
                'high_24h': round(stats_24h['high'], 8),
                'low_24h': round(stats_24h['low'], 8),
                'volume_24h': round(stats_24h['volume'], 2),
                'quote_volume_24h': round(stats_24h['quote_volume'], 2),
                'trades_24h': stats_24h['trades'],
                'candles': len(df),
                'time_range': f"{df['timestamp'].iloc[0].strftime('%Y-%m-%d %H:%M')} to {df['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M')}"
            },
            'ohlc_data': ohlc_data,
            'tradingview_data': tv_data
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/json', methods=['POST'])
def export_json():
    """Export data to JSON file"""
    try:
        data = request.get_json()
        tv_data = data.get('data')

        if not tv_data:
            return jsonify({
                'success': False,
                'error': 'No data to export'
            }), 400

        # Create JSON file in memory
        json_str = json.dumps(tv_data, indent=2)
        json_bytes = io.BytesIO(json_str.encode('utf-8'))

        filename = f"tradingview_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export data to CSV file"""
    try:
        data = request.get_json()
        ohlc_data = data.get('data')

        if not ohlc_data:
            return jsonify({
                'success': False,
                'error': 'No data to export'
            }), 400

        # Convert to DataFrame
        df = pd.DataFrame(ohlc_data)

        # Create CSV file in memory
        csv_str = df.to_csv(index=False)
        csv_bytes = io.BytesIO(csv_str.encode('utf-8'))

        filename = f"ohlc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Intraday Token Fetcher - Web Interface")
    print("="*80)
    print("\n📡 Server starting...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("⏸️  Press CTRL+C to stop the server\n")
    print("="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
