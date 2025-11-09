#!/usr/bin/env python3
"""
Multi-Coin Dashboard - Monitor 20+ cryptocurrencies simultaneously
"""

from flask import Flask, render_template, jsonify
import ccxt
import time
from datetime import datetime
import threading
from collections import deque
import random

app = Flask(__name__)

# Global state
latest_data = {
    'all_opportunities': [],
    'coin_data': {},
    'last_update': None,
    'iteration': 0,
    'demo_mode': False,
    'stats': {}
}

data_lock = threading.Lock()

# Initialize exchanges
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

# Top 25 cryptocurrencies to monitor
SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT',
    'UNI/USDT', 'ATOM/USDT', 'LTC/USDT', 'BCH/USDT', 'ALGO/USDT',
    'XLM/USDT', 'NEAR/USDT', 'FIL/USDT', 'APT/USDT', 'ARB/USDT',
    'OP/USDT', 'INJ/USDT', 'TIA/USDT', 'SUI/USDT', 'SEI/USDT'
]

FEE_PERCENT = 0.2
UPDATE_INTERVAL = 20  # Longer interval since we're checking many coins


def add_demo_variation(prices, symbol):
    """Add variations for demo mode"""
    if not prices or len(prices) < 2:
        return prices

    demo_prices = {}
    exchange_names = list(prices.keys())

    # Randomly decide if this symbol gets arbitrage opportunity
    # 30% chance of having an opportunity in demo mode
    has_opportunity = random.random() < 0.3

    for i, exchange_name in enumerate(exchange_names):
        if prices[exchange_name]:
            if has_opportunity:
                # Create larger variation for opportunity
                if i == 0:
                    variation = random.uniform(0.006, 0.012)  # Higher
                elif i == len(exchange_names) - 1:
                    variation = random.uniform(-0.012, -0.006)  # Lower
                else:
                    variation = random.uniform(-0.004, 0.004)
            else:
                # Small variation, no opportunity
                variation = random.uniform(-0.002, 0.002)

            multiplier = 1 + variation

            demo_prices[exchange_name] = {
                'bid': prices[exchange_name]['bid'] * multiplier,
                'ask': prices[exchange_name]['ask'] * multiplier,
                'last': prices[exchange_name]['last'] * multiplier,
                'timestamp': prices[exchange_name]['timestamp']
            }
        else:
            demo_prices[exchange_name] = prices[exchange_name]

    return demo_prices


def fetch_prices_for_symbol(symbol, demo_mode=False):
    """Fetch prices for a single symbol"""
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
        except Exception:
            # Try USD version
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

    if demo_mode and prices:
        prices = add_demo_variation(prices, symbol)

    return prices


def calculate_arbitrage(symbol, prices, fee_percent=FEE_PERCENT):
    """Calculate arbitrage for a symbol"""
    opportunities = []
    exchange_names = list(prices.keys())

    for i, buy_exchange in enumerate(exchange_names):
        for sell_exchange in exchange_names[i+1:]:
            if prices[buy_exchange] and prices[sell_exchange]:
                # Try both directions
                for buy_ex, sell_ex, buy_p, sell_p in [
                    (buy_exchange, sell_exchange, prices[buy_exchange]['ask'], prices[sell_exchange]['bid']),
                    (sell_exchange, buy_exchange, prices[sell_exchange]['ask'], prices[buy_exchange]['bid'])
                ]:
                    if buy_p and sell_p and buy_p > 0:
                        gross_profit = ((sell_p - buy_p) / buy_p) * 100
                        net_profit = gross_profit - (fee_percent * 2)

                        if net_profit > 0:
                            opportunities.append({
                                'symbol': symbol,
                                'buy_from': buy_ex,
                                'sell_to': sell_ex,
                                'buy_price': buy_p,
                                'sell_price': sell_p,
                                'gross_profit_pct': gross_profit,
                                'net_profit_pct': net_profit
                            })

    return opportunities


def calculate_coin_stats(symbol, prices):
    """Calculate stats for a coin"""
    price_values = [p['last'] for p in prices.values() if p]

    if not price_values:
        return None

    avg = sum(price_values) / len(price_values)
    min_price = min(price_values)
    max_price = max(price_values)
    spread = ((max_price - min_price) / min_price) * 100

    return {
        'symbol': symbol,
        'avg_price': avg,
        'min_price': min_price,
        'max_price': max_price,
        'spread_pct': spread,
        'exchanges_online': len(price_values)
    }


def update_data_loop():
    """Background thread to update all coins"""
    coin_index = 0

    while True:
        try:
            with data_lock:
                demo_mode = latest_data['demo_mode']

            # Process coins in batches to avoid rate limits
            symbols_to_check = SYMBOLS[coin_index:coin_index+5]

            for symbol in symbols_to_check:
                try:
                    prices = fetch_prices_for_symbol(symbol, demo_mode)
                    opportunities = calculate_arbitrage(symbol, prices)
                    stats = calculate_coin_stats(symbol, prices)

                    with data_lock:
                        latest_data['coin_data'][symbol] = {
                            'prices': prices,
                            'opportunities': opportunities,
                            'stats': stats
                        }
                except Exception as e:
                    print(f"Error processing {symbol}: {e}")

                time.sleep(0.5)  # Rate limiting

            # Update aggregated opportunities
            with data_lock:
                all_opps = []
                for coin_data in latest_data['coin_data'].values():
                    if coin_data.get('opportunities'):
                        all_opps.extend(coin_data['opportunities'])

                all_opps.sort(key=lambda x: x['net_profit_pct'], reverse=True)
                latest_data['all_opportunities'] = all_opps[:20]  # Top 20
                latest_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                latest_data['iteration'] += 1

                # Calculate global stats
                latest_data['stats'] = {
                    'total_coins': len(latest_data['coin_data']),
                    'coins_with_opps': sum(1 for cd in latest_data['coin_data'].values()
                                          if cd.get('opportunities')),
                    'total_opps': len(all_opps),
                    'best_profit': all_opps[0]['net_profit_pct'] if all_opps else 0
                }

            # Move to next batch
            coin_index = (coin_index + 5) % len(SYMBOLS)

        except Exception as e:
            print(f"Error in update loop: {e}")

        time.sleep(2)


@app.route('/')
def index():
    return render_template('multi_coin_dashboard.html')


@app.route('/api/data')
def get_data():
    with data_lock:
        return jsonify({
            'all_opportunities': latest_data['all_opportunities'],
            'coin_data': latest_data['coin_data'],
            'stats': latest_data['stats'],
            'last_update': latest_data['last_update'],
            'iteration': latest_data['iteration'],
            'demo_mode': latest_data['demo_mode'],
            'symbols': SYMBOLS,
            'fee_percent': FEE_PERCENT
        })


@app.route('/api/toggle_demo', methods=['POST'])
def toggle_demo():
    with data_lock:
        latest_data['demo_mode'] = not latest_data['demo_mode']
        # Clear data to force refresh with new mode
        latest_data['coin_data'] = {}
        mode = latest_data['demo_mode']

    print(f"🎭 Demo mode: {'ON' if mode else 'OFF'}")
    return jsonify({'demo_mode': mode})


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 MULTI-COIN ARBITRAGE DASHBOARD")
    print("="*70)
    print(f"Monitoring: {len(SYMBOLS)} cryptocurrencies")
    print(f"Exchanges: {', '.join(exchanges.keys())}")
    print(f"Fee: {FEE_PERCENT}%")
    print(f"\n💡 Coins: {', '.join([s.split('/')[0] for s in SYMBOLS[:10]])}...")
    print("💡 Click 'DEMO MODE' button to simulate arbitrage opportunities")
    print("="*70)

    # Start background thread
    update_thread = threading.Thread(target=update_data_loop, daemon=True)
    update_thread.start()
    print("✓ Background update thread started")

    print("\n🌐 Starting web server...")
    print("📊 Dashboard: http://localhost:5001")
    print("\nPress Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
