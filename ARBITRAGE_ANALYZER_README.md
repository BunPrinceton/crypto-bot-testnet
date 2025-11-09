# Enhanced Arbitrage Analyzer

## Overview

Enhanced arbitrage detection system with historical tracking, statistics, and alerting capabilities.

## New Files Created

### 1. `src/arbitrage_analyzer.py` (Core Engine)
- **ArbitrageAnalyzer** class - Main analytics engine
- Tracks all arbitrage opportunities to disk (JSONL format)
- Calculates comprehensive statistics
- Generates alerts for high-value opportunities
- Provides historical analysis capabilities

### 2. `src/enhanced_monitor.py` (Integrated Monitor)
- Enhanced version of `price_monitor.py`
- Multi-symbol support (BTC/USDT, ETH/USDT)
- Real-time opportunity tracking
- Displays statistics every 5 iterations
- Shows final statistics on shutdown

### 3. `src/view_stats.py` (Statistics Viewer)
- Standalone statistics viewer
- View historical data without running the monitor
- Configurable time windows
- Command-line interface

## Key Features

### Historical Tracking
- All opportunities saved to `data/arbitrage_history.jsonl`
- JSONL format (one JSON object per line) for easy streaming
- Timestamped records with full opportunity details

### Statistics Calculated
- **Overall Stats**: Total opportunities, time ranges
- **Profit Statistics**: Min, max, mean, median, standard deviation
- **Per-Symbol Breakdown**: Count, average profit, frequency
- **Top Exchange Pairs**: Best performing exchange routes
- **High-Value Count**: Opportunities above alert threshold

### Alert System
- Configurable profit threshold (default: 0.5% for viewer, 0.2% for monitor)
- Real-time alerts during monitoring
- Alert history tracking

### Multi-Symbol Support
- Monitor multiple cryptocurrencies simultaneously
- Per-symbol statistics and analysis
- Symbol-specific opportunity tracking

## Usage

### Running the Enhanced Monitor

```bash
cd /mnt/c/Users/benja/Documents/projects/crypto-bot-testnet
python3 src/enhanced_monitor.py
```

Features:
- Monitors BTC/USDT and ETH/USDT
- Shows prices and opportunities for each symbol
- Displays high-value alerts as they occur
- Shows quick stats every 5 iterations
- On exit (Ctrl+C), displays full statistics

### Viewing Statistics

```bash
# View last 24 hours (default)
python3 src/view_stats.py

# View all-time statistics
python3 src/view_stats.py --hours 0

# View last 12 hours, top 5 opportunities
python3 src/view_stats.py --hours 12 --top 5

# Custom data directory
python3 src/view_stats.py --data-dir /path/to/data
```

### Running the Demo

```bash
# Test the analyzer with simulated data
python3 src/arbitrage_analyzer.py
```

## Data Storage

### Files Created
- `data/arbitrage_history.jsonl` - Line-delimited JSON log of all opportunities
- `data/arbitrage_stats.json` - Latest statistics snapshot (saved on shutdown)

### Data Format (JSONL)
```json
{
  "timestamp": "2025-11-09T02:42:56.338580",
  "symbol": "BTC/USDT",
  "buy_from": "Binance",
  "sell_to": "Kraken",
  "buy_price": 43250.5,
  "sell_price": 43320.75,
  "gross_profit_pct": 0.162,
  "net_profit_pct": 0.062
}
```

## Integration with Existing Code

### The analyzer integrates seamlessly:
1. Import: `from arbitrage_analyzer import ArbitrageAnalyzer`
2. Initialize: `analyzer = ArbitrageAnalyzer(alert_threshold=0.3)`
3. Record: `analyzer.record_opportunity(symbol, opportunity_dict)`
4. View stats: `analyzer.display_statistics(hours=24)`

### Example Integration
```python
from arbitrage_analyzer import ArbitrageAnalyzer

# Initialize
analyzer = ArbitrageAnalyzer(alert_threshold=0.2)

# In your monitoring loop
for opportunity in opportunities:
    analyzer.record_opportunity('BTC/USDT', opportunity)

# Check for alerts
if analyzer.get_alerts():
    analyzer.display_alerts()
    analyzer.clear_alerts()

# View statistics
analyzer.display_statistics(hours=24)
```

## Sample Output

### Statistics Display
```
================================================================================
📊 ARBITRAGE STATISTICS - Last 24 Hours
================================================================================

Total Opportunities: 45
High-Value Opportunities (≥0.5%): 3
Time Range: 2025-11-09T01:00:00 to 2025-11-09T02:42:56

📈 Net Profit Statistics:
  Average:  0.1257%
  Median:   0.0620%
  Min:      -0.1650%
  Max:      0.4800%
  Std Dev:  0.3272%

💰 By Symbol:
  ETH/USDT:
    Count: 15 (33.3%)
    Avg Profit: 0.4800%
    Max Profit: 0.4800%
  BTC/USDT:
    Count: 30 (66.7%)
    Avg Profit: -0.0515%
    Max Profit: 0.0620%

🏆 Top Exchange Pairs:
  1. Coinbase → Binance
     Count: 12, Avg: 0.4800%, Max: 0.4800%
  2. Binance → Kraken
     Count: 18, Avg: 0.0620%, Max: 0.0620%
```

### Best Opportunities Display
```
================================================================================
🌟 TOP 5 ARBITRAGE OPPORTUNITIES - Last 24 Hours
================================================================================

#1 - 2025-11-09T02:42:56.441027
  Symbol: ETH/USDT
  Route: Coinbase → Binance
  Buy Price:  $2280.30
  Sell Price: $2295.80
  Net Profit: 0.4800% 🎯
```

### Alert Display
```
================================================================================
🚨 HIGH-VALUE ALERTS (3 total)
================================================================================

🚨 HIGH PROFIT ALERT: 0.680% on ETH/USDT
  Time: 2025-11-09T02:42:56.441027
  Route: Coinbase → Binance
  Profit: 0.6800%
```

## Configuration Options

### ArbitrageAnalyzer Parameters
- `data_dir`: Directory for storing data (default: "data")
- `alert_threshold`: Net profit % to trigger alerts (default: 0.5)

### Analyzer Methods
- `record_opportunity(symbol, opportunity)` - Record an opportunity
- `load_history(hours=None)` - Load historical records
- `get_statistics(hours=24, by_symbol=True)` - Get statistics
- `get_best_opportunities(hours=24, limit=10)` - Get top opportunities
- `display_statistics(hours=24)` - Display formatted statistics
- `display_best_opportunities(hours=24, limit=5)` - Display top opportunities
- `get_alerts()` - Get current session alerts
- `clear_alerts()` - Clear alerts
- `save_statistics()` - Save stats to JSON file

## Demo Ready Features

For your 11 AM demo:

1. **Live Monitoring**: Run `enhanced_monitor.py` to show real-time tracking
2. **Historical Analysis**: Use `view_stats.py` to show accumulated data
3. **Multi-Symbol**: Demonstrates monitoring multiple cryptocurrencies
4. **Alert System**: Shows high-value opportunities as they occur
5. **Statistics**: Comprehensive analytics on demand

## Tips for Demo

1. Run the enhanced monitor for a few minutes before the demo to collect data
2. Keep it running in one terminal
3. Open another terminal to run `view_stats.py` and show historical analysis
4. Point out the data files being created in real-time
5. Show how statistics evolve as more data is collected

## Dependencies

All required dependencies are already in `requirements.txt`:
- ccxt (crypto exchange API)
- Standard library only for the analyzer (json, statistics, pathlib)

No additional installations needed!
