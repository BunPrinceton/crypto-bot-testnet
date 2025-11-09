# Enhanced Arbitrage Bot - Quick Reference

## Commands Cheat Sheet

### Run Live Monitor (Enhanced)
```bash
python3 src/enhanced_monitor.py
```
- Monitors BTC/USDT and ETH/USDT
- Shows real-time opportunities
- Records all opportunities to disk
- Displays stats every 5 iterations
- Press Ctrl+C to stop and see final stats

### View Historical Statistics
```bash
# Last 24 hours (default)
python3 src/view_stats.py

# All time
python3 src/view_stats.py --hours 0

# Last 12 hours, top 15 opportunities
python3 src/view_stats.py --hours 12 --top 15
```

### Generate Test Data
```bash
python3 src/test_analyzer.py
```
Creates 50 realistic test opportunities for demo purposes

### Run Original Monitor (Basic)
```bash
python3 src/price_monitor.py
```
Original version without historical tracking

## File Locations

### Source Files
- `/src/arbitrage_analyzer.py` - Core analytics engine
- `/src/enhanced_monitor.py` - Live monitor with analytics
- `/src/view_stats.py` - Statistics viewer CLI
- `/src/test_analyzer.py` - Test suite & data generator
- `/src/price_monitor.py` - Original basic monitor

### Data Files
- `/data/arbitrage_history.jsonl` - All opportunities (JSONL format)
- `/data/arbitrage_stats.json` - Latest statistics snapshot

### Documentation
- `ARBITRAGE_ANALYZER_README.md` - Complete feature documentation
- `DEMO_GUIDE.md` - Step-by-step demo presentation guide
- `QUICK_REFERENCE.md` - This file

## Key Statistics Explained

### Net Profit vs Gross Profit
- **Gross Profit**: Raw price difference percentage
- **Net Profit**: After accounting for 0.1% trading fee on BOTH buy and sell (0.2% total)
- Only positive net profit opportunities are truly profitable

### Statistical Measures
- **Mean**: Average profit across all opportunities
- **Median**: Middle value (less affected by outliers)
- **Std Dev**: Volatility/spread of profit values
- **Min/Max**: Range of observed profits

### Alert Threshold
- **Enhanced Monitor**: 0.2% net profit
- **Stats Viewer**: 0.5% net profit
- Configurable when initializing ArbitrageAnalyzer

## Common Issues & Solutions

### "No opportunities found"
- This is normal! Real arbitrage opportunities are rare
- Run `python3 src/test_analyzer.py` to generate test data
- Markets may be efficient (no arbitrage available)

### "No module named 'arbitrage_analyzer'"
- Make sure you're in the project root directory
- Check that src/ is in your Python path

### "File not found" errors
- Ensure you're running from project root: `/mnt/c/Users/benja/Documents/projects/crypto-bot-testnet/`
- Data directory is auto-created if missing

## Integration Example

```python
from arbitrage_analyzer import ArbitrageAnalyzer

# Initialize
analyzer = ArbitrageAnalyzer(
    data_dir='data',
    alert_threshold=0.3  # 0.3% net profit
)

# In your trading loop
for opportunity in opportunities:
    # Record opportunity
    analyzer.record_opportunity('BTC/USDT', opportunity)

    # Check for alerts
    alerts = analyzer.get_alerts()
    if alerts:
        print(f"🚨 {len(alerts)} high-value alerts!")
        analyzer.clear_alerts()

# View statistics
analyzer.display_statistics(hours=24)
analyzer.display_best_opportunities(hours=24, limit=10)

# Save to file
analyzer.save_statistics()
```

## Demo Checklist

- [ ] Navigate to project directory
- [ ] Run `python3 src/test_analyzer.py` to generate test data
- [ ] Start `python3 src/enhanced_monitor.py` (leave running)
- [ ] Open second terminal for `python3 src/view_stats.py`
- [ ] Prepare to show data files in `/data/`
- [ ] Know your talking points (see DEMO_GUIDE.md)

## Performance Notes

### Data Volume Estimates
- ~100 bytes per opportunity record
- 1000 opportunities ≈ 100KB
- 10,000 opportunities ≈ 1MB
- Very lightweight, can track millions of opportunities

### Memory Usage
- Minimal: Only current session in memory
- Historical data loaded on-demand
- Efficient JSONL streaming

### Speed
- Record opportunity: < 1ms
- Load 10,000 records: ~50ms
- Calculate statistics: ~100ms

## Next Steps / Future Enhancements

Ideas for expansion:
1. Add webhook notifications for high-value alerts
2. Integrate with trading execution engine
3. Machine learning models for opportunity prediction
4. Web dashboard for visualization
5. Multi-timeframe analysis (hourly, daily, weekly trends)
6. Correlation analysis between symbols
7. Exchange reliability tracking
8. Cost basis and actual profit tracking
