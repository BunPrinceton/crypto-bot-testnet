# Crypto Arbitrage Dashboard Guide

Complete guide to all three arbitrage monitoring dashboards in this project.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all three dashboards (in separate terminals):
python src/multi_coin_dashboard.py    # Port 5001 - CEX Arbitrage
python src/pump_fun_dashboard.py       # Port 5002 - Pump.fun DEX
python src/raydium_dashboard.py        # Port 5003 - Raydium DEX
```

---

## Dashboard 1: Multi-Coin CEX Dashboard

**URL**: http://localhost:5001
**File**: `src/multi_coin_dashboard.py`

### Features
- **25 cryptocurrencies** monitored simultaneously
- **5 USA-friendly exchanges**: Kraken, Coinbase, Gemini, KuCoin, Bitstamp
- **Real-time arbitrage detection** with net profit calculations
- **Sortable table columns** (click headers to sort)
- **Demo mode** to simulate arbitrage opportunities for presentations
- **Live statistics**: total coins, coins with opportunities, best profit %

### What It Shows
- Average price across all exchanges
- Price spread percentage between exchanges
- Number of exchanges with price data
- Top arbitrage opportunities ranked by net profit
- Where to buy (cheapest exchange) and sell (most expensive exchange)

### Demo Mode
Click the "DEMO MODE" button in the top-right corner to:
- Simulate price variations across exchanges
- Show ~30% of coins with arbitrage opportunities
- Perfect for presentations when real opportunities are rare

### Use Case
Best for: High-cap cryptocurrencies on centralized exchanges with deep liquidity.

---

## Dashboard 2: Pump.fun DEX Dashboard

**URL**: http://localhost:5002
**File**: `src/pump_fun_dashboard.py`

### Features
- **5 popular Solana tokens**: BONK, WEN, POPCAT, WIF, MEW
- **Multi-DEX monitoring**: Tracks prices across Orca, Meteora, Raydium, Jupiter
- **Real arbitrage opportunities**: Live detection of profitable trades
- **Liquidity tracking**: Shows available liquidity on each DEX
- **Fast updates**: Refreshes every 5 seconds

### What It Shows
- Token average price (across all DEX pairs)
- Price spread percentage
- Total liquidity across all pairs
- 24-hour trading volume
- Number of active trading pairs
- **Arbitrage opportunities**: Buy from X DEX @ $Y, Sell to Z DEX @ $W
- Net profit % (after 0.3% fees on each trade)

### Example Output
```
#1: BONK
Buy from orca @ $0.0000124900 (Liq: $301K)
Sell to meteora @ $0.0000126200 (Liq: $69K)
💰 0.441% Net Profit
```

### Use Case
Best for: Solana memecoin traders looking for quick arbitrage between DEXs.

---

## Dashboard 3: Raydium DEX Dashboard

**URL**: http://localhost:5003
**File**: `src/raydium_dashboard.py`

### Features
- **10 Raydium liquidity pools** monitored
- **Slippage analysis**: Shows impact for trades of $100, $1K, $5K, $10K, $50K
- **CEX price comparison**: Compares DEX prices vs Kraken
- **Pool health metrics**: Liquidity, volume, transaction counts
- **24h price changes**: Track pool performance

### What It Shows
- Pool price in USD
- 24-hour price change (%)
- Total liquidity in USD
- 24-hour trading volume
- Number of transactions (buys + sells)
- Slippage for different trade sizes
- Comparison with CEX prices (when available)

### Slippage Analysis Example
```
SOL/USDC (Liquidity: $43.5M)
  $100    → 0.00% slippage
  $1,000  → 0.00% slippage
  $5,000  → 0.01% slippage
  $10,000 → 0.01% slippage
  $50,000 → 0.06% slippage
```

### Use Case
Best for: Traders who need to understand slippage impact before executing large trades on Raydium.

---

## Understanding the Data

### Arbitrage Opportunity Calculations

**Gross Profit**:
```
Gross Profit % = ((Sell Price - Buy Price) / Buy Price) × 100
```

**Net Profit** (after fees):
```
Net Profit % = Gross Profit % - (Fee% × 2)
```

- CEX fees: 0.2% per trade → 0.4% total
- DEX fees: 0.3% per trade → 0.6% total

**Example**:
- Buy BTC on Kraken: $43,500
- Sell BTC on Coinbase: $43,700
- Gross profit: 0.46%
- Net profit: 0.46% - 0.4% = **0.06%**

### Slippage Calculation

Slippage occurs when your trade moves the market price against you:

```
Slippage ≈ (Trade Size / Pool Liquidity) / (2 × (1 - Trade Size/Pool Liquidity))
```

**Rule of thumb**:
- Trade < 1% of liquidity → <0.01% slippage ✅
- Trade < 5% of liquidity → <0.25% slippage ⚠️
- Trade > 10% of liquidity → >1% slippage ❌

---

## API Sources

All dashboards use **free, no-auth APIs**:

### CEX Dashboard
- **CCXT Library**: https://github.com/ccxt/ccxt
- Unified API for 100+ exchanges
- Rate limit: Varies by exchange (~1200/min on Kraken)

### Pump.fun Dashboard
- **DexScreener API**: https://docs.dexscreener.com/api/reference
- Free tier: 300 requests/minute
- Covers all Solana DEXs (Orca, Meteora, Raydium, Jupiter, etc.)

### Raydium Dashboard
- **DexScreener API**: https://docs.dexscreener.com/api/reference
- Same as above
- Also uses CCXT for CEX price comparison

---

## Important Notes

### Profitability Reality Check

**CEX Arbitrage**:
- Markets are efficient - real opportunities are rare
- Most spreads are too small to cover fees
- Use Demo Mode for presentations

**DEX Arbitrage**:
- More opportunities on Solana (faster + cheaper than Ethereum)
- Real 0.3-0.8% opportunities exist on low-liquidity pairs
- Must account for:
  - Slippage (especially on smaller pools)
  - Gas fees (~$0.00025 per tx on Solana)
  - Price movement during execution
  - MEV/front-running risk

### Risk Warnings

⚠️ **This is monitoring software only. It does NOT execute trades.**

Before executing any arbitrage:
1. Verify prices on actual exchanges (APIs can lag)
2. Check current liquidity (can change rapidly)
3. Calculate slippage for YOUR trade size
4. Consider withdrawal/deposit times for CEX arbitrage
5. Account for network congestion (especially on Ethereum L2s)
6. Be aware of potential smart contract risks on DEXs

---

## Troubleshooting

### Dashboard not loading data?

**CEX Dashboard**:
- Check exchange is accessible from your region
- Verify internet connection
- Some exchanges (Binance) block USA IPs

**DEX Dashboards**:
- DexScreener API has 300 req/min limit
- Wait 1 minute if you hit rate limit
- Check console for specific errors

### Port already in use?

```bash
# Find process using port
lsof -i :5001
lsof -i :5002
lsof -i :5003

# Kill process
kill -9 <PID>
```

Or change port in the dashboard .py file:
```python
app.run(debug=True, host='0.0.0.0', port=5004)  # Change port here
```

---

## Advanced Usage

### Adding More Coins

**CEX Dashboard** (`src/multi_coin_dashboard.py`):
```python
SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT',
    'YOUR/COIN',  # Add here
]
```

**Pump.fun Dashboard** (`src/pump_fun_dashboard.py`):
```python
TOKEN_LIST = [
    {'symbol': 'BONK', 'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'},
    {'symbol': 'YOUR_TOKEN', 'address': 'YOUR_SOLANA_TOKEN_ADDRESS'},  # Add here
]
```

### Adjusting Update Frequency

All dashboards have update intervals:
```python
# In Python file
time.sleep(10)  # Change to adjust backend update frequency

# In HTML file
setInterval(updateDashboard, 5000);  # Change to adjust frontend refresh (milliseconds)
```

---

## File Structure

```
crypto-bot-testnet/
├── src/
│   ├── multi_coin_dashboard.py      # CEX dashboard backend
│   ├── pump_fun_dashboard.py         # Pump.fun dashboard backend
│   ├── raydium_dashboard.py          # Raydium dashboard backend
│   ├── pump_fun_monitor.py           # Pump.fun API wrapper
│   ├── raydium_monitor.py            # Raydium API wrapper
│   └── templates/
│       ├── multi_coin_dashboard.html  # CEX dashboard UI
│       ├── pump_fun_dashboard.html    # Pump.fun dashboard UI
│       └── raydium_dashboard.html     # Raydium dashboard UI
├── examples/
│   ├── pump_fun_basic_example.py
│   └── pump_fun_arbitrage_example.py
├── DASHBOARD_GUIDE.md                # This file
├── PUMP_FUN_INTEGRATION.md           # Pump.fun technical docs
├── RAYDIUM_INTEGRATION.md            # Raydium technical docs
└── requirements.txt
```

---

## Performance Tips

1. **Run dashboards on separate terminals** for better monitoring
2. **Use Chrome DevTools** to inspect live API calls
3. **Monitor network tab** to see real-time data updates
4. **Adjust update intervals** if hitting rate limits
5. **Use Demo Mode** when presenting to avoid API strain

---

## Next Steps

1. **Explore the dashboards**: Open all three in separate browser tabs
2. **Compare opportunities**: See which markets (CEX vs DEX) have better spreads
3. **Test with small amounts**: If you find an opportunity, test with minimal capital first
4. **Read integration docs**: Check PUMP_FUN_INTEGRATION.md and RAYDIUM_INTEGRATION.md for deep dives

---

## Questions?

- Check existing documentation: `PUMP_FUN_INTEGRATION.md`, `RAYDIUM_INTEGRATION.md`
- Review API docs: DexScreener (https://docs.dexscreener.com), CCXT (https://docs.ccxt.com)
- Test with CLI examples first: `examples/pump_fun_basic_example.py`

**Built for demonstration and educational purposes. Not financial advice.**
