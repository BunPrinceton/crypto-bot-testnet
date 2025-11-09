# Pump.fun Integration Guide

## Overview

This document explains the Pump.fun integration for monitoring Solana-based memecoins in your arbitrage bot. Pump.fun is a launchpad for creating and trading memecoins on Solana using a bonding curve mechanism.

**Status:** ✅ Functional price monitoring implemented
**Last Updated:** 2025-11-09

---

## Table of Contents

1. [What is Pump.fun?](#what-is-pumpfun)
2. [Architecture Overview](#architecture-overview)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [API Methods](#api-methods)
6. [Data Sources](#data-sources)
7. [Challenges & Limitations](#challenges--limitations)
8. [Arbitrage Considerations](#arbitrage-considerations)
9. [Future Enhancements](#future-enhancements)

---

## What is Pump.fun?

### Platform Overview

Pump.fun is a decentralized token launchpad on Solana that enables anyone to create memecoins instantly. Key features:

- **No Code Required**: Create tokens with just a name, symbol, and image
- **Bonding Curve Mechanism**: Automated market maker (AMM) with linear bonding curve
- **Fair Launch**: No presales, no team allocations
- **Migration to Raydium**: Tokens automatically migrate to Raydium DEX at $69k market cap
- **Low Fees**: Solana's low transaction costs (~$0.00025 per transaction)

### How the Bonding Curve Works

1. **Token Creation**: Anyone can create a token for ~0.02 SOL
2. **Initial Trading**: Tokens trade on Pump.fun's bonding curve
3. **Price Discovery**: Price increases as more tokens are purchased (constant product formula: x*y=k)
4. **Migration Threshold**: At $69k market cap, liquidity migrates to Raydium
5. **Post-Migration**: Token trades on Raydium as a standard DEX pair

### Key Metrics

- **Virtual Reserves**: Used for pricing calculations
- **Real Reserves**: Actual SOL and tokens in the curve
- **Bonding Progress**: Percentage towards Raydium migration (0-100%)
- **Graduation**: When a token migrates to Raydium (bonding complete)

---

## Architecture Overview

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Pump.fun Monitor                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  DexScreener API │         │  On-Chain Data   │          │
│  │  (Primary)       │         │  (Optional)      │          │
│  └────────┬─────────┘         └────────┬─────────┘          │
│           │                            │                     │
│           │  REST API                  │  Solana RPC        │
│           │  60 req/min                │  Direct queries    │
│           │                            │                     │
│  ┌────────▼────────────────────────────▼─────────┐          │
│  │         PumpFunMonitor Class                  │          │
│  │  - fetch_token_price_dexscreener()            │          │
│  │  - fetch_trending_pumpfun_tokens()            │          │
│  │  - fetch_bonding_curve_price() (on-chain)     │          │
│  │  - detect_dex_arbitrage()                     │          │
│  └───────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **DexScreener API** → Aggregated price data from multiple DEXs
2. **On-Chain Queries** → Direct bonding curve state from Solana RPC
3. **Price Calculation** → Compute token price from reserves
4. **Arbitrage Detection** → Compare prices across DEXs/CEXs

---

## Installation

### Prerequisites

- Python 3.8+
- Existing crypto-bot-testnet setup
- Internet connection for API calls

### Step 1: Install Core Dependencies

```bash
# Navigate to project directory
cd /mnt/c/Users/benja/Documents/projects/crypto-bot-testnet

# Install base requirements if not already installed
pip install -r requirements.txt
```

### Step 2: Install DEX-Specific Dependencies

```bash
# Install Solana and DEX libraries
pip install -r requirements_dex.txt
```

**Note:** The Solana libraries are **optional**. The monitor works with just DexScreener API if you skip this step. However, on-chain queries provide more accurate real-time data.

### Step 3: System Dependencies (for Solana libraries)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential pkg-config libssl-dev
```

**MacOS:**
```bash
xcode-select --install
```

**Windows (WSL recommended):**
```bash
# Use WSL Ubuntu and follow Ubuntu instructions
```

### Troubleshooting Installation

If `solders` fails to install:
```bash
# Install without Solana libraries
pip install requests  # Should already be installed

# The monitor will work with DexScreener only
# You'll see: "⚠️  Solana libraries not available. On-chain queries disabled."
```

---

## Usage Examples

### Basic Usage - Fetch Single Token

```python
from src.pump_fun_monitor import PumpFunMonitor

# Initialize monitor
monitor = PumpFunMonitor(demo_mode=False)

# Fetch token price
token_address = "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"  # POPCAT
price_data = monitor.fetch_token_price_dexscreener(token_address)

if price_data:
    print(f"Token: {price_data['symbol']}")
    print(f"Price: ${price_data['price_usd']:.8f}")
    print(f"Liquidity: ${price_data['liquidity_usd']:,.2f}")
    print(f"24h Volume: ${price_data['volume_24h']:,.2f}")
```

### Fetch Multiple Tokens

```python
token_addresses = [
    "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
    "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",  # WEN
]

prices = monitor.fetch_multiple_tokens(token_addresses)

for address, data in prices.items():
    print(f"{data['symbol']}: ${data['price_usd']:.8f}")
```

### Fetch Trending Tokens

```python
# Get trending Pump.fun tokens
trending = monitor.fetch_trending_pumpfun_tokens()

print(f"Found {len(trending)} trending tokens:")
for i, token in enumerate(trending[:5], 1):
    base = token.get('baseToken', {})
    symbol = base.get('symbol')
    price = float(token.get('priceUsd', 0))
    volume = float(token.get('volume', {}).get('h24', 0))

    print(f"{i}. {symbol}: ${price:.8f} | 24h Vol: ${volume:,.0f}")
```

### On-Chain Price Query (Advanced)

```python
import asyncio

async def get_onchain_price():
    monitor = PumpFunMonitor()

    # Fetch price directly from bonding curve
    mint_address = "GjSn1XHncttWZtx9u6JB9BNM3QYqiumXfGbtkm4ypump"
    price_sol = await monitor.fetch_bonding_curve_price(mint_address)

    if price_sol:
        print(f"On-chain price: {price_sol:.10f} SOL")
    else:
        print("Unable to fetch on-chain price")

# Run async function
asyncio.run(get_onchain_price())
```

### Run the Demo

```bash
# Run the built-in demo
python src/pump_fun_monitor.py
```

Expected output:
```
🚀 PUMP.FUN MONITOR - Solana Memecoin Price Tracker
================================================================================
Features:
  ✓ DexScreener API integration (free, no auth required)
  ✓ Real-time price monitoring
  ✓ Trending token discovery
  ✓ On-chain bonding curve queries (optional)
  ✓ Solana libraries: AVAILABLE

📊 Fetching prices for sample tokens...
[1/5] Fetching GjSn1XHncttWZtx9u6JB9BNM3QYqiumXfGbtkm4ypump...

Token: Example Token (EXAM)
Price (USD):    $0.0000123456
Price (SOL):    0.000000567 SOL
Liquidity:      $12,345.67
24h Volume:     $67,890.12
...
```

---

## API Methods

### `PumpFunMonitor` Class

#### `__init__(demo_mode=False)`

Initialize the monitor.

**Parameters:**
- `demo_mode` (bool): Enable demo mode (currently unused, for future features)

**Returns:** PumpFunMonitor instance

---

#### `fetch_token_price_dexscreener(token_address: str) -> Optional[Dict]`

Fetch comprehensive price data for a single token from DexScreener.

**Parameters:**
- `token_address` (str): Solana token mint address

**Returns:**
```python
{
    'symbol': str,           # Token symbol (e.g., 'BONK')
    'name': str,             # Token name
    'address': str,          # Mint address
    'price_usd': float,      # Price in USD
    'price_native': float,   # Price in SOL
    'liquidity_usd': float,  # Total liquidity in USD
    'volume_24h': float,     # 24-hour volume
    'price_change_24h': float, # 24h price change %
    'dex': str,              # DEX identifier
    'pair_address': str,     # Pair contract address
    'fdv': float,            # Fully diluted valuation
    'market_cap': float,     # Market capitalization
    'timestamp': str         # ISO timestamp
}
```

---

#### `fetch_trending_pumpfun_tokens() -> List[Dict]`

Fetch trending Pump.fun tokens from DexScreener.

**Returns:** List of token dictionaries (up to 20)

---

#### `fetch_multiple_tokens(token_addresses: List[str]) -> Dict[str, Dict]`

Fetch prices for multiple tokens with automatic rate limiting.

**Parameters:**
- `token_addresses` (List[str]): List of token mint addresses

**Returns:** Dictionary mapping addresses to price data

---

#### `fetch_bonding_curve_price(mint_address: str) -> Optional[float]` (async)

Fetch price directly from on-chain bonding curve.

**Requires:** Solana libraries installed

**Parameters:**
- `mint_address` (str): Token mint address

**Returns:** Price in SOL or None

---

#### `detect_dex_arbitrage(prices: Dict, fee_percent: float = 0.3) -> List[Dict]`

Detect arbitrage opportunities between different DEX pairs.

**Parameters:**
- `prices` (Dict): Dictionary of token prices
- `fee_percent` (float): Trading fee percentage (default: 0.3%)

**Returns:** List of arbitrage opportunities sorted by profit

---

## Data Sources

### 1. DexScreener API (Primary)

**Advantages:**
- ✅ Free, no authentication required
- ✅ Aggregates data from multiple DEXs
- ✅ 300 requests/minute rate limit
- ✅ Comprehensive data (price, volume, liquidity, etc.)
- ✅ Easy to use REST API

**Limitations:**
- ❌ ~1-2 second delay vs on-chain
- ❌ Limited to tokens with active pairs
- ❌ No historical data beyond 24h

**Endpoints Used:**
- `/latest/dex/tokens/{chainId}/{tokenAddress}` - Token data
- `/latest/dex/search?q={query}` - Search tokens
- `/latest/dex/pairs/{chainId}/{pairId}` - Pair details

### 2. On-Chain Solana RPC (Optional)

**Advantages:**
- ✅ Real-time data (no delay)
- ✅ Direct from source (bonding curve)
- ✅ Works for any token (even before DEX pairs exist)
- ✅ Most accurate pricing

**Limitations:**
- ❌ Requires Solana libraries
- ❌ More complex implementation
- ❌ RPC rate limits (varies by provider)
- ❌ Only provides price, not volume/liquidity

**How It Works:**
1. Derive bonding curve PDA (Program Derived Address)
2. Fetch account data via RPC
3. Parse binary data structure
4. Calculate price from virtual reserves

### 3. Alternative APIs (Not Implemented)

**Bitquery:**
- GraphQL API for blockchain data
- Paid service ($99-$999/month)
- More comprehensive historical data

**Moralis:**
- Pump.fun API support
- Free tier available
- Good for metadata and events

**Birdeye:**
- Professional DEX aggregator
- WebSocket support
- Paid tiers for high-frequency data

---

## Challenges & Limitations

### 1. DEX-Specific Challenges

#### High Volatility
- **Issue:** Memecoin prices can swing 100%+ in seconds
- **Impact:** Arbitrage opportunities appear/disappear rapidly
- **Mitigation:** Use WebSockets (future enhancement) for real-time updates

#### Low Liquidity
- **Issue:** Many tokens have <$1k liquidity
- **Impact:** Slippage can exceed 10-50% on trades
- **Mitigation:** Filter by minimum liquidity threshold (e.g., $5k+)

#### Rug Pulls
- **Issue:** Token creators can abandon projects
- **Impact:** Liquidity disappears, token becomes worthless
- **Mitigation:** Check bonding curve completion, audit contract

### 2. Technical Challenges

#### Gas Fees (Minimal)
- **Solana:** ~$0.00025 per transaction
- **Impact:** Negligible compared to Ethereum (~$5-50)
- **Note:** Not a significant concern for arbitrage

#### Slippage
- **Issue:** Price moves between quote and execution
- **Formula:** `slippage = (execution_price - quoted_price) / quoted_price * 100`
- **Typical Range:** 0.5% to 5% on Pump.fun
- **Mitigation:** Set slippage tolerance, use limit orders

#### MEV/Frontrunning
- **Issue:** Bots can see pending transactions and front-run
- **Impact:** Your arbitrage gets taken by faster bots
- **Mitigation:** Use private RPC, Jito bundles, or direct DEX integration

### 3. Rate Limiting

**DexScreener:**
- 300 requests/minute for price data
- 60 requests/minute for profiles/boosts
- **Impact:** Can monitor ~150 tokens/minute with 2-second updates

**Solana RPC:**
- Public RPC: ~10-50 req/sec
- Helius/Quicknode: 100+ req/sec (paid)
- **Impact:** On-chain queries more limited on free tier

### 4. Data Accuracy

**DexScreener Delay:**
- Typically 1-2 seconds behind on-chain
- During high volatility, can be 5-10 seconds
- **Solution:** Use on-chain queries for critical trades

**Bonding Curve vs DEX Price:**
- Pump.fun bonding curve price ≠ Raydium price (after migration)
- Can diverge by 1-5% due to arbitrage lag
- **Solution:** Check migration status before trading

### 5. Token Identification

**Address Changes:**
- Token may have different addresses on different chains
- Wrapped versions (e.g., wSOL) vs native
- **Solution:** Maintain token mapping database

**Spam Tokens:**
- Thousands of new tokens daily
- Many are scams or duplicates
- **Solution:** Filter by volume, age, liquidity

---

## Arbitrage Considerations

### CEX vs DEX Arbitrage

**Challenges:**
1. **Listing Lag:** Pump.fun tokens rarely listed on CEXs
2. **Transfer Time:** Moving SOL to CEX takes 5-30 minutes
3. **Withdrawal Fees:** CEX withdrawal fees can be high
4. **KYC Requirements:** CEXs require identity verification

**Opportunity:** Only viable for graduated tokens on major CEXs (very rare)

### DEX vs DEX Arbitrage

**More Viable:**
1. **Pump.fun → Raydium:** After migration, prices can diverge
2. **Raydium → Orca:** Different AMM algorithms create spreads
3. **Jupiter Aggregation:** Compare Jupiter quotes vs direct swaps

**Example Scenario:**
```
Token XYZ migrates to Raydium at $0.001
↓
Pump.fun still shows $0.00095 (bonding curve residual)
↓
Arbitrage: Buy on Pump.fun, sell on Raydium
↓
Profit: 0.5% - fees (0.3% * 2) = -0.1% (UNPROFITABLE)
```

**Reality Check:** DEX-DEX arbitrage requires:
- Minimum 1% spread (to cover fees)
- Sufficient liquidity (>$10k on both sides)
- Fast execution (<500ms)

### Triangular Arbitrage

**Concept:** Trade through 3 pairs to profit from price inefficiencies

**Example:**
```
SOL → Token A (Pump.fun)
Token A → Token B (Raydium)
Token B → SOL (Orca)
```

**Profitability:** Requires:
- 1.5%+ total spread (0.5% per trade)
- High liquidity on all pairs
- Atomic execution (Flash loans or MEV)

### Risk-Adjusted Returns

**Formula:**
```
Expected Profit = (Spread % - Fees % - Slippage %) * Trade Size
Risk = Volatility * Execution Time
Risk-Adjusted Return = Expected Profit / Risk
```

**Realistic Targets:**
- Minimum spread: 1.5%
- Typical fees: 0.6% (0.3% * 2)
- Typical slippage: 0.5%
- **Net profit:** 0.4% (before considering execution risk)

**Conclusion:** Pump.fun arbitrage is **challenging** but **possible** for:
- High-volume tokens (>$100k/day)
- Post-migration phase (Raydium arbitrage)
- Automated bots with <100ms execution

---

## Future Enhancements

### Priority 1: Real-Time Monitoring

**WebSocket Integration:**
```python
# Connect to DexScreener WebSocket (when available)
# Or use Solana WebSocket for on-chain events

import websockets
import asyncio

async def monitor_pumpfun_trades():
    async with websockets.connect('wss://solana-mainnet.websocket') as ws:
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [{
                "mentions": ["6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"]
            }]
        }))

        async for message in ws:
            # Parse trade events in real-time
            process_trade(message)
```

### Priority 2: Trading Execution

**Jupiter Aggregator Integration:**
```python
from jupiter_python_sdk import Jupiter

# Get best swap route
jupiter = Jupiter()
route = jupiter.get_route(
    input_mint="SOL",
    output_mint="TOKEN_MINT",
    amount=1000000,  # 0.001 SOL
    slippage=50  # 0.5%
)

# Execute swap
tx = jupiter.swap(route)
```

### Priority 3: Dashboard Integration

**Add to `multi_coin_dashboard.py`:**
```python
# Add Pump.fun section to dashboard
from src.pump_fun_monitor import PumpFunMonitor

pumpfun_monitor = PumpFunMonitor()

@app.route('/api/pumpfun/trending')
def get_trending():
    tokens = pumpfun_monitor.fetch_trending_pumpfun_tokens()
    return jsonify(tokens)
```

### Priority 4: Advanced Analytics

**Track Token Lifecycle:**
- Monitor new token launches
- Track bonding curve progress
- Alert on migration to Raydium
- Calculate graduation probability

**Smart Filters:**
- Minimum liquidity threshold
- Maximum age (avoid dead tokens)
- Social signals (Twitter mentions, holder count)
- Rug pull detection (LP lock, mint authority)

### Priority 5: Automated Trading Bot

**Components:**
- Strategy engine (when to buy/sell)
- Risk management (position sizing, stop-loss)
- Execution engine (submit transactions)
- Portfolio tracker (P&L, win rate)

**Safety Features:**
- Max drawdown limits
- Whitelist/blacklist tokens
- Emergency stop button
- Audit logs

---

## Appendix

### A. Token Address Examples

Current active Pump.fun tokens (as of Nov 2025):

```python
EXAMPLE_TOKENS = {
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WEN": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",
    "ANALOS": "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn",
}
```

**Note:** Token addresses change. Use DexScreener search to find current active tokens.

### B. Useful Resources

**Official:**
- Pump.fun: https://pump.fun
- Solana Docs: https://docs.solana.com
- Anchor Framework: https://www.anchor-lang.com

**APIs:**
- DexScreener: https://docs.dexscreener.com
- Bitquery: https://docs.bitquery.io
- Moralis: https://docs.moralis.com

**Tools:**
- Solscan (explorer): https://solscan.io
- Birdeye (analytics): https://birdeye.so
- Jupiter (aggregator): https://jup.ag

**Community:**
- Solana Discord: https://discord.gg/solana
- Pump.fun Telegram: https://t.me/pumpfun

### C. Glossary

- **Bonding Curve:** Automated pricing mechanism that increases price as supply decreases
- **DEX:** Decentralized Exchange (no central authority)
- **Graduation:** Token migrating from Pump.fun to Raydium at $69k market cap
- **Liquidity Pool:** Reserve of tokens that enable trading
- **MEV:** Maximal Extractable Value (profit from transaction ordering)
- **PDA:** Program Derived Address (deterministic Solana account address)
- **RPC:** Remote Procedure Call (how to query blockchain data)
- **Slippage:** Price difference between quote and execution
- **SOL:** Native token of Solana blockchain

---

## Support & Contributing

**Issues:**
- Report bugs in the GitHub repository
- Check existing issues before creating new ones

**Contributing:**
- Fork the repository
- Create feature branch
- Submit pull request with tests

**Questions:**
- Check this documentation first
- Search GitHub issues
- Ask in project Discord/Telegram

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0
**Maintainer:** Crypto Bot Team
