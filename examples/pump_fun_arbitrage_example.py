#!/usr/bin/env python3
"""
Arbitrage Detection Example
Shows how to detect price differences between DEXs
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pump_fun_monitor import PumpFunMonitor


def main():
    print("="*100)
    print("PUMP.FUN ARBITRAGE DETECTION EXAMPLE")
    print("="*100)

    monitor = PumpFunMonitor()

    # Token to analyze (BONK has good liquidity across multiple DEXs)
    token_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    token_symbol = "BONK"

    print(f"\nAnalyzing {token_symbol} across multiple DEX pairs...")
    print(f"Address: {token_address}\n")

    # Fetch all pairs for this token
    data = monitor.fetch_dexscreener_pairs(token_address)

    if not data or 'pairs' not in data:
        print("❌ Could not fetch data")
        return

    pairs = data['pairs']
    print(f"Found {len(pairs)} trading pairs\n")

    # Sort by liquidity (most liquid first)
    pairs_sorted = sorted(
        pairs,
        key=lambda p: float(p.get('liquidity', {}).get('usd', 0)),
        reverse=True
    )

    # Analyze top 10 most liquid pairs
    print("TOP 10 MOST LIQUID PAIRS:")
    print("="*100)
    print(f"{'#':<4} {'DEX':<12} {'Price (USD)':<18} {'Liquidity':<18} {'24h Volume':<18}")
    print("-"*100)

    prices = []
    for i, pair in enumerate(pairs_sorted[:10], 1):
        dex = pair.get('dexId', 'unknown')
        price_usd = float(pair.get('priceUsd', 0))
        liq = float(pair.get('liquidity', {}).get('usd', 0))
        vol = float(pair.get('volume', {}).get('h24', 0))

        print(f"{i:<4} {dex:<12} ${price_usd:<17.10f} ${liq:<17,.0f} ${vol:<17,.0f}")

        if liq > 50000:  # Only consider pairs with >$50k liquidity
            prices.append({
                'dex': dex,
                'price': price_usd,
                'liquidity': liq,
                'volume': vol
            })

    # Calculate arbitrage opportunities
    print("\n" + "="*100)
    print("ARBITRAGE ANALYSIS:")
    print("="*100)

    if len(prices) < 2:
        print("Not enough liquid pairs for arbitrage analysis")
        return

    # Find best buy and sell
    buy_pair = min(prices, key=lambda x: x['price'])
    sell_pair = max(prices, key=lambda x: x['price'])

    buy_price = buy_pair['price']
    sell_price = sell_pair['price']

    # Calculate profit
    gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100

    # Typical fees
    fee_pct = 0.3  # 0.3% per trade
    total_fees = fee_pct * 2  # Buy + sell

    net_profit_pct = gross_profit_pct - total_fees

    print(f"\nBest Buy:  {buy_pair['dex']:<12} @ ${buy_price:.10f} (Liq: ${buy_pair['liquidity']:,.0f})")
    print(f"Best Sell: {sell_pair['dex']:<12} @ ${sell_price:.10f} (Liq: ${sell_pair['liquidity']:,.0f})")
    print(f"\nGross Spread:    {gross_profit_pct:>8.3f}%")
    print(f"Trading Fees:    {total_fees:>8.3f}%")
    print(f"Net Profit:      {net_profit_pct:>8.3f}%")

    if net_profit_pct > 0:
        print(f"\n✅ ARBITRAGE OPPORTUNITY DETECTED!")
        print(f"   Strategy: Buy on {buy_pair['dex']}, Sell on {sell_pair['dex']}")
        print(f"   Expected Profit: {net_profit_pct:.3f}%")
        print(f"\n⚠️  IMPORTANT:")
        print(f"   - Check actual slippage on both DEXs")
        print(f"   - Ensure sufficient liquidity for your trade size")
        print(f"   - Account for gas fees (~$0.00025 per tx on Solana)")
        print(f"   - Price may move during execution")
    else:
        print(f"\n❌ No profitable arbitrage opportunity")
        print(f"   Spread too small to cover fees ({net_profit_pct:.3f}%)")
        print(f"   Need at least {total_fees:.1f}% spread to break even")

    # Calculate required trade size for worthwhile profit
    min_profit_usd = 5  # Minimum $5 profit to make it worthwhile
    if net_profit_pct > 0:
        required_trade_size = min_profit_usd / (net_profit_pct / 100)
        print(f"\n💡 For ${min_profit_usd} profit, need ${required_trade_size:,.0f} trade size")

    print("\n" + "="*100)


if __name__ == "__main__":
    main()
