#!/usr/bin/env python3
"""
Basic example: Fetch Pump.fun token prices
Minimal code to get started
"""

import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pump_fun_monitor import PumpFunMonitor


def main():
    print("="*80)
    print("BASIC PUMP.FUN EXAMPLE - Get Token Prices")
    print("="*80)

    # Initialize monitor
    monitor = PumpFunMonitor()

    # Popular Solana memecoin addresses
    tokens = {
        "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "WEN": "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
    }

    print(f"\nFetching prices for {len(tokens)} tokens...\n")

    # Fetch each token
    for name, address in tokens.items():
        data = monitor.fetch_token_price_dexscreener(address)

        if data:
            print(f"{name:>10}: ${data['price_usd']:<15.8f} | "
                  f"24h Vol: ${data['volume_24h']:>12,.0f} | "
                  f"Liq: ${data['liquidity_usd']:>12,.0f}")
        else:
            print(f"{name:>10}: Data not available")

    print("\n" + "="*80)
    print("✅ Done! Check src/pump_fun_monitor.py for more features.")
    print("="*80)


if __name__ == "__main__":
    main()
