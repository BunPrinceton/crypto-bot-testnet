# Crypto Arbitrage Bot - Web Dashboard

## Quick Start for Demo

### Option 1: Using the Launch Script (Easiest)
```bash
./run_dashboard.sh
```

### Option 2: Manual Start
```bash
# Install Flask if needed
pip install Flask==3.0.0

# Run the dashboard
cd src
python3 dashboard.py
```

### Access the Dashboard
Once running, open your browser and visit:
```
http://localhost:5000
```

## What's Included

### Dashboard Features

#### 1. Real-Time Price Monitor
- Live prices from 3 major exchanges (Binance, Kraken, Coinbase)
- Displays Bid, Ask, and Last price for BTC/USDT
- Updates every 10 seconds automatically
- Color-coded for easy reading:
  - 🔴 Bid (red)
  - 🟢 Ask (green)
  - 🔵 Last (blue)

#### 2. Arbitrage Opportunity Detection
- Automatically scans for profitable arbitrage opportunities
- Shows buy/sell exchange pairs
- Calculates gross and net profit after fees
- Highlights best opportunities first
- Clear "no opportunities" message when market is efficient

#### 3. Statistics Dashboard
- Number of exchanges online
- Average, min, and max prices across exchanges
- Price spread percentage
- Total opportunities found

#### 4. Live Updates
- Background thread continuously fetches data
- Auto-refresh every 10 seconds
- Visual indicator when data updates
- Shows iteration count and last update time

### Technical Architecture

```
src/
├── dashboard.py          # Flask web server + background data fetcher
└── templates/
    └── dashboard.html    # Single-page dashboard UI
```

#### Key Components:

1. **Flask Web Server** (`dashboard.py`)
   - Serves the dashboard HTML
   - Provides `/api/data` endpoint for real-time data
   - Background thread updates data every 10 seconds
   - Thread-safe data access with locks

2. **Frontend** (`dashboard.html`)
   - Clean, modern UI with gradient background
   - Responsive grid layout
   - Auto-refreshing JavaScript
   - No external dependencies (no jQuery, no React)
   - Pure CSS animations

3. **Data Flow**
   ```
   Background Thread → Fetch Prices → Calculate Arbitrage
         ↓
   Global State (thread-safe)
         ↓
   API Endpoint → JSON Response
         ↓
   Frontend JS → Update DOM
   ```

## Configuration

Edit `src/dashboard.py` to customize:

```python
SYMBOL = 'BTC/USDT'        # Trading pair to monitor
FEE_PERCENT = 0.1          # Trading fee percentage
UPDATE_INTERVAL = 10       # Seconds between updates
```

Add/remove exchanges:
```python
exchanges = {
    'Binance': ccxt.binance(),
    'Kraken': ccxt.kraken(),
    'Coinbase': ccxt.coinbase(),
    # Add more exchanges here
}
```

## Demo Tips

### For Your 11 AM Presentation:

1. **Start Early**: Launch the dashboard 5-10 minutes before the demo to ensure it's collecting data

2. **Explain the UI**:
   - Top bar shows configuration and status
   - Left panel: live prices from multiple exchanges
   - Right panel: detected arbitrage opportunities
   - Bottom panel: market statistics

3. **Key Talking Points**:
   - "Real-time monitoring across 3 major exchanges"
   - "Automatically detects profitable arbitrage opportunities"
   - "Accounts for trading fees in profit calculations"
   - "Updates every 10 seconds without page refresh"
   - "Built with Python and Flask - minimal dependencies"

4. **Expected Behavior**:
   - Most of the time: NO opportunities (markets are efficient)
   - Occasionally: Small opportunities may appear briefly
   - This is realistic! Real arbitrage is rare

5. **Fallback**: If no opportunities appear:
   - Point out the price spread statistics
   - Explain why no opportunities is actually good (efficient markets)
   - Show the live updating prices as proof it's working

### Troubleshooting

**Dashboard won't start:**
```bash
# Install Flask
pip install Flask==3.0.0

# Or install all dependencies
pip install -r requirements.txt
```

**No data appearing:**
- Check your internet connection
- Exchanges may have rate limits - wait a minute and refresh
- Check the terminal for error messages

**Port 5000 already in use:**
Edit `src/dashboard.py`, change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

## Files Created

1. **`/src/dashboard.py`** - Main Flask application
2. **`/src/templates/dashboard.html`** - Dashboard UI
3. **`/run_dashboard.sh`** - Quick launch script
4. **`/DASHBOARD_README.md`** - This file
5. **Updated `/requirements.txt`** - Added Flask dependency

## Next Steps (After Demo)

Potential enhancements:
- Add historical price charts using Chart.js
- WebSocket for instant updates instead of polling
- Database to log opportunities and calculate hit rate
- Email/SMS alerts for profitable opportunities
- Support for multiple trading pairs
- Execution simulator to test strategies
- User authentication for multi-user access

## Architecture Decisions

**Why Flask over FastAPI?**
- Simpler for quick demos
- Fewer dependencies
- More familiar to general audience
- Built-in templating

**Why polling over WebSocket?**
- Simpler implementation
- More reliable for demo
- 10-second updates are sufficient
- Easy to understand

**Why no frontend framework?**
- Faster to build
- No build step required
- Easier to debug during demo
- Smaller bundle size

**Why threading over async?**
- ccxt library is sync by default
- Simpler mental model
- Adequate for this use case
- Thread-safe with locks

## Performance Notes

- Minimal CPU usage (sleeps between updates)
- Low memory footprint (~50-100 MB)
- Network calls are the bottleneck
- Can handle multiple concurrent viewers
- Background thread runs independently of web requests

---

**Good luck with your demo! 🚀**
