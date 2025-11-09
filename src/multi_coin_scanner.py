#!/usr/bin/env python3
"""
Multi-Coin Arbitrage Scanner
Scans top cryptocurrencies for real arbitrage opportunities
"""

import ccxt
import time
from datetime import datetime
import json

# Initialize exchanges
exchanges = {
    'Binance': ccxt.binance(),
    'Kraken': ccxt.kraken(),
    'Coinbase': ccxt.coinbase(),
}

# Configuration
FEE_PERCENT = 0.2  # More realistic fee (0.1% each side)
MIN_PROFIT = 0.3  # Minimum 0.3% profit to be worth it
TOP_N = 200  # Number of coins to check


def get_common_symbols():
    """Get symbols that exist on multiple exchanges"""
    print("🔍 Finding common trading pairs across exchanges...")

    all_symbols = {}
    for exchange_name, exchange in exchanges.items():
        try:
            markets = exchange.load_markets()
            # Filter for USDT pairs (most liquid)
            symbols = [s for s in markets.keys() if '/USDT' in s or '/USD' in s]
            all_symbols[exchange_name] = set(symbols)
            print(f"  ✓ {exchange_name}: {len(symbols)} USD(T) pairs")
        except Exception as e:
            print(f"  ❌ Error loading {exchange_name}: {str(e)[:100]}")
            all_symbols[exchange_name] = set()

    # Remove exchanges that failed to load
    all_symbols = {k: v for k, v in all_symbols.items() if v}

    if len(all_symbols) < 2:
        print("❌ Need at least 2 working exchanges")
        return []

    # Find intersection of working exchanges
    common = set.intersection(*all_symbols.values())
    print(f"\n✓ Found {len(common)} common pairs across {len(all_symbols)} exchanges")
    print(f"  Working exchanges: {', '.join(all_symbols.keys())}")
    return sorted(list(common))[:TOP_N]


def fetch_price(exchange, symbol):
    """Fetch price for a single symbol from an exchange"""
    try:
        ticker = exchange.fetch_ticker(symbol)
        return {
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'last': ticker['last'],
        }
    except Exception as e:
        return None


def scan_symbol(symbol):
    """Scan a single symbol for arbitrage opportunities"""
    prices = {}

    # Fetch from all exchanges
    for exchange_name, exchange in exchanges.items():
        price = fetch_price(exchange, symbol)
        if price:
            prices[exchange_name] = price

    # Need at least 2 exchanges with data
    if len(prices) < 2:
        return None

    # Find best arbitrage opportunity for this symbol
    best_opportunity = None
    best_profit = 0

    exchange_names = list(prices.keys())
    for i, buy_exchange in enumerate(exchange_names):
        for sell_exchange in exchange_names[i+1:]:
            # Forward direction
            buy_price = prices[buy_exchange]['ask']
            sell_price = prices[sell_exchange]['bid']

            gross_profit = ((sell_price - buy_price) / buy_price) * 100
            net_profit = gross_profit - (FEE_PERCENT * 2)

            if net_profit > best_profit and net_profit > MIN_PROFIT:
                best_profit = net_profit
                best_opportunity = {
                    'symbol': symbol,
                    'buy_from': buy_exchange,
                    'sell_to': sell_exchange,
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'gross_profit_pct': gross_profit,
                    'net_profit_pct': net_profit,
                    'price_difference': sell_price - buy_price
                }

            # Reverse direction
            buy_price_rev = prices[sell_exchange]['ask']
            sell_price_rev = prices[buy_exchange]['bid']

            gross_profit_rev = ((sell_price_rev - buy_price_rev) / buy_price_rev) * 100
            net_profit_rev = gross_profit_rev - (FEE_PERCENT * 2)

            if net_profit_rev > best_profit and net_profit_rev > MIN_PROFIT:
                best_profit = net_profit_rev
                best_opportunity = {
                    'symbol': symbol,
                    'buy_from': sell_exchange,
                    'sell_to': buy_exchange,
                    'buy_price': buy_price_rev,
                    'sell_price': sell_price_rev,
                    'gross_profit_pct': gross_profit_rev,
                    'net_profit_pct': net_profit_rev,
                    'price_difference': sell_price_rev - buy_price_rev
                }

    return best_opportunity


def scan_all_symbols():
    """Scan all common symbols and return best opportunities"""
    print("\n🚀 Starting multi-coin arbitrage scan...")
    print(f"Configuration: {FEE_PERCENT}% fees, minimum {MIN_PROFIT}% profit\n")

    # Get common symbols
    symbols = get_common_symbols()
    if not symbols:
        print("❌ No common symbols found!")
        return []

    print(f"\n📊 Scanning {len(symbols)} symbols for arbitrage opportunities...")
    print("="*80)

    opportunities = []
    checked = 0

    for symbol in symbols:
        checked += 1
        if checked % 20 == 0:
            print(f"Progress: {checked}/{len(symbols)} symbols checked, {len(opportunities)} opportunities found...")

        opp = scan_symbol(symbol)
        if opp:
            opportunities.append(opp)
            print(f"✓ {symbol}: {opp['net_profit_pct']:.3f}% profit ({opp['buy_from']} → {opp['sell_to']})")

        # Rate limiting - be nice to the APIs
        time.sleep(0.5)

    print("="*80)
    print(f"\n✅ Scan complete! Checked {checked} symbols")
    print(f"🎯 Found {len(opportunities)} profitable arbitrage opportunities\n")

    # Sort by profit
    opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)

    return opportunities


def display_opportunities(opportunities, top_n=20):
    """Display the top opportunities"""
    if not opportunities:
        print("❌ No arbitrage opportunities found above minimum threshold")
        print(f"   (Minimum profit: {MIN_PROFIT}% after {FEE_PERCENT*2}% fees)")
        return

    print("="*100)
    print(f"🏆 TOP {min(top_n, len(opportunities))} ARBITRAGE OPPORTUNITIES")
    print("="*100)
    print(f"{'#':<4} {'Symbol':<12} {'Route':<25} {'Buy Price':<15} {'Sell Price':<15} {'Net Profit':<12}")
    print("-"*100)

    for i, opp in enumerate(opportunities[:top_n], 1):
        route = f"{opp['buy_from']} → {opp['sell_to']}"
        print(f"{i:<4} {opp['symbol']:<12} {route:<25} "
              f"${opp['buy_price']:<14.4f} ${opp['sell_price']:<14.4f} "
              f"{opp['net_profit_pct']:<11.3f}%")

    print("="*100)

    # Statistics
    if opportunities:
        avg_profit = sum(o['net_profit_pct'] for o in opportunities) / len(opportunities)
        max_profit = opportunities[0]['net_profit_pct']
        print(f"\n📈 Statistics:")
        print(f"   Total opportunities: {len(opportunities)}")
        print(f"   Average net profit: {avg_profit:.3f}%")
        print(f"   Maximum net profit: {max_profit:.3f}% ({opportunities[0]['symbol']})")
        print(f"   Minimum net profit: {opportunities[-1]['net_profit_pct']:.3f}% ({opportunities[-1]['symbol']})")


def save_opportunities(opportunities, filename='data/arbitrage_opportunities.json'):
    """Save opportunities to JSON file"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'fee_percent': FEE_PERCENT,
            'min_profit': MIN_PROFIT,
            'top_n': TOP_N
        },
        'opportunities': opportunities
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Saved opportunities to {filename}")


if __name__ == "__main__":
    try:
        # Run the scan
        opportunities = scan_all_symbols()

        # Display results
        display_opportunities(opportunities, top_n=20)

        # Save to file
        if opportunities:
            save_opportunities(opportunities)

        print("\n✨ Scan complete!")

    except KeyboardInterrupt:
        print("\n\n👋 Scan interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
