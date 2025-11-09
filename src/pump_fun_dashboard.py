#!/usr/bin/env python3
"""
Pump.fun Dashboard - Monitor Solana DEX tokens and arbitrage
"""

from flask import Flask, render_template, jsonify
import time
from datetime import datetime
import threading
from pump_fun_monitor import PumpFunMonitor

app = Flask(__name__)

# Global state
latest_data = {
    'tokens': [],
    'arbitrage_opportunities': [],
    'last_update': None,
    'iteration': 0
}

data_lock = threading.Lock()

# Popular Solana tokens to monitor
TOKEN_LIST = [
    {'symbol': 'BONK', 'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'},
    {'symbol': 'WEN', 'address': 'WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk'},
    {'symbol': 'POPCAT', 'address': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr'},
    {'symbol': 'WIF', 'address': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm'},
    {'symbol': 'MEW', 'address': 'MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5'},
]

monitor = PumpFunMonitor()


def calculate_arbitrage_for_token(token_data):
    """Calculate arbitrage opportunities for a token across DEXs"""
    opportunities = []

    if not token_data or 'pairs' not in token_data:
        return opportunities

    pairs = token_data['pairs']

    # Filter pairs with sufficient liquidity
    liquid_pairs = [
        p for p in pairs
        if float(p.get('liquidity', {}).get('usd', 0)) > 10000
    ]

    if len(liquid_pairs) < 2:
        return opportunities

    # Find best buy and sell prices
    for i, buy_pair in enumerate(liquid_pairs):
        for sell_pair in liquid_pairs[i+1:]:
            buy_price = float(buy_pair.get('priceUsd', 0))
            sell_price = float(sell_pair.get('priceUsd', 0))

            if buy_price <= 0 or sell_price <= 0:
                continue

            # Calculate both directions
            for bp, sp, buy_dex, sell_dex in [
                (buy_price, sell_price, buy_pair.get('dexId'), sell_pair.get('dexId')),
                (sell_price, buy_price, sell_pair.get('dexId'), buy_pair.get('dexId'))
            ]:
                gross_profit = ((sp - bp) / bp) * 100
                net_profit = gross_profit - 0.6  # 0.3% fee per trade

                if net_profit > 0:
                    opportunities.append({
                        'token': token_data.get('symbol', 'Unknown'),
                        'buy_dex': buy_dex,
                        'sell_dex': sell_dex,
                        'buy_price': bp,
                        'sell_price': sp,
                        'gross_profit_pct': gross_profit,
                        'net_profit_pct': net_profit,
                        'buy_liquidity': float(buy_pair.get('liquidity', {}).get('usd', 0)) if bp == buy_price else float(sell_pair.get('liquidity', {}).get('usd', 0)),
                        'sell_liquidity': float(sell_pair.get('liquidity', {}).get('usd', 0)) if sp == sell_price else float(buy_pair.get('liquidity', {}).get('usd', 0))
                    })

    return opportunities


def update_data_loop():
    """Background thread to update token data"""
    while True:
        try:
            tokens = []
            all_opportunities = []

            for token_info in TOKEN_LIST:
                try:
                    # Fetch token data
                    data = monitor.fetch_dexscreener_pairs(token_info['address'])

                    if data and 'pairs' in data:
                        pairs = data['pairs']

                        # Calculate average price and stats
                        prices = [float(p.get('priceUsd', 0)) for p in pairs if float(p.get('priceUsd', 0)) > 0]
                        liquidities = [float(p.get('liquidity', {}).get('usd', 0)) for p in pairs]
                        volumes = [float(p.get('volume', {}).get('h24', 0)) for p in pairs]

                        if prices:
                            token_data = {
                                'symbol': token_info['symbol'],
                                'address': token_info['address'],
                                'avg_price': sum(prices) / len(prices),
                                'min_price': min(prices),
                                'max_price': max(prices),
                                'spread_pct': ((max(prices) - min(prices)) / min(prices)) * 100 if prices else 0,
                                'total_liquidity': sum(liquidities),
                                'total_volume_24h': sum(volumes),
                                'num_pairs': len(pairs)
                            }

                            tokens.append(token_data)

                            # Calculate arbitrage opportunities
                            token_data['symbol'] = token_info['symbol']
                            token_data['pairs'] = pairs
                            opps = calculate_arbitrage_for_token(token_data)
                            all_opportunities.extend(opps)

                except Exception as e:
                    print(f"Error fetching {token_info['symbol']}: {e}")

                time.sleep(0.3)  # Rate limiting

            # Sort opportunities by profit
            all_opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)

            with data_lock:
                latest_data['tokens'] = tokens
                latest_data['arbitrage_opportunities'] = all_opportunities[:10]  # Top 10
                latest_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                latest_data['iteration'] += 1

        except Exception as e:
            print(f"Error in update loop: {e}")

        time.sleep(10)  # Update every 10 seconds


@app.route('/')
def index():
    return render_template('pump_fun_dashboard.html')


@app.route('/api/data')
def get_data():
    with data_lock:
        return jsonify(latest_data)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 PUMP.FUN DEX DASHBOARD")
    print("="*70)
    print(f"Monitoring: {len(TOKEN_LIST)} Solana tokens")
    print(f"Tokens: {', '.join([t['symbol'] for t in TOKEN_LIST])}")
    print("="*70)

    # Start background thread
    update_thread = threading.Thread(target=update_data_loop, daemon=True)
    update_thread.start()
    print("✓ Background update thread started")

    print("\n🌐 Starting web server...")
    print("📊 Dashboard: http://localhost:5002")
    print("\nPress Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5002, use_reloader=False)
