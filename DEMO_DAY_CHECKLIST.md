# Demo Day - WebSocket Monitor Checklist

## Pre-Demo Setup (Do This Before 11 AM)

### 1. Install Dependencies (2 minutes)
```bash
cd /mnt/c/Users/benja/Documents/projects/crypto-bot-testnet
./setup_websocket.sh
```

### 2. Test WebSocket Connections (30 seconds)
```bash
./venv/bin/python test_websocket.py
```
Expected: Should connect to Coinbase, possibly Kraken. Binance may be geo-blocked (OK).

### 3. Verify Data Logging
```bash
ls -lh data/prices_*.csv data/arbitrage_*.json
```
Expected: Should see CSV and JSON files created with timestamps.

## Demo Flow (10 minutes)

### Part 1: Show the Problem (2 minutes)
```bash
# Show the old polling monitor
cat src/price_monitor.py | head -30
```
Explain: "This polls every 10 seconds. Misses opportunities."

### Part 2: Show the Comparison (2 minutes)
```bash
python compare_monitors.py
```
Read through the output, emphasize real-time vs 10-second intervals.

### Part 3: Live Demo (4 minutes)
```bash
./venv/bin/python run_websocket_monitor.py
```
Point out:
- Real-time price updates
- Data freshness indicators (🟢 green = fresh data)
- Multiple exchanges updating independently
- CSV logging happening in background

Let it run for 1-2 minutes showing live updates.

Press Ctrl+C to stop gracefully.

### Part 4: Show the Data (2 minutes)
```bash
# Show CSV data
head -20 data/prices_*.csv | tail -15

# Count total records
wc -l data/prices_*.csv

# Show arbitrage JSON (if any opportunities detected)
cat data/arbitrage_*.json
```

Open CSV in Excel/viewer to show proper formatting.

## Demo Talking Points

### Why WebSocket vs Polling?
- "Arbitrage opportunities last < 1 second in real markets"
- "10-second polling means we miss 90% of opportunities"
- "WebSocket = instant updates, no API rate limits"

### What Makes This Production-Ready?
- "Real-time data is critical for trading"
- "Automatic logging for backtesting and analysis"
- "Error handling and graceful degradation"
- "Concurrent connections using async/await"

### Data Logging Benefits
- "CSV files can be imported into Excel/pandas"
- "JSON logs track every arbitrage opportunity"
- "Timestamped files for historical analysis"
- "Can backtest strategies using logged data"

### Next Steps
- "Add order execution when arbitrage detected"
- "Connect to database for long-term storage"
- "Add web dashboard for monitoring"
- "Implement alerts via Telegram/Discord"

## Quick Commands Reference

### Start monitor:
```bash
./venv/bin/python run_websocket_monitor.py
```

### Stop monitor:
```
Ctrl+C
```

### View latest data:
```bash
tail -20 data/prices_*.csv
```

### Count price updates:
```bash
wc -l data/prices_*.csv
```

### Check for arbitrage:
```bash
cat data/arbitrage_*.json
```

## Troubleshooting

### "No module named websockets"
```bash
./venv/bin/pip install websockets aiohttp
```

### "Binance WebSocket unavailable (geo-restricted)"
Normal! Binance blocks some regions. Monitor works with Coinbase/Kraken.

### "No data from Kraken"
Kraken can be slow. Wait 10-20 seconds. If still nothing, continue with Coinbase.

### Excel won't open CSV
CSV files are valid. Try:
- Right-click → Open with → Excel
- Import data instead of double-clicking
- Use Google Sheets

## Files to Have Open During Demo

1. Terminal: Running the WebSocket monitor
2. File explorer: data/ folder showing CSV/JSON files
3. Text editor: compare_monitors.py output
4. Browser: WEBSOCKET_DEMO.md for reference

## Backup Plan

If WebSocket demo fails:
1. Show the comparison script output
2. Show existing CSV files with data
3. Explain architecture using WEBSOCKET_SUMMARY.md
4. Show the code in websocket_monitor.py

## Time Allocation

- 00:00 - 02:00: Explain the problem (polling)
- 02:00 - 04:00: Show comparison script
- 04:00 - 08:00: Live WebSocket demo
- 08:00 - 10:00: Show logged data

Total: 10 minutes with buffer

## Success Criteria

- ✅ Monitor connects to at least one exchange
- ✅ Prices update in real-time
- ✅ CSV files are created and contain data
- ✅ Demonstrate graceful shutdown (Ctrl+C)
- ✅ Explain why WebSocket is better than polling

## Post-Demo

Show the implementation:
```bash
wc -l src/websocket_monitor.py
cat WEBSOCKET_SUMMARY.md
```

"Only 300 lines of code for a production-ready real-time monitor with data logging!"
