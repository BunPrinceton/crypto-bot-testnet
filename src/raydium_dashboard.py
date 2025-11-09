#!/usr/bin/env python3
"""
Raydium Dashboard - Monitor Raydium DEX pools and liquidity
"""

from flask import Flask, render_template, jsonify
import time
from datetime import datetime
import threading
from raydium_monitor import RaydiumMonitor
import ccxt

app = Flask(__name__)

# Global state
latest_data = {
    'pools': [],
    'last_update': None,
    'iteration': 0,
    'cex_prices': {}
}

data_lock = threading.Lock()

# Initialize monitors
raydium = RaydiumMonitor()

# Pool list from raydium_monitor.py
POOL_LIST = [
    {'symbol': 'SOL/USDC', 'pool_id': '58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2'},
    {'symbol': 'SOL/USDT', 'pool_id': '7XawhbbxtsRcQA8KTkHT9f9nc6d69UwqCDh6U5EEbEmX'},
    {'symbol': 'RAY/USDC', 'pool_id': '6UmmUiYoBjSrhakAobJw8BvkmJtDVxaeBtbt7rxWo1mg'},
    {'symbol': 'RAY/SOL', 'pool_id': 'AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA'},
    {'symbol': 'BONK/USDC', 'pool_id': 'Hs97TCZeuYiJxooo3U73qEHXg3dKpRL4uYKYRryEK9CF'},
    {'symbol': 'JUP/USDC', 'pool_id': '8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6'},
    {'symbol': 'ORCA/USDC', 'pool_id': '2p7nYbtPBgtmY69NsE8DAW6szpRJn7tQvDnqvoEWQvjY'},
    {'symbol': 'PYTH/USDC', 'pool_id': '4UBB3GJhTZUKLXDhFkSjGLCUoJz4U8uFNKTNXmqzJiSG'},
    {'symbol': 'JTO/USDC', 'pool_id': '5r878BSWPtoXgnqaeFJi7BCycKZ5CodBB2vS9SeiV8q'},
    {'symbol': 'WIF/USDC', 'pool_id': 'EP2ib6dYdEeqD8MfE2ezHCxX3kP3K2eLKkirfPm5eyMx'},
]

# Initialize exchange for CEX comparison
exchange = ccxt.kraken()


def calculate_slippage(trade_size_usd, liquidity_usd):
    """Calculate slippage"""
    if liquidity_usd == 0:
        return 0
    ratio = trade_size_usd / liquidity_usd
    if ratio >= 1:
        return 100
    slippage = ratio / (2 * (1 - ratio))
    return slippage * 100


def fetch_cex_prices():
    """Fetch CEX prices for comparison"""
    prices = {}
    symbols_to_check = ['SOL/USDT', 'RAY/USDT']

    for symbol in symbols_to_check:
        try:
            ticker = exchange.fetch_ticker(symbol)
            prices[symbol] = ticker['last']
        except:
            pass

    return prices


def update_data_loop():
    """Background thread to update pool data"""
    while True:
        try:
            pools = []

            # Fetch all pools
            for pool_info in POOL_LIST:
                try:
                    pair = raydium.fetch_pool_data(pool_info['pool_id'], pool_info['symbol'])

                    if pair:
                        price_usd = float(pair.get('price_usd', 0))
                        liquidity_usd = float(pair.get('liquidity_usd', 0))
                        volume_24h = float(pair.get('volume_24h', 0))
                        price_change_24h = float(pair.get('price_change_24h', 0))
                        total_txns = pair.get('txns_24h_buys', 0) + pair.get('txns_24h_sells', 0)

                        # Calculate slippage for different trade sizes
                        slippage_data = []
                        for trade_size in [100, 1000, 5000, 10000, 50000]:
                            slippage = calculate_slippage(trade_size, liquidity_usd)
                            slippage_data.append({
                                'size': trade_size,
                                'slippage': slippage
                            })

                        pool_data = {
                            'symbol': pool_info['symbol'],
                            'pool_id': pool_info['pool_id'],
                            'price_usd': price_usd,
                            'liquidity_usd': liquidity_usd,
                            'volume_24h': volume_24h,
                            'price_change_24h': price_change_24h,
                            'total_txns_24h': total_txns,
                            'slippage_data': slippage_data,
                            'dex_id': pair.get('dex', 'raydium')
                        }

                        pools.append(pool_data)

                except Exception as e:
                    print(f"Error fetching {pool_info['symbol']}: {e}")

                time.sleep(0.3)  # Rate limiting

            # Fetch CEX prices
            cex_prices = fetch_cex_prices()

            with data_lock:
                latest_data['pools'] = pools
                latest_data['cex_prices'] = cex_prices
                latest_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                latest_data['iteration'] += 1

        except Exception as e:
            print(f"Error in update loop: {e}")

        time.sleep(15)  # Update every 15 seconds


@app.route('/')
def index():
    return render_template('raydium_dashboard.html')


@app.route('/api/data')
def get_data():
    with data_lock:
        return jsonify(latest_data)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 RAYDIUM DEX DASHBOARD")
    print("="*70)
    print(f"Monitoring: {len(POOL_LIST)} Raydium pools")
    print(f"Pools: {', '.join([p['symbol'] for p in POOL_LIST])}")
    print("="*70)

    # Start background thread
    update_thread = threading.Thread(target=update_data_loop, daemon=True)
    update_thread.start()
    print("✓ Background update thread started")

    print("\n🌐 Starting web server...")
    print("📊 Dashboard: http://localhost:5003")
    print("\nPress Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5003, use_reloader=False)
