# WebSocket Price Monitor - Demo Guide

## Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Run the WebSocket Monitor
```bash
python run_websocket_monitor.py
```

Or use the Python executable directly:
```bash
./venv/bin/python run_websocket_monitor.py
```

### 3. Stop the Monitor
Press `Ctrl+C` to stop gracefully.

## What It Does

The WebSocket monitor provides **real-time** cryptocurrency price tracking:

- Connects to multiple exchange WebSocket APIs simultaneously
- Displays live bid/ask/last prices updated in real-time (not polling!)
- Calculates arbitrage opportunities as prices change
- Logs all price data to CSV files for analysis
- Logs arbitrage opportunities to JSON files

## Data Logging

All data is saved to the `data/` folder:

### CSV Price Logs
- Filename: `data/prices_YYYYMMDD_HHMMSS.csv`
- Contains: timestamp, exchange, bid, ask, last, volume
- Updated in real-time as prices come in
- Perfect for Excel/pandas analysis

### JSON Arbitrage Logs
- Filename: `data/arbitrage_YYYYMMDD_HHMMSS.json`
- Contains: All detected arbitrage opportunities with timestamps
- Includes buy/sell exchanges, prices, profit percentages

## Supported Exchanges

- **Binance**: May be geo-restricted in some regions
- **Kraken**: BTC/USDT pair
- **Coinbase**: BTC-USD pair (converted to USDT equivalent)

## Key Features vs. Polling Monitor

| Feature | WebSocket Monitor | Old Polling Monitor |
|---------|------------------|-------------------|
| Update frequency | Real-time (ms) | Every 10 seconds |
| Data freshness | Instant | Stale by up to 10s |
| API efficiency | 1 connection | Repeated requests |
| Rate limits | No issues | Can hit limits |
| Data logging | Yes (CSV/JSON) | No |
| Arbitrage detection | Real-time | Delayed |

## Troubleshooting

### "Connection error" for Binance
- Binance blocks certain regions (HTTP 451)
- Monitor will continue with other exchanges
- This is normal and expected

### No data from Kraken
- Kraken WebSocket can be slow to send initial data
- Wait 10-20 seconds for first update
- If still no data, check internet connection

### Virtual environment not found
```bash
python3 -m venv venv
./venv/bin/pip install websockets aiohttp
```

## Demo Talking Points

1. **Real-time updates**: Show how prices update instantly, not every 10 seconds
2. **Data logging**: Open CSV file in Excel to show price history
3. **Multi-exchange**: Demonstrates handling multiple WebSocket connections concurrently
4. **Arbitrage detection**: Show live calculation when price spreads appear
5. **Production-ready**: Includes error handling, reconnection logic, data persistence

## Next Steps for Production

- Add authentication for private endpoints
- Implement order execution when arbitrage detected
- Add database storage (PostgreSQL/MongoDB)
- Create web dashboard for monitoring
- Add Telegram/email alerts
- Implement proper position sizing and risk management
