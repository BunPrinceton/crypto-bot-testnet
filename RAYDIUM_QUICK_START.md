# Raydium Monitor - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies (Choose One)

**Option A: Minimal (just monitoring)**
```bash
pip install requests python-dotenv
```

**Option B: Full Solana features**
```bash
pip install -r requirements_dex.txt
```

### 2. Run the Monitor

```bash
python3 src/raydium_monitor.py
```

**Expected Output:**
- Live prices for 7+ Solana pairs
- Liquidity and volume data
- Slippage analysis for different trade sizes
- Arbitrage opportunities (if any)
- Saved snapshot in `data/` folder

### 3. Understanding the Output

**Pool Data Example:**
```
SOL/USDC     $159.360000   Liquidity: $43,495,161
```

**Slippage Analysis:**
```
Trade Size    Slippage    Effective Buy Price
$  1,000       0.00%      $159.760237
$ 10,000       0.01%      $159.776769
```

**Interpretation:**
- $1K trade = almost no slippage (0.00%)
- $10K trade = minimal slippage (0.01%)
- This pool has excellent liquidity!

---

## Quick Integration Examples

### Example 1: Compare DEX vs CEX

```python
from src.raydium_monitor import RaydiumMonitor
import ccxt

# Initialize
dex = RaydiumMonitor()
cex = ccxt.binance()

# Fetch prices
dex_pools = dex.fetch_all_pools()
cex_ticker = cex.fetch_ticker('SOL/USDT')

# Compare
dex_price = dex_pools['SOL/USDC']['price_usd']
cex_price = cex_ticker['last']

spread = ((cex_price - dex_price) / dex_price) * 100
print(f"Spread: {spread:.2f}%")

if abs(spread) > 0.5:
    print("ARBITRAGE OPPORTUNITY!")
```

### Example 2: Calculate Trade Cost

```python
monitor = RaydiumMonitor()
pools = monitor.fetch_all_pools()

# Get SOL/USDC pool
sol_pool = pools['SOL/USDC']

# Calculate for $10K trade
slippage = monitor.calculate_slippage(
    sol_pool['liquidity_usd'],
    10000
)

effective_price = monitor.calculate_effective_price(
    sol_pool['price_usd'],
    slippage,
    monitor.RAYDIUM_FEE_PERCENT,
    is_buy=True
)

print(f"Base price: ${sol_pool['price_usd']:.2f}")
print(f"Slippage: {slippage:.2f}%")
print(f"Effective buy price: ${effective_price:.2f}")
```

### Example 3: Monitor and Alert

```python
import time

monitor = RaydiumMonitor()

while True:
    pools = monitor.fetch_all_pools()

    # Check liquidity warnings
    for symbol, data in pools.items():
        if data['liquidity_usd'] < 500000:
            print(f"WARNING: {symbol} low liquidity!")

    # Save snapshot every 5 minutes
    monitor.save_snapshot(pools)

    time.sleep(300)
```

---

## Common Use Cases

### Research: "What's the best pool for SOL?"

Run the monitor and look at the output table:

```
Symbol       Price (USD)     Liquidity       24h Volume
SOL/USDC     $159.360000     $43,495,161    $118,775,578  <- BEST
SOL/USDT     $159.320000     $1,132,260     $23,071,169
```

**Answer:** SOL/USDC on Orca (highest liquidity, lowest slippage)

---

### Trading: "How much slippage for my trade?"

Look at the slippage analysis:

```
SOL/USDC (Liquidity: $43,495,161)
  $ 10,000       0.01%      $159.776769
  $ 50,000       0.06%      $159.850331
```

**Answer:** $10K = 0.01%, $50K = 0.06% (very low!)

---

### Arbitrage: "Is there a CEX-DEX opportunity?"

The monitor compares automatically:

```
COMPARING WITH CEX PRICES
  SOL/USDT: $159.678720

No profitable arbitrage opportunities found
```

**Answer:** Current spread too small (need >0.5%)

---

## File Locations

**Code:**
- `/src/raydium_monitor.py` - Main monitor

**Documentation:**
- `RAYDIUM_INTEGRATION.md` - Comprehensive guide (how AMMs work)
- `DEX_VS_CEX_ARBITRAGE.md` - Profitability analysis
- `RAYDIUM_IMPLEMENTATION_REPORT.md` - Technical report
- `RAYDIUM_QUICK_START.md` - This file

**Data:**
- `/data/raydium_snapshot_*.json` - Saved snapshots

---

## What's Monitored

**Working Pools (7/10):**
- ✅ SOL/USDC (Orca) - $43.5M liquidity
- ✅ SOL/USDT (Raydium) - $1.1M liquidity
- ✅ RAY/USDC - $5.2M liquidity
- ✅ RAY/SOL - $5.6M liquidity
- ✅ WIF/USDC - $10.1M liquidity
- ✅ JUP/USDC - $579K liquidity
- ✅ ORCA/USDC - $858K liquidity

**Need Pool ID Updates:**
- ❌ BONK/USDC
- ❌ PYTH/USDC
- ❌ JTO/USDC

---

## Next Steps

**For Learning:**
1. Run the monitor daily for a week
2. Track price differences vs CEX
3. Read `RAYDIUM_INTEGRATION.md`

**For Trading:**
1. Start with manual monitoring (this tool)
2. Test with $100-$500 first
3. Read `DEX_VS_CEX_ARBITRAGE.md` for strategies

**For Development:**
1. Add Jupiter API integration
2. Implement WebSocket feeds
3. Build execution logic (see report for roadmap)

---

## Troubleshooting

**Q: No pool data returned?**

A: Check internet connection and DexScreener API status

**Q: Slippage seems high?**

A: Check pool liquidity. Small pools = high slippage

**Q: Getting rate limited?**

A: Increase `min_request_interval` in code (default 0.21s)

**Q: Snapshot not saving?**

A: Check `data/` folder exists and is writable

---

## Support

**Issues:** Check `RAYDIUM_IMPLEMENTATION_REPORT.md` for known issues

**Advanced Usage:** See `RAYDIUM_INTEGRATION.md` for detailed examples

**Profitability Questions:** Read `DEX_VS_CEX_ARBITRAGE.md`

---

**That's it! You're ready to monitor Solana DEX prices.**

Run: `python3 src/raydium_monitor.py` and explore!
