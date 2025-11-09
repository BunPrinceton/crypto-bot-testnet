# Quick Start - Dashboard for 11 AM Demo

## Start the Dashboard (Choose One)

### Option 1: Quick Launch
```bash
./run_dashboard.sh
```

### Option 2: Direct Python
```bash
cd src
python3 dashboard.py
```

### Option 3: If Flask Not Installed
```bash
pip install Flask==3.0.0
cd src
python3 dashboard.py
```

## Access the Dashboard

Open your browser and go to:
```
http://localhost:5000
```

## You Should See

✅ Blue gradient background
✅ "Crypto Arbitrage Bot" header
✅ Live prices from 3 exchanges
✅ Arbitrage opportunities section
✅ Statistics table
✅ Auto-updating every 10 seconds

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'flask'`
**Solution**: `pip install Flask==3.0.0`

**Problem**: `ModuleNotFoundError: No module named 'ccxt'`
**Solution**: `pip install -r requirements.txt`

**Problem**: Port 5000 in use
**Solution**: Edit `src/dashboard.py` line 183, change port to 5001

**Problem**: No data showing
**Solution**: Wait 10-15 seconds for first update, check internet connection

## Stop the Dashboard

Press `Ctrl+C` in the terminal

## Files Created

1. `/src/dashboard.py` - Main web server
2. `/src/templates/dashboard.html` - UI
3. `/run_dashboard.sh` - Launch script
4. `/DASHBOARD_README.md` - Full documentation
5. `/DASHBOARD_PREVIEW.md` - Visual guide

## Demo Tips

- Start 5-10 minutes before demo
- Refresh browser once before presenting
- Don't worry if no opportunities show (normal!)
- Point out the live updates (iteration counter)
- Highlight the price differences between exchanges

---

**That's it! Good luck with your demo! 🎯**
