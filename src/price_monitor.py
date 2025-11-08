#!/usr/bin/env python3
"""
Simple price monitor for cryptocurrency arbitrage detection
This is your starting point for tonight's prototype!
"""

import ccxt
import time
from datetime import datetime


def fetch_prices(exchanges, symbol='BTC/USDT'):
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


def calculate_arbitrage(prices, fee_percent=0.1):
    """
    Calculate potential arbitrage opportunities
    fee_percent: Trading fee percentage (default 0.1% = Binance fee)
    """
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

    return opportunities


def display_prices(prices, symbol):
    """Display prices in a formatted table"""
    print("\n" + "="*80)
    print(f"Prices for {symbol} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(f"{'Exchange':<15} {'Bid':<12} {'Ask':<12} {'Last':<12}")
    print("-"*80)

    for exchange_name, data in prices.items():
        if data:
            print(f"{exchange_name:<15} ${data['bid']:<11.2f} ${data['ask']:<11.2f} ${data['last']:<11.2f}")
        else:
            print(f"{exchange_name:<15} {'ERROR':>12} {'ERROR':>12} {'ERROR':>12}")


def display_opportunities(opportunities):
    """Display arbitrage opportunities"""
    if not opportunities:
        print("\n❌ No arbitrage opportunities found")
        return

    print("\n" + "="*80)
    print("🎯 ARBITRAGE OPPORTUNITIES DETECTED!")
    print("="*80)

    for i, opp in enumerate(opportunities, 1):
        print(f"\nOpportunity #{i}:")
        print(f"  Buy from:  {opp['buy_from']:<15} @ ${opp['buy_price']:.2f}")
        print(f"  Sell to:   {opp['sell_to']:<15} @ ${opp['sell_price']:.2f}")
        print(f"  Gross Profit: {opp['gross_profit_pct']:.3f}%")
        print(f"  Net Profit:   {opp['net_profit_pct']:.3f}% ✅")


def main():
    """Main monitoring loop"""
    print("🤖 Crypto Arbitrage Bot - Price Monitor")
    print("Starting up...\n")

    # Initialize exchanges (using public APIs, no authentication needed)
    exchanges = {
        'Binance': ccxt.binance(),
        'Kraken': ccxt.kraken(),
        'Coinbase': ccxt.coinbase(),
    }

    # Symbol to monitor
    symbol = 'BTC/USDT'

    # Trading fee percentage (adjust based on your exchange tier)
    fee_percent = 0.1

    print(f"Monitoring {symbol} on {len(exchanges)} exchanges")
    print(f"Assuming {fee_percent}% trading fee per transaction\n")
    print("Press Ctrl+C to stop\n")

    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'#'*80}")
            print(f"Iteration #{iteration}")

            # Fetch prices
            prices = fetch_prices(exchanges, symbol)

            # Display prices
            display_prices(prices, symbol)

            # Calculate and display arbitrage opportunities
            opportunities = calculate_arbitrage(prices, fee_percent)
            display_opportunities(opportunities)

            # Wait before next iteration
            print(f"\n⏳ Waiting 10 seconds before next check...")
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        print("Thanks for using the Crypto Arbitrage Bot!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
