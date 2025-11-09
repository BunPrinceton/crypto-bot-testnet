#!/usr/bin/env python3
"""
Quick Arbitrage Scanner - Top coins only
"""

import ccxt
import time
from datetime import datetime

# Initialize exchanges - only use ones that work
exchanges = {}

print("🔧 Initializing exchanges...")

try:
    exchanges['Kraken'] = ccxt.kraken()
    print("  ✓ Kraken initialized")
except Exception as e:
    print(f"  ❌ Kraken failed: {e}")

try:
    exchanges['Coinbase'] = ccxt.coinbase()
    print("  ✓ Coinbase initialized")
except Exception as e:
    print(f"  ❌ Coinbase failed: {e}")

try:
    exchanges['Binance'] = ccxt.binance()
    print("  ✓ Binance initialized")
except Exception as e:
    print(f"  ❌ Binance failed: {e}")

# Top cryptocurrencies to check (symbols that should exist on most exchanges)
TOP_COINS = [
    'BTC/USDT', 'ETH/USDT', 'BTC/USD', 'ETH/USD',
    'SOL/USDT', 'SOL/USD', 'ADA/USDT', 'ADA/USD',
    'XRP/USDT', 'XRP/USD', 'DOT/USDT', 'DOT/USD',
    'AVAX/USDT', 'AVAX/USD', 'MATIC/USDT', 'MATIC/USD',
    'LINK/USDT', 'LINK/USD', 'UNI/USDT', 'UNI/USD',
    'ATOM/USDT', 'ATOM/USD', 'LTC/USDT', 'LTC/USD',
    'DOGE/USDT', 'DOGE/USD', 'SHIB/USDT',
]

FEE_PERCENT = 0.2  # 0.1% per trade
MIN_PROFIT = 0.3   # Minimum 0.3% net profit


def check_arbitrage(symbol):
    """Check arbitrage for a single symbol across all working exchanges"""
    prices = {}

    # Fetch from all exchanges
    for exchange_name, exchange in exchanges.items():
        try:
            ticker = exchange.fetch_ticker(symbol)
            prices[exchange_name] = {
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
            }
        except Exception:
            # Skip if symbol not available on this exchange
            pass

    # Need at least 2 exchanges
    if len(prices) < 2:
        return None

    # Find best opportunity
    best_opp = None
    best_profit = 0

    exchange_names = list(prices.keys())
    for i, buy_ex in enumerate(exchange_names):
        for sell_ex in exchange_names[i+1:]:
            # Try both directions
            for direction in [
                (buy_ex, sell_ex, prices[buy_ex]['ask'], prices[sell_ex]['bid']),
                (sell_ex, buy_ex, prices[sell_ex]['ask'], prices[buy_ex]['bid'])
            ]:
                buy_from, sell_to, buy_price, sell_price = direction

                if buy_price and sell_price and buy_price > 0:
                    gross_profit = ((sell_price - buy_price) / buy_price) * 100
                    net_profit = gross_profit - (FEE_PERCENT * 2)

                    if net_profit > best_profit and net_profit > MIN_PROFIT:
                        best_profit = net_profit
                        best_opp = {
                            'symbol': symbol,
                            'buy_from': buy_from,
                            'sell_to': sell_to,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'gross_profit_pct': gross_profit,
                            'net_profit_pct': net_profit,
                            'exchanges_checked': len(prices)
                        }

    return best_opp


def main():
    print(f"\n{'='*80}")
    print("🚀 QUICK ARBITRAGE SCANNER")
    print(f"{'='*80}")
    print(f"Checking {len(TOP_COINS)} popular cryptocurrencies")
    print(f"Working exchanges: {', '.join(exchanges.keys())}")
    print(f"Fee assumption: {FEE_PERCENT}% per trade ({FEE_PERCENT*2}% total)")
    print(f"Minimum profit threshold: {MIN_PROFIT}%")
    print(f"{'='*80}\n")

    opportunities = []
    checked = 0

    for symbol in TOP_COINS:
        checked += 1
        print(f"[{checked}/{len(TOP_COINS)}] Checking {symbol:15} ...", end=' ')

        try:
            opp = check_arbitrage(symbol)
            if opp:
                opportunities.append(opp)
                print(f"✓ {opp['net_profit_pct']:.3f}% profit ({opp['buy_from']} → {opp['sell_to']})")
            else:
                print("No profitable arbitrage")
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")

        time.sleep(0.3)  # Rate limiting

    print(f"\n{'='*80}")
    print(f"📊 RESULTS")
    print(f"{'='*80}")

    if not opportunities:
        print("\n❌ No profitable arbitrage opportunities found")
        print(f"   This is normal! Crypto markets are highly efficient.")
        print(f"   Most arbitrage opportunities exist for <1 second.")
        print(f"\n💡 Tips for finding arbitrage:")
        print(f"   • Check less popular altcoins (lower liquidity)")
        print(f"   • Use faster data (WebSockets instead of REST)")
        print(f"   • Look for triangle arbitrage (same exchange)")
        print(f"   • Monitor during high volatility periods")
    else:
        # Sort by profit
        opportunities.sort(key=lambda x: x['net_profit_pct'], reverse=True)

        print(f"\n🎯 Found {len(opportunities)} profitable opportunities!\n")
        print(f"{'#':<4} {'Symbol':<12} {'Route':<30} {'Buy':<12} {'Sell':<12} {'Net Profit':<12}")
        print("-"*90)

        for i, opp in enumerate(opportunities[:20], 1):
            route = f"{opp['buy_from']} → {opp['sell_to']}"
            print(f"{i:<4} {opp['symbol']:<12} {route:<30} "
                  f"${opp['buy_price']:<11.2f} ${opp['sell_price']:<11.2f} "
                  f"{opp['net_profit_pct']:<11.3f}%")

        print("\n" + "="*90)
        avg_profit = sum(o['net_profit_pct'] for o in opportunities) / len(opportunities)
        print(f"Average profit: {avg_profit:.3f}%")
        print(f"Maximum profit: {opportunities[0]['net_profit_pct']:.3f}% ({opportunities[0]['symbol']})")

    print(f"\n✅ Scan complete! Checked {checked} symbols\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
