#!/usr/bin/env python3
"""
Enhanced Price Monitor with Arbitrage Analysis
Integrates the arbitrage analyzer with price monitoring
"""

import ccxt
import time
from datetime import datetime
from arbitrage_analyzer import ArbitrageAnalyzer


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

                opportunities.append({
                    'buy_from': sell_exchange,
                    'sell_to': buy_exchange,
                    'buy_price': buy_price_reverse,
                    'sell_price': sell_price_reverse,
                    'gross_profit_pct': gross_profit_reverse,
                    'net_profit_pct': net_profit_reverse
                })

    # Only return profitable opportunities
    return [opp for opp in opportunities if opp['net_profit_pct'] > 0]


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
        print("\nNo profitable arbitrage opportunities found")
        return

    print("\n" + "="*80)
    print(f"🎯 {len(opportunities)} ARBITRAGE OPPORTUNITIES DETECTED!")
    print("="*80)

    for i, opp in enumerate(opportunities, 1):
        print(f"\nOpportunity #{i}:")
        print(f"  Buy from:  {opp['buy_from']:<15} @ ${opp['buy_price']:.2f}")
        print(f"  Sell to:   {opp['sell_to']:<15} @ ${opp['sell_price']:.2f}")
        print(f"  Gross Profit: {opp['gross_profit_pct']:.3f}%")
        print(f"  Net Profit:   {opp['net_profit_pct']:.3f}%")


def main():
    """Main monitoring loop with enhanced analytics"""
    print("🤖 Enhanced Crypto Arbitrage Bot")
    print("With Historical Analysis & Statistics")
    print("="*80 + "\n")

    # Initialize exchanges (using public APIs, no authentication needed)
    exchanges = {
        'Binance': ccxt.binance(),
        'Kraken': ccxt.kraken(),
        'Coinbase': ccxt.coinbase(),
    }

    # Symbols to monitor
    symbols = ['BTC/USDT', 'ETH/USDT']

    # Trading fee percentage (adjust based on your exchange tier)
    fee_percent = 0.1

    # Initialize analyzer with 0.2% alert threshold
    analyzer = ArbitrageAnalyzer(alert_threshold=0.2)

    print(f"Monitoring {len(symbols)} symbols on {len(exchanges)} exchanges")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Trading fee: {fee_percent}% per transaction")
    print(f"Alert threshold: {analyzer.alert_threshold}% net profit\n")
    print("Press Ctrl+C to stop and view statistics\n")

    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n{'#'*80}")
            print(f"Iteration #{iteration}")

            # Monitor each symbol
            for symbol in symbols:
                print(f"\n--- {symbol} ---")

                # Fetch prices
                prices = fetch_prices(exchanges, symbol)

                # Display prices
                display_prices(prices, symbol)

                # Calculate and display arbitrage opportunities
                opportunities = calculate_arbitrage(prices, fee_percent)
                display_opportunities(opportunities)

                # Record opportunities in analyzer
                for opp in opportunities:
                    analyzer.record_opportunity(symbol, opp)

            # Show any new alerts
            alerts = analyzer.get_alerts()
            if alerts:
                print("\n" + "="*80)
                print(f"🚨 {len(alerts)} NEW HIGH-VALUE ALERTS!")
                print("="*80)
                for alert in alerts[-3:]:  # Show last 3 alerts
                    print(f"\n{alert['message']}")
                analyzer.clear_alerts()

            # Show quick stats every 5 iterations
            if iteration % 5 == 0:
                print("\n" + "="*80)
                print("📊 QUICK STATS (Current Session)")
                print("="*80)
                stats = analyzer.get_statistics(hours=24)
                if stats['total_opportunities'] > 0:
                    print(f"Total Opportunities: {stats['total_opportunities']}")
                    print(f"Average Net Profit: {stats['net_profit']['mean']:.4f}%")
                    print(f"Best Net Profit: {stats['net_profit']['max']:.4f}%")

            # Wait before next iteration
            wait_time = 10
            print(f"\n⏳ Waiting {wait_time} seconds before next check...")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("👋 Shutting down...")
        print("="*80)

        # Display final statistics
        print("\n🎉 Final Session Statistics")
        analyzer.display_statistics(hours=24)
        analyzer.display_best_opportunities(hours=24, limit=10)

        # Save statistics to file
        analyzer.save_statistics()
        print(f"\n💾 Statistics saved to: {analyzer.stats_file}")
        print(f"📝 History saved to: {analyzer.history_file}")

        print("\nThanks for using the Enhanced Crypto Arbitrage Bot!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
