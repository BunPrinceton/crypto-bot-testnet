# Demo Guide - 11 AM Presentation

## Quick Setup (5 minutes before demo)

### 1. Pre-populate with test data
```bash
cd /mnt/c/Users/benja/Documents/projects/crypto-bot-testnet
python3 src/test_analyzer.py
```

This creates realistic test data to show during the demo.

### 2. Start the enhanced monitor
```bash
python3 src/enhanced_monitor.py
```

Let it run for 2-3 minutes to collect some live data.

## Demo Flow (Recommended Order)

### Part 1: Show Live Monitoring (2-3 minutes)
Keep `enhanced_monitor.py` running in the terminal and show:

1. **Multi-symbol tracking**: "We're monitoring BTC and ETH simultaneously"
2. **Real-time prices**: Point out the price table for each symbol
3. **Opportunity detection**: Show arbitrage opportunities as they appear
4. **Alert system**: If any high-value alerts appear (>0.2%), highlight them
5. **Periodic stats**: Wait for iteration 5 to show the quick stats summary

### Part 2: Historical Analysis (2 minutes)
Open a second terminal window:

```bash
# Show last 24 hours statistics
python3 src/view_stats.py

# Show all-time statistics
python3 src/view_stats.py --hours 0

# Show top 15 opportunities
python3 src/view_stats.py --hours 0 --top 15
```

Point out:
- Total opportunities tracked
- Statistical analysis (mean, median, std dev)
- Per-symbol breakdown
- Top exchange pairs for arbitrage

### Part 3: Data Persistence (1 minute)
Show the data files:

```bash
# Show the data directory
ls -lh data/

# Show sample of historical data
head -5 data/arbitrage_history.jsonl

# Show formatted stats file
cat data/arbitrage_stats.json
```

Explain:
- JSONL format for efficient streaming
- One record per opportunity
- Timestamped for historical analysis

### Part 4: Exit Demo (1 minute)
Stop the enhanced monitor (Ctrl+C) and show:
- Final statistics summary
- Total opportunities found in session
- Best opportunities
- Where data was saved

## Key Talking Points

### Problem We're Solving
"Traditional arbitrage bots only track current opportunities. We're adding intelligence with historical analysis to identify the BEST opportunities and exchange pairs over time."

### Key Features to Highlight
1. **Multi-symbol support**: Track multiple cryptocurrencies simultaneously
2. **Historical tracking**: Every opportunity is saved for later analysis
3. **Statistical analysis**: Mean, median, std dev, per-symbol breakdown
4. **Alert system**: Get notified of high-value opportunities
5. **Persistence**: All data saved to disk for long-term analysis
6. **Exchange pair analysis**: Identify which exchange pairs are most profitable

### Technical Highlights
1. **Efficient data format**: JSONL for streaming and processing
2. **Modular design**: `ArbitrageAnalyzer` can be integrated into any trading system
3. **No external dependencies**: Uses only standard library (except ccxt for price data)
4. **Demo-ready**: Test data generator for presentations

## Backup Commands (If Something Goes Wrong)

### If monitor fails:
```bash
# Run the simple version
python3 src/price_monitor.py
```

### If no data yet:
```bash
# Generate test data again
python3 src/test_analyzer.py
```

### If stats viewer fails:
```bash
# Run the demo directly
python3 src/arbitrage_analyzer.py
```

## File Summary for Demo

### Created Files
1. `src/arbitrage_analyzer.py` - Core analytics engine (300+ lines)
2. `src/enhanced_monitor.py` - Integrated live monitor (200+ lines)
3. `src/view_stats.py` - Statistics viewer CLI (50+ lines)
4. `src/test_analyzer.py` - Test suite and data generator (100+ lines)

### Data Files (auto-generated)
1. `data/arbitrage_history.jsonl` - All opportunities, one per line
2. `data/arbitrage_stats.json` - Latest statistics snapshot

## Demo Script Example

"Let me show you our enhanced arbitrage detection system.

[Show enhanced_monitor.py running]
As you can see, we're monitoring Bitcoin and Ethereum across three exchanges - Binance, Kraken, and Coinbase. The system fetches real-time prices every 10 seconds.

[Point to opportunity display]
When it finds a profitable arbitrage opportunity - even after accounting for trading fees - it records it. You'll see we're tracking both gross profit and net profit after fees.

[Open second terminal]
Now, here's where it gets interesting. Every opportunity is saved to disk, so we can analyze historical patterns.

[Run view_stats.py]
Look at this - we've tracked 53 opportunities in the last 24 hours. The average net profit is 0.2%, but we've seen opportunities as high as 0.58%.

[Show per-symbol breakdown]
The system breaks down performance by cryptocurrency. ETH has been showing better arbitrage opportunities than BTC, averaging 0.26% profit.

[Show top exchange pairs]
And here's the real insight - we can see which exchange pairs are most profitable. KuCoin to Binance has been our best route, averaging almost 0.4% profit.

[Stop the monitor with Ctrl+C]
When we stop the monitor, it automatically saves a full statistics report and shows us the session summary.

[Show data files]
All of this is persisted to disk in an efficient JSONL format, so we can do long-term analysis and machine learning in the future.

The key innovation here is turning a simple 'current state' monitor into a learning system that gets smarter over time by analyzing historical patterns."

## Questions You Might Get

**Q: How does this improve on the basic version?**
A: Basic version only shows current opportunities. Our version tracks everything, calculates statistics, identifies patterns, and alerts you to the BEST opportunities based on historical data.

**Q: Can this scale to more exchanges/symbols?**
A: Absolutely. The analyzer is symbol-agnostic. Just add more symbols to the list and it automatically tracks them separately with per-symbol statistics.

**Q: What about the alert threshold?**
A: Configurable! Default is 0.5% for the stats viewer, 0.2% for the live monitor. Adjust based on your risk tolerance and trading strategy.

**Q: Is the data persistent across restarts?**
A: Yes! JSONL format means you can stop and restart anytime. All historical data is preserved and loaded automatically.

**Q: Can we use this data for machine learning?**
A: That's the plan! The JSONL format is perfect for ML pipelines. We're building the data foundation now for predictive models later.

## Time Allocation (10-minute demo)

- 0:00-0:30 - Introduction and problem statement
- 0:30-3:00 - Show live monitoring (Part 1)
- 3:00-5:00 - Historical analysis (Part 2)
- 5:00-6:00 - Data persistence (Part 3)
- 6:00-7:00 - Exit and summary (Part 4)
- 7:00-10:00 - Q&A

Good luck with your demo!
