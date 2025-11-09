#!/usr/bin/env python3
"""
Enhanced Arbitrage Analyzer with Historical Tracking and Statistics
Tracks arbitrage opportunities over time and provides detailed analytics
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class ArbitrageAnalyzer:
    """
    Enhanced arbitrage analyzer with historical tracking and statistics
    """

    def __init__(self, data_dir: str = "data", alert_threshold: float = 0.5):
        """
        Initialize the analyzer

        Args:
            data_dir: Directory to store historical data
            alert_threshold: Net profit threshold (%) to trigger alerts
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.alert_threshold = alert_threshold
        self.history_file = self.data_dir / "arbitrage_history.jsonl"
        self.stats_file = self.data_dir / "arbitrage_stats.json"

        # In-memory storage for current session
        self.opportunities = []
        self.alerts = []

    def record_opportunity(self, symbol: str, opportunity: Dict, timestamp: Optional[datetime] = None) -> None:
        """
        Record an arbitrage opportunity

        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
            opportunity: Opportunity dict with buy/sell details
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        record = {
            'timestamp': timestamp.isoformat(),
            'symbol': symbol,
            'buy_from': opportunity['buy_from'],
            'sell_to': opportunity['sell_to'],
            'buy_price': opportunity['buy_price'],
            'sell_price': opportunity['sell_price'],
            'gross_profit_pct': opportunity['gross_profit_pct'],
            'net_profit_pct': opportunity['net_profit_pct']
        }

        # Add to in-memory storage
        self.opportunities.append(record)

        # Append to file
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(record) + '\n')

        # Check for alert
        if record['net_profit_pct'] >= self.alert_threshold:
            self._create_alert(record)

    def _create_alert(self, record: Dict) -> None:
        """Create an alert for a high-value opportunity"""
        alert = {
            'timestamp': record['timestamp'],
            'message': f"🚨 HIGH PROFIT ALERT: {record['net_profit_pct']:.3f}% on {record['symbol']}",
            'details': record
        }
        self.alerts.append(alert)

    def load_history(self, hours: Optional[int] = None) -> List[Dict]:
        """
        Load historical opportunities from file

        Args:
            hours: Only load records from the last N hours (None = all records)

        Returns:
            List of opportunity records
        """
        if not self.history_file.exists():
            return []

        records = []
        cutoff_time = None

        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)

        with open(self.history_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    record_time = datetime.fromisoformat(record['timestamp'])

                    if cutoff_time is None or record_time >= cutoff_time:
                        records.append(record)

        return records

    def get_statistics(self, hours: Optional[int] = 24, by_symbol: bool = True) -> Dict:
        """
        Calculate statistics from historical data

        Args:
            hours: Time window for statistics (None = all time)
            by_symbol: Include per-symbol breakdown

        Returns:
            Dictionary with comprehensive statistics
        """
        records = self.load_history(hours)

        if not records:
            return {
                'total_opportunities': 0,
                'time_window_hours': hours,
                'message': 'No historical data available'
            }

        # Overall statistics
        net_profits = [r['net_profit_pct'] for r in records]
        gross_profits = [r['gross_profit_pct'] for r in records]

        stats = {
            'total_opportunities': len(records),
            'time_window_hours': hours or 'all',
            'first_seen': records[0]['timestamp'],
            'last_seen': records[-1]['timestamp'],
            'net_profit': {
                'min': min(net_profits),
                'max': max(net_profits),
                'mean': statistics.mean(net_profits),
                'median': statistics.median(net_profits),
                'stdev': statistics.stdev(net_profits) if len(net_profits) > 1 else 0
            },
            'gross_profit': {
                'min': min(gross_profits),
                'max': max(gross_profits),
                'mean': statistics.mean(gross_profits),
                'median': statistics.median(gross_profits)
            },
            'high_value_count': len([r for r in records if r['net_profit_pct'] >= self.alert_threshold])
        }

        # Per-symbol statistics
        if by_symbol:
            symbol_stats = defaultdict(lambda: {'count': 0, 'profits': []})

            for record in records:
                symbol = record['symbol']
                symbol_stats[symbol]['count'] += 1
                symbol_stats[symbol]['profits'].append(record['net_profit_pct'])

            stats['by_symbol'] = {}
            for symbol, data in symbol_stats.items():
                stats['by_symbol'][symbol] = {
                    'count': data['count'],
                    'avg_profit': statistics.mean(data['profits']),
                    'max_profit': max(data['profits']),
                    'frequency_pct': (data['count'] / len(records)) * 100
                }

        # Exchange pair statistics
        pair_stats = defaultdict(lambda: {'count': 0, 'profits': []})

        for record in records:
            pair = f"{record['buy_from']} → {record['sell_to']}"
            pair_stats[pair]['count'] += 1
            pair_stats[pair]['profits'].append(record['net_profit_pct'])

        # Find best exchange pairs
        best_pairs = sorted(
            pair_stats.items(),
            key=lambda x: statistics.mean(x[1]['profits']),
            reverse=True
        )[:5]

        stats['top_exchange_pairs'] = {
            pair: {
                'count': data['count'],
                'avg_profit': statistics.mean(data['profits']),
                'max_profit': max(data['profits'])
            }
            for pair, data in best_pairs
        }

        return stats

    def get_best_opportunities(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """
        Get the best arbitrage opportunities from history

        Args:
            hours: Time window to search
            limit: Maximum number of opportunities to return

        Returns:
            List of top opportunities sorted by net profit
        """
        records = self.load_history(hours)

        # Sort by net profit descending
        sorted_records = sorted(
            records,
            key=lambda x: x['net_profit_pct'],
            reverse=True
        )

        return sorted_records[:limit]

    def get_alerts(self) -> List[Dict]:
        """Get all alerts from current session"""
        return self.alerts

    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self.alerts = []

    def save_statistics(self) -> None:
        """Save current statistics to file"""
        stats = self.get_statistics(hours=None, by_symbol=True)

        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

    def display_statistics(self, hours: int = 24) -> None:
        """
        Display formatted statistics

        Args:
            hours: Time window for statistics
        """
        stats = self.get_statistics(hours)

        print("\n" + "="*80)
        print(f"📊 ARBITRAGE STATISTICS - Last {hours} Hours")
        print("="*80)

        if stats['total_opportunities'] == 0:
            print("\nNo opportunities found in this time window.")
            return

        print(f"\nTotal Opportunities: {stats['total_opportunities']}")
        print(f"High-Value Opportunities (≥{self.alert_threshold}%): {stats['high_value_count']}")
        print(f"Time Range: {stats['first_seen']} to {stats['last_seen']}")

        print("\n📈 Net Profit Statistics:")
        print(f"  Average:  {stats['net_profit']['mean']:.4f}%")
        print(f"  Median:   {stats['net_profit']['median']:.4f}%")
        print(f"  Min:      {stats['net_profit']['min']:.4f}%")
        print(f"  Max:      {stats['net_profit']['max']:.4f}%")
        print(f"  Std Dev:  {stats['net_profit']['stdev']:.4f}%")

        # Symbol breakdown
        if 'by_symbol' in stats and stats['by_symbol']:
            print("\n💰 By Symbol:")
            for symbol, data in sorted(
                stats['by_symbol'].items(),
                key=lambda x: x[1]['avg_profit'],
                reverse=True
            ):
                print(f"  {symbol}:")
                print(f"    Count: {data['count']} ({data['frequency_pct']:.1f}%)")
                print(f"    Avg Profit: {data['avg_profit']:.4f}%")
                print(f"    Max Profit: {data['max_profit']:.4f}%")

        # Best exchange pairs
        if 'top_exchange_pairs' in stats and stats['top_exchange_pairs']:
            print("\n🏆 Top Exchange Pairs:")
            for i, (pair, data) in enumerate(stats['top_exchange_pairs'].items(), 1):
                print(f"  {i}. {pair}")
                print(f"     Count: {data['count']}, Avg: {data['avg_profit']:.4f}%, Max: {data['max_profit']:.4f}%")

    def display_best_opportunities(self, hours: int = 24, limit: int = 5) -> None:
        """
        Display the best opportunities from history

        Args:
            hours: Time window to search
            limit: Number of opportunities to show
        """
        opportunities = self.get_best_opportunities(hours, limit)

        print("\n" + "="*80)
        print(f"🌟 TOP {limit} ARBITRAGE OPPORTUNITIES - Last {hours} Hours")
        print("="*80)

        if not opportunities:
            print("\nNo opportunities found in this time window.")
            return

        for i, opp in enumerate(opportunities, 1):
            print(f"\n#{i} - {opp['timestamp']}")
            print(f"  Symbol: {opp['symbol']}")
            print(f"  Route: {opp['buy_from']} → {opp['sell_to']}")
            print(f"  Buy Price:  ${opp['buy_price']:.2f}")
            print(f"  Sell Price: ${opp['sell_price']:.2f}")
            print(f"  Net Profit: {opp['net_profit_pct']:.4f}% 🎯")

    def display_alerts(self) -> None:
        """Display all alerts from current session"""
        if not self.alerts:
            print("\n✅ No high-value alerts in this session")
            return

        print("\n" + "="*80)
        print(f"🚨 HIGH-VALUE ALERTS ({len(self.alerts)} total)")
        print("="*80)

        for alert in self.alerts:
            print(f"\n{alert['message']}")
            details = alert['details']
            print(f"  Time: {details['timestamp']}")
            print(f"  Route: {details['buy_from']} → {details['sell_to']}")
            print(f"  Profit: {details['net_profit_pct']:.4f}%")


def demo_analyzer():
    """Demo function to show analyzer capabilities"""
    print("🤖 Arbitrage Analyzer Demo\n")

    # Initialize analyzer
    analyzer = ArbitrageAnalyzer(alert_threshold=0.3)

    # Simulate some opportunities
    print("📝 Simulating opportunities...")

    test_opportunities = [
        {
            'symbol': 'BTC/USDT',
            'buy_from': 'Binance',
            'sell_to': 'Kraken',
            'buy_price': 43250.50,
            'sell_price': 43320.75,
            'gross_profit_pct': 0.162,
            'net_profit_pct': 0.062
        },
        {
            'symbol': 'ETH/USDT',
            'buy_from': 'Coinbase',
            'sell_to': 'Binance',
            'buy_price': 2280.30,
            'sell_price': 2295.80,
            'gross_profit_pct': 0.680,
            'net_profit_pct': 0.480
        },
        {
            'symbol': 'BTC/USDT',
            'buy_from': 'Kraken',
            'sell_to': 'Coinbase',
            'buy_price': 43240.00,
            'sell_price': 43255.00,
            'gross_profit_pct': 0.035,
            'net_profit_pct': -0.165
        }
    ]

    for opp in test_opportunities:
        symbol = opp.pop('symbol')
        analyzer.record_opportunity(symbol, opp)
        time.sleep(0.1)

    # Display results
    analyzer.display_statistics(hours=24)
    analyzer.display_best_opportunities(hours=24, limit=3)
    analyzer.display_alerts()

    print("\n" + "="*80)
    print("✅ Demo complete!")


if __name__ == "__main__":
    demo_analyzer()
