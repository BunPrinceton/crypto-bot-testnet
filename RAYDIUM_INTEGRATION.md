# Raydium DEX Integration Guide

## Overview

This document explains the Raydium integration for the crypto arbitrage bot, including how AMMs work, differences from CEX trading, and how to use the Raydium monitor.

**Raydium** is the leading automated market maker (AMM) and liquidity provider on the Solana blockchain, similar to Uniswap on Ethereum. It uses a constant product formula (x * y = k) for pricing and enables decentralized token swaps.

---

## Table of Contents

1. [How Raydium Works](#how-raydium-works)
2. [CEX vs DEX Key Differences](#cex-vs-dex-key-differences)
3. [Installation & Setup](#installation--setup)
4. [Using the Raydium Monitor](#using-the-raydium-monitor)
5. [Understanding the Output](#understanding-the-output)
6. [Arbitrage Strategies](#arbitrage-strategies)
7. [Limitations & Risks](#limitations--risks)
8. [Advanced Usage](#advanced-usage)

---

## How Raydium Works

### Automated Market Maker (AMM) Basics

Unlike centralized exchanges with order books, Raydium uses **liquidity pools**:

1. **Liquidity Pool**: A smart contract holding two tokens (e.g., SOL and USDC)
2. **Constant Product Formula**: `x * y = k` where:
   - `x` = amount of token A in pool
   - `y` = amount of token B in pool
   - `k` = constant product
3. **Price Determination**: Price is the ratio of the two reserves
   - If pool has 1000 SOL and 100,000 USDC, price = 100,000/1000 = $100/SOL

### Trading Mechanics

When you swap tokens:
1. You add token A to the pool
2. You receive token B from the pool
3. The product `k` remains constant
4. Price adjusts based on new ratio

**Example:**
- Pool: 1000 SOL, 100,000 USDC (k = 100,000,000)
- You swap 10 SOL for USDC
- New pool: 1010 SOL, 99,010 USDC (k ≈ 100,000,000)
- You received ~990 USDC (not 1000!) due to slippage
- New price: ~$98/SOL (price moved against you)

### Raydium Fees

- **Swap Fee**: 0.25% (0.22% to LPs, 0.03% to protocol)
- **Solana Gas**: ~0.000005 SOL per transaction (~$0.0001 at $100/SOL)

---

## CEX vs DEX Key Differences

| Aspect | CEX (Binance, Coinbase) | DEX (Raydium) |
|--------|------------------------|---------------|
| **Price Discovery** | Order book matching | AMM formula (x*y=k) |
| **Liquidity** | Centralized, deep | Distributed, varies by pool |
| **Slippage** | Minimal for market orders | Increases with trade size |
| **Fees** | 0.1% typical | 0.25% swap fee + gas |
| **Speed** | Instant execution | ~400ms Solana block time |
| **Custody** | Custodial (CEX holds funds) | Non-custodial (you control) |
| **MEV Risk** | None | Sandwich attacks possible |
| **Account Required** | Yes (KYC) | No (just a wallet) |
| **API Access** | Rate limited, auth needed | Public APIs available |
| **Price Impact** | Low (deep order books) | High for large trades |

### Critical Differences for Arbitrage

1. **Slippage**: DEX trades suffer price impact; CEX limit orders don't
2. **Fees**: Raydium 0.25% vs CEX 0.1% = 0.15% disadvantage
3. **Speed**: Solana block time + network congestion
4. **MEV**: Bots can front-run your DEX trades
5. **Liquidity Fragmentation**: Multiple DEX pools for same pair

---

## Installation & Setup

### Prerequisites

```bash
# Python 3.8+
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Install Dependencies

**Option 1: Minimal (just price monitoring)**
```bash
pip install requests python-dotenv
```

**Option 2: Full DEX integration**
```bash
pip install -r requirements_dex.txt
```

This installs:
- `solana` - Solana Python SDK
- `solders` - Rust-based Solana SDK (faster)
- `base58` - Address encoding
- `anchorpy` - For Anchor programs (Raydium uses Anchor)

### Quick Test

```bash
# Test the monitor
python src/raydium_monitor.py
```

You should see live data from 10+ Raydium pools!

---

## Using the Raydium Monitor

### Basic Usage

```python
from src.raydium_monitor import RaydiumMonitor

# Initialize monitor
monitor = RaydiumMonitor(data_dir="data")

# Fetch all pool data
pools_data = monitor.fetch_all_pools()

# Display table
monitor.display_pools_table(pools_data)
```

### Fetch Single Pool

```python
# Get SOL/USDC pool data
pool_data = monitor.fetch_pool_data(
    pool_id="JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    symbol="SOL/USDC"
)

print(f"SOL Price: ${pool_data['price_usd']}")
print(f"Liquidity: ${pool_data['liquidity_usd']:,.0f}")
print(f"24h Volume: ${pool_data['volume_24h']:,.0f}")
```

### Calculate Slippage

```python
# Calculate slippage for a $5000 trade
slippage = monitor.calculate_slippage(
    liquidity_usd=10_000_000,  # $10M pool
    trade_size_usd=5_000
)

print(f"Estimated slippage: {slippage:.2f}%")
# Output: ~0.05% for $5K trade in $10M pool
```

### Get Effective Price (with slippage + fees)

```python
base_price = 100.0  # $100/SOL
slippage = 0.5      # 0.5%
fee = 0.25          # 0.25%

# Buying (price increases)
buy_price = monitor.calculate_effective_price(
    base_price, slippage, fee, is_buy=True
)
# Result: $100.75 (0.5% slippage + 0.25% fee)

# Selling (price decreases)
sell_price = monitor.calculate_effective_price(
    base_price, slippage, fee, is_buy=False
)
# Result: $99.25
```

---

## Understanding the Output

### Pool Data Structure

```python
{
    'symbol': 'SOL/USDC',
    'pool_id': 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',
    'price_usd': 98.456789,
    'price_native': 1.0,  # SOL is native token
    'liquidity_usd': 45000000.0,  # $45M liquidity
    'volume_24h': 12000000.0,      # $12M daily volume
    'price_change_24h': 2.5,       # +2.5%
    'txns_24h_buys': 1500,
    'txns_24h_sells': 1400,
    'fdv': 5000000000.0,           # Fully diluted valuation
    'market_cap': 4500000000.0,
    'timestamp': '2025-11-09T12:34:56',
    'dex': 'raydium'
}
```

### Arbitrage Opportunity Structure

```python
{
    'symbol': 'SOL/USDC',
    'direction': 'DEX→CEX',           # Buy on DEX, sell on CEX
    'buy_venue': 'Raydium',
    'sell_venue': 'CEX',
    'buy_price': 98.50,
    'sell_price': 99.20,
    'gross_profit_pct': 0.71,         # 0.71% profit before gas
    'slippage_pct': 0.15,             # 0.15% slippage
    'liquidity_usd': 45000000.0,
    'trade_size_usd': 1000.0
}
```

---

## Arbitrage Strategies

### 1. CEX-DEX Arbitrage

**Strategy**: Buy on the cheaper venue, sell on the more expensive one.

**Example:**
- Raydium SOL/USDC: $98.50 (after slippage + fees)
- Binance SOL/USDT: $99.20 (after fees)
- **Profit**: 0.71% per round trip

**Reality Check:**
```
Buy 1 SOL on Raydium:  $98.50
Sell 1 SOL on Binance: $99.20
Gross profit:          $0.70
Solana gas:            $0.0001
Withdrawal fee:        $0.50 (if moving SOL to CEX)
NET PROFIT:            $0.20 (0.2%)
```

**Key Challenge**: Moving funds between CEX and DEX takes time (minutes to hours), during which prices change.

### 2. Triangle Arbitrage (DEX-only)

**Strategy**: Execute 3 swaps in a cycle to profit from price inefficiencies.

**Example Route: SOL → USDC → RAY → SOL**

```
1. Start: 1 SOL
2. Swap SOL → USDC:  1 SOL = 100 USDC (after fees: 99.75 USDC)
3. Swap USDC → RAY:  99.75 USDC = 50 RAY (after fees: 49.87 RAY)
4. Swap RAY → SOL:   49.87 RAY = 1.01 SOL (after fees: 1.007 SOL)
5. Net profit: 0.007 SOL = 0.7% profit
```

**Advantages:**
- No CEX needed (fully on-chain)
- Instant execution (single Solana transaction)
- No withdrawal delays

**Disadvantages:**
- 3x fees (0.75% total)
- 3x slippage
- Requires all 3 pools to be liquid

### 3. Cross-DEX Arbitrage

**Strategy**: Exploit price differences between Raydium, Orca, and other Solana DEXs.

**Example:**
- Raydium SOL/USDC: $98.50
- Orca SOL/USDC: $99.00
- **Profit**: 0.5% minus fees

**Implementation:**
```python
# Compare Raydium vs Orca
raydium_price = monitor.fetch_pool_data(...)
orca_price = fetch_orca_price(...)  # Need Orca SDK

if raydium_price < orca_price * 0.995:  # 0.5% threshold
    # Buy on Raydium, sell on Orca
    execute_arbitrage()
```

### Profit Calculation Formula

```python
# CEX-DEX Arbitrage
net_profit = (
    sell_price * (1 - cex_fee)
    - buy_price * (1 + dex_fee) * (1 + slippage)
    - gas_cost_usd
    - withdrawal_fee
) / buy_price * 100

# Triangle Arbitrage
net_profit = (
    final_amount / initial_amount - 1
    - 3 * fee_per_swap
    - total_slippage
) * 100
```

---

## Limitations & Risks

### Technical Limitations

1. **No Real-time WebSocket**: Uses DexScreener API (polling, rate limited to 300 req/min)
2. **Approximate Slippage**: Actual slippage requires on-chain pool reserve data
3. **No On-chain Execution**: Monitor only; doesn't execute trades
4. **Gas Estimation**: Fixed at 0.000005 SOL; can spike during congestion

### Market Risks

1. **MEV (Maximal Extractable Value)**
   - Bots scan the mempool for profitable trades
   - Can "sandwich" your trade: buy before you, sell after you
   - Your profit becomes their profit
   - **Mitigation**: Use private RPC endpoints, MEV-protected relayers

2. **Slippage**
   - Large trades move the price against you
   - $10K trade in $1M pool = ~1% slippage
   - **Mitigation**: Split into smaller trades, use Jupiter aggregator

3. **Impermanent Loss** (if providing liquidity)
   - Price divergence causes loss for LPs
   - Not relevant for arbitrage traders

4. **Failed Transactions**
   - Solana transactions can fail (price moved, insufficient balance)
   - You still pay gas
   - **Mitigation**: Use slippage tolerance, check balance beforehand

5. **Regulatory Risk**
   - DEX arbitrage is unregulated
   - Tax implications vary by jurisdiction
   - **Consult a tax professional**

### Execution Challenges

1. **Capital Requirements**
   - Need funds on both CEX and DEX
   - Withdrawal delays can lock capital for hours

2. **Network Congestion**
   - Solana can slow down during high activity
   - Gas fees spike (priority fees needed)

3. **Oracle Delays**
   - CEX prices update instantly
   - DexScreener API has ~1-2 second lag

---

## Advanced Usage

### Integrating with CEX Monitor

```python
import ccxt
from src.raydium_monitor import RaydiumMonitor

# Initialize both monitors
dex_monitor = RaydiumMonitor()
cex = ccxt.binance()

# Fetch prices
dex_pools = dex_monitor.fetch_all_pools()
cex_ticker = cex.fetch_ticker('SOL/USDT')

# Compare
cex_price = cex_ticker['last']
dex_price = dex_pools['SOL/USDC']['price_usd']

price_diff = ((cex_price - dex_price) / dex_price) * 100
print(f"Price difference: {price_diff:.2f}%")

# Find arbitrage
opportunities = dex_monitor.compare_with_cex(
    dex_pools,
    {'SOL/USDT': cex_price},
    trade_size_usd=1000
)
```

### Using Jupiter API for Better Prices

Jupiter aggregates liquidity from multiple DEXs (Raydium, Orca, etc.) to get best prices:

```python
import requests

def get_jupiter_quote(input_mint, output_mint, amount_lamports):
    """Get best price from Jupiter aggregator"""
    url = f"https://quote-api.jup.ag/v6/quote"
    params = {
        'inputMint': input_mint,
        'outputMint': output_mint,
        'amount': amount_lamports,
        'slippageBps': 50  # 0.5% slippage tolerance
    }

    response = requests.get(url, params=params)
    quote = response.json()

    return {
        'input_amount': int(quote['inAmount']),
        'output_amount': int(quote['outAmount']),
        'price_impact': float(quote['priceImpactPct']),
        'route': quote['routePlan']  # Which DEXs it uses
    }

# Example: Get quote for 1 SOL → USDC
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

quote = get_jupiter_quote(SOL_MINT, USDC_MINT, 1_000_000_000)  # 1 SOL
print(f"Jupiter price: ${quote['output_amount'] / 1_000_000:.2f}")
```

### Monitoring Multiple Pools

```python
import time

monitor = RaydiumMonitor()

# Continuous monitoring
while True:
    pools = monitor.fetch_all_pools()

    # Check liquidity changes
    for symbol, data in pools.items():
        if data['liquidity_usd'] < 100_000:
            print(f"WARNING: {symbol} liquidity low: ${data['liquidity_usd']:,.0f}")

    # Save snapshot every 5 minutes
    monitor.save_snapshot(pools)

    time.sleep(300)  # 5 minutes
```

---

## Example Use Cases

### 1. Price Discovery Research

**Goal**: Understand which venue has better prices for SOL.

```bash
python src/raydium_monitor.py
```

Check output:
- Raydium SOL/USDC vs Binance SOL/USDT
- If Raydium consistently cheaper → CEX premium exists
- If Raydium more expensive → DEX premium (possibly due to MEV bots)

### 2. Liquidity Analysis

**Goal**: Find the most liquid pools for low slippage.

```python
pools = monitor.fetch_all_pools()

# Sort by liquidity
sorted_pools = sorted(
    pools.items(),
    key=lambda x: x[1]['liquidity_usd'],
    reverse=True
)

print("Top 5 Most Liquid Pools:")
for symbol, data in sorted_pools[:5]:
    print(f"{symbol}: ${data['liquidity_usd']:,.0f}")
```

### 3. Historical Analysis

**Goal**: Track arbitrage opportunities over time.

```python
import json
from pathlib import Path

# Load all snapshots
data_dir = Path("data")
snapshots = []

for file in data_dir.glob("raydium_snapshot_*.json"):
    with open(file) as f:
        snapshots.append(json.load(f))

# Analyze
for snapshot in snapshots:
    sol_price = snapshot.get('SOL/USDC', {}).get('price_usd', 0)
    timestamp = snapshot.get('SOL/USDC', {}).get('timestamp', '')
    print(f"{timestamp}: ${sol_price:.2f}")
```

---

## Comparison: CEX vs DEX Arbitrage

| Factor | CEX Arbitrage | DEX Arbitrage |
|--------|---------------|---------------|
| **Profit Margin** | 0.1-0.3% typical | 0.3-1.0% possible |
| **Execution Speed** | Milliseconds | 400ms-2s (Solana) |
| **Capital Efficiency** | High (instant settlement) | Low (cross-venue delays) |
| **Fees** | 0.1-0.2% | 0.25-0.75% |
| **Slippage** | Minimal | Significant |
| **MEV Risk** | None | High |
| **Barriers to Entry** | KYC, API keys | Just a wallet |
| **Automation** | Easy (CCXT) | Complex (Web3) |
| **Frequency** | Rare (efficient markets) | More common (fragmentation) |

**Verdict**: CEX arbitrage is more efficient but harder to find. DEX arbitrage has more opportunities but higher execution risk.

---

## Troubleshooting

### API Rate Limit Errors

**Problem**: `429 Too Many Requests` from DexScreener

**Solution**: The monitor has built-in rate limiting (0.21s between requests). If you're still hitting limits:
```python
monitor.min_request_interval = 0.5  # Slow down to 2 requests/sec
```

### No Pool Data Returned

**Problem**: `fetch_pool_data()` returns `None`

**Possible Causes**:
1. Invalid pool ID
2. Pool doesn't exist on Raydium
3. Network error

**Debug**:
```python
import requests
response = requests.get(
    "https://api.dexscreener.com/latest/dex/pairs/solana/POOL_ID"
)
print(response.status_code)
print(response.text)
```

### Slippage Too High

**Problem**: All trades show >5% slippage

**Solution**: You're trying to trade too much for the pool size. Reduce `trade_size_usd` or choose larger pools.

---

## Next Steps

1. **Test with Real Data**: Run `python src/raydium_monitor.py` and observe live prices
2. **Compare with CEX**: Integrate with your existing `price_monitor.py`
3. **Build a Dashboard**: Add Raydium to `multi_coin_dashboard.py`
4. **Implement Execution**: Use Solana SDK to actually execute trades (requires wallet)
5. **Add Jupiter**: Integrate Jupiter API for multi-DEX routing

---

## Resources

- [Raydium Docs](https://docs.raydium.io/)
- [Solana Docs](https://docs.solana.com/)
- [Jupiter Docs](https://station.jup.ag/docs)
- [DexScreener API](https://docs.dexscreener.com/)
- [Constant Product AMM Explained](https://docs.uniswap.org/protocol/V2/concepts/protocol-overview/how-uniswap-works)

---

## License

Same as main project.

## Disclaimer

This software is for educational purposes only. Trading cryptocurrencies carries significant financial risk. DEX arbitrage involves smart contract risk, MEV risk, and potential loss of funds. Always test with small amounts first. Not financial advice.
