#!/usr/bin/env python3
"""
Quick test script to verify the analyzer is working
"""

from arbitrage_analyzer import ArbitrageAnalyzer
import random
import time
from datetime import datetime, timedelta


def generate_test_data(analyzer, num_records=50):
    """Generate test data for demonstration"""
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT']
    exchanges = ['Binance', 'Kraken', 'Coinbase', 'KuCoin']

    print(f"Generating {num_records} test opportunities...")

    for i in range(num_records):
        symbol = random.choice(symbols)
        buy_from = random.choice(exchanges)
        sell_to = random.choice([e for e in exchanges if e != buy_from])

        # Generate realistic prices
        base_prices = {
            'BTC/USDT': 43000,
            'ETH/USDT': 2300,
            'SOL/USDT': 95,
            'ADA/USDT': 0.45
        }

        base_price = base_prices[symbol]

        # Random price variation (0.01% to 0.8%)
        variation = random.uniform(0.0001, 0.008)
        buy_price = base_price * (1 + random.uniform(-0.002, 0.002))
        sell_price = buy_price * (1 + variation)

        gross_profit_pct = ((sell_price - buy_price) / buy_price) * 100
        net_profit_pct = gross_profit_pct - 0.2  # 0.1% fee on each side

        opportunity = {
            'buy_from': buy_from,
            'sell_to': sell_to,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'gross_profit_pct': gross_profit_pct,
            'net_profit_pct': net_profit_pct
        }

        # Record with varied timestamps (spread over last hour)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
        analyzer.record_opportunity(symbol, opportunity, timestamp)

        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_records} opportunities...")

    print(f"✅ Generated {num_records} test opportunities\n")


def main():
    """Run comprehensive test"""
    print("="*80)
    print("🧪 ARBITRAGE ANALYZER TEST SUITE")
    print("="*80 + "\n")

    # Initialize analyzer
    print("1. Initializing analyzer...")
    analyzer = ArbitrageAnalyzer(alert_threshold=0.3)
    print(f"   Data directory: {analyzer.data_dir}")
    print(f"   Alert threshold: {analyzer.alert_threshold}%")
    print("   ✅ Analyzer initialized\n")

    # Generate test data
    print("2. Generating test data...")
    generate_test_data(analyzer, num_records=50)

    # Display statistics
    print("3. Displaying statistics...")
    analyzer.display_statistics(hours=24)

    # Display best opportunities
    print("\n4. Displaying best opportunities...")
    analyzer.display_best_opportunities(hours=24, limit=10)

    # Display alerts
    print("\n5. Checking alerts...")
    analyzer.display_alerts()

    # Save statistics
    print("\n6. Saving statistics to file...")
    analyzer.save_statistics()
    print(f"   ✅ Saved to {analyzer.stats_file}")

    # Verify data files
    print("\n7. Verifying data files...")
    print(f"   History file: {analyzer.history_file}")
    print(f"   File exists: {analyzer.history_file.exists()}")

    if analyzer.history_file.exists():
        line_count = sum(1 for line in open(analyzer.history_file) if line.strip())
        print(f"   Records in file: {line_count}")

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)

    # Quick usage example
    print("\n📝 Quick Usage Example:")
    print("="*80)
    print("""
# View statistics
python3 src/view_stats.py

# View all-time stats
python3 src/view_stats.py --hours 0

# Run enhanced monitor
python3 src/enhanced_monitor.py
    """)


if __name__ == "__main__":
    main()
