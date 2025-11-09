#!/usr/bin/env python3
"""
Enhanced Visual Dashboard with Charts and Multiple Exchanges
"""

from flask import Flask, render_template, jsonify
import ccxt
import time
from datetime import datetime
import threading
from collections import deque

app = Flask(__name__)

# Price history storage (last 50 data points)
price_history = {
    'timestamps': deque(maxlen=50),
    'exchanges': {}
}

# Global state
latest_data = {
    'prices': {},
    'opportunities': [],
    'last_update': None,
    'iteration': 0,
    'spread_data': []
}

data_lock = threading.Lock()

# Initialize USA-friendly exchanges
exchanges = {}
exchange_configs = [
    ('Kraken', ccxt.kraken),
    ('Coinbase', ccxt.coinbase),
    ('Gemini', ccxt.gemini),
    ('KuCoin', ccxt.kucoin),
    ('Bitstamp', ccxt.bitstamp),
]

print("🔧 Initializing exchanges...")
for name, exchange_class in exchange_configs:
    try:
        exchanges[name] = exchange_class()
        print(f"  ✓ {name} initialized")
    except Exception as e:
        print(f"  ❌ {name} failed: {e}")

# Configuration
SYMBOL = 'BTC/USDT'
FEE_PERCENT = 0.2  # Realistic fee
UPDATE_INTERVAL = 15  # seconds


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
            # Try USD version if USDT fails
            try:
                ticker = exchange.fetch_ticker(symbol.replace('USDT', 'USD'))
                prices[exchange_name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last'],
                    'timestamp': ticker['timestamp']
                }
            except:
                pass

    return prices


def calculate_arbitrage(prices, fee_percent=FEE_PERCENT):
    """Calculate potential arbitrage opportunities"""
    opportunities = []
    exchange_names = list(prices.keys())

    for i, buy_exchange in enumerate(exchange_names):
        for sell_exchange in exchange_names[i+1:]:
            if prices[buy_exchange] and prices[sell_exchange]:
                # Forward direction
                buy_price = prices[buy_exchange]['ask']
                sell_price = prices[sell_exchange]['bid']

                gross_profit = ((sell_price - buy_price) / buy_price) * 100
                fees = fee_percent * 2
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

                # Reverse direction
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

    opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)
    return opportunities


def calculate_spread_data(prices):
    """Calculate spread data for visualization"""
    if len(prices) < 2:
        return []

    all_prices = [p['last'] for p in prices.values() if p]
    if not all_prices:
        return []

    min_price = min(all_prices)
    max_price = max(all_prices)
    spread_pct = ((max_price - min_price) / min_price) * 100

    spread_data = []
    for exchange_name, price_data in prices.items():
        if price_data:
            spread_data.append({
                'exchange': exchange_name,
                'price': price_data['last'],
                'diff_from_min': price_data['last'] - min_price,
                'diff_pct': ((price_data['last'] - min_price) / min_price) * 100
            })

    return sorted(spread_data, key=lambda x: x['price'])


def update_price_history(prices):
    """Update price history for charts"""
    with data_lock:
        timestamp = datetime.now().strftime('%H:%M:%S')
        price_history['timestamps'].append(timestamp)

        for exchange_name, price_data in prices.items():
            if price_data:
                if exchange_name not in price_history['exchanges']:
                    price_history['exchanges'][exchange_name] = deque(maxlen=50)
                price_history['exchanges'][exchange_name].append(price_data['last'])


def update_data_loop():
    """Background thread to continuously update data"""
    while True:
        try:
            prices = fetch_prices()
            opportunities = calculate_arbitrage(prices)
            spread_data = calculate_spread_data(prices)
            update_price_history(prices)

            with data_lock:
                latest_data['prices'] = prices
                latest_data['opportunities'] = opportunities
                latest_data['spread_data'] = spread_data
                latest_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                latest_data['iteration'] += 1

        except Exception as e:
            print(f"Error in update loop: {e}")

        time.sleep(UPDATE_INTERVAL)


@app.route('/')
def index():
    return render_template('visual_dashboard.html')


@app.route('/api/data')
def get_data():
    with data_lock:
        # Prepare chart data
        chart_data = {
            'labels': list(price_history['timestamps']),
            'datasets': []
        }

        colors = {
            'Kraken': '#5741D9',
            'Coinbase': '#0052FF',
            'Gemini': '#00DCFA',
            'KuCoin': '#24AE8F',
            'Bitstamp': '#00B143'
        }

        for exchange_name, prices in price_history['exchanges'].items():
            chart_data['datasets'].append({
                'label': exchange_name,
                'data': list(prices),
                'borderColor': colors.get(exchange_name, '#999'),
                'backgroundColor': 'transparent',
                'tension': 0.4
            })

        return jsonify({
            'prices': latest_data['prices'],
            'opportunities': latest_data['opportunities'],
            'spread_data': latest_data['spread_data'],
            'last_update': latest_data['last_update'],
            'iteration': latest_data['iteration'],
            'chart_data': chart_data,
            'symbol': SYMBOL,
            'fee_percent': FEE_PERCENT,
            'update_interval': UPDATE_INTERVAL
        })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Enhanced Crypto Arbitrage Dashboard")
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
