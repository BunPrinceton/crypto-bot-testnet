#!/usr/bin/env python3
"""
Arbitrage Statistics Viewer
View historical arbitrage data and statistics without running the monitor
"""

import argparse
from arbitrage_analyzer import ArbitrageAnalyzer


def main():
    """Main function to view statistics"""
    parser = argparse.ArgumentParser(
        description='View arbitrage statistics from historical data'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Time window in hours (default: 24, use 0 for all time)'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top opportunities to show (default: 10)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Data directory (default: data)'
    )

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = ArbitrageAnalyzer(data_dir=args.data_dir)

    # Display statistics
    hours = None if args.hours == 0 else args.hours
    time_desc = "All Time" if hours is None else f"Last {hours} Hours"

    print("="*80)
    print(f"📊 ARBITRAGE ANALYTICS - {time_desc}")
    print("="*80)

    analyzer.display_statistics(hours=hours if hours else 24)
    analyzer.display_best_opportunities(hours=hours if hours else 24, limit=args.top)

    print("\n" + "="*80)
    print("✅ Analysis complete!")


if __name__ == "__main__":
    main()
