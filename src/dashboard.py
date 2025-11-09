#!/usr/bin/env python3
"""
Web Dashboard for Crypto Arbitrage Bot
Simple Flask dashboard with real-time price monitoring and arbitrage detection
"""

from flask import Flask, render_template, jsonify
import ccxt
import time
from datetime import datetime
import threading
import json

app = Flask(__name__)

# Global state to store latest data
latest_data = {
    'prices': {},
    'opportunities': [],
    'last_update': None,
    'iteration': 0
}

# Lock for thread-safe access
data_lock = threading.Lock()

# Initialize exchanges (using public APIs)
exchanges = {
    'Binance': ccxt.binance(),
    'Kraken': ccxt.kraken(),
    'Coinbase': ccxt.coinbase(),
}

# Configuration
SYMBOL = 'BTC/USDT'
FEE_PERCENT = 0.1
UPDATE_INTERVAL = 10  # seconds


def fetch_prices(symbol=SYMBOL):
    """Fetch current price for a symbol from multiple exchanges"""
    prices = {}

    for exchange_name, exchange in exchanges.items():
        try:
            ticker = exchange.fetch_ticker(symbol)
            prices[exchange_name] = {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            print(f"Error fetching from {exchange_name}: {e}")
            prices[exchange_name] = None

    return prices


def calculate_arbitrage(prices, fee_percent=FEE_PERCENT):
    """Calculate potential arbitrage opportunities"""
    opportunities = []
    exchange_names = list(prices.keys())

    for i, buy_exchange in enumerate(exchange_names):
        for sell_exchange in exchange_names[i+1:]:
            if prices[buy_exchange] and prices[sell_exchange]:
                buy_price = prices[buy_exchange]['ask']
                sell_price = prices[sell_exchange]['bid']

                # Calculate profit percentage after fees
                gross_profit = ((sell_price - buy_price) / buy_price) * 100
                fees = fee_percent * 2  # Buy fee + sell fee
                net_profit = gross_profit - fees

                if net_profit > 0:
                    opportunities.append({
                        'buy_from': buy_exchange,
                        'sell_to': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'gross_profit_pct': gross_profit,
                        'net_profit_pct': net_profit
                    })

                # Also check reverse direction
                buy_price_reverse = prices[sell_exchange]['ask']
                sell_price_reverse = prices[buy_exchange]['bid']

                gross_profit_reverse = ((sell_price_reverse - buy_price_reverse) / buy_price_reverse) * 100
                net_profit_reverse = gross_profit_reverse - fees

                if net_profit_reverse > 0:
                    opportunities.append({
                        'buy_from': sell_exchange,
                        'sell_to': buy_exchange,
                        'buy_price': buy_price_reverse,
                        'sell_price': sell_price_reverse,
                        'gross_profit_pct': gross_profit_reverse,
                        'net_profit_pct': net_profit_reverse
                    })

    # Sort by net profit descending
    opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)

    return opportunities


def update_data_loop():
    """Background thread to continuously update price data"""
    global latest_data
    iteration = 0

    while True:
        try:
            iteration += 1

            # Fetch prices
            prices = fetch_prices(SYMBOL)

            # Calculate arbitrage opportunities
            opportunities = calculate_arbitrage(prices, FEE_PERCENT)

            # Update global state with thread lock
            with data_lock:
                latest_data['prices'] = prices
                latest_data['opportunities'] = opportunities
                latest_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                latest_data['iteration'] = iteration

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Update #{iteration} - Found {len(opportunities)} opportunities")

            # Wait before next update
            time.sleep(UPDATE_INTERVAL)

        except Exception as e:
            print(f"Error in update loop: {e}")
            time.sleep(5)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html',
                         symbol=SYMBOL,
                         fee_percent=FEE_PERCENT,
                         update_interval=UPDATE_INTERVAL)


@app.route('/api/data')
def get_data():
    """API endpoint to fetch latest data"""
    with data_lock:
        return jsonify(latest_data)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    print("🚀 Crypto Arbitrage Bot Dashboard")
    print("="*60)
    print(f"Monitoring: {SYMBOL}")
    print(f"Exchanges: {', '.join(exchanges.keys())}")
    print(f"Fee: {FEE_PERCENT}%")
    print(f"Update Interval: {UPDATE_INTERVAL} seconds")
    print("="*60)

    # Start background update thread
    update_thread = threading.Thread(target=update_data_loop, daemon=True)
    update_thread.start()
    print("✓ Background update thread started")

    # Start Flask server
    print("\n🌐 Starting web server...")
    print("📊 Dashboard: http://localhost:5001")
    print("\nPress Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
