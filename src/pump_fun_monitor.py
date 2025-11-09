#!/usr/bin/env python3
"""
Pump.fun Monitor - Price monitoring for Solana memecoins on Pump.fun
Integrates with existing arbitrage bot infrastructure for DEX monitoring
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import asyncio
from decimal import Decimal, getcontext

# Try importing Solana libraries (optional for enhanced features)
try:
    from solders.pubkey import Pubkey
    from solana.rpc.async_api import AsyncClient
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    # Define placeholder types for type hints
    Pubkey = None
    AsyncClient = None
    print("⚠️  Solana libraries not available. On-chain queries disabled.")
    print("   Install with: pip install -r requirements_dex.txt")


# Configuration
DEXSCREENER_BASE_URL = "https://api.dexscreener.com/latest/dex"
PUMP_PROGRAM_ADDRESS = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
SOLANA_RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
PUMP_CURVE_TOKEN_DECIMALS = 6

# Rate limiting
REQUESTS_PER_MINUTE = 60
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE  # 1 second between requests


class PumpFunMonitor:
    """Monitor Pump.fun token prices and detect arbitrage opportunities"""

    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode
        self.last_request_time = 0
        self.solana_client = None

        if SOLANA_AVAILABLE:
            self.solana_client = AsyncClient(SOLANA_RPC_ENDPOINT)

    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - time_since_last)

        self.last_request_time = time.time()

    def fetch_dexscreener_pairs(self, token_address: str) -> Optional[Dict]:
        """
        Fetch token pair data from DexScreener API

        Args:
            token_address: Solana token mint address

        Returns:
            Dictionary with pair data or None on error
        """
        self._rate_limit()

        try:
            url = f"{DEXSCREENER_BASE_URL}/tokens/{token_address}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"DexScreener API error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error fetching from DexScreener: {e}")
            return None

    def fetch_trending_pumpfun_tokens(self) -> List[Dict]:
        """
        Fetch trending Pump.fun tokens from DexScreener
        Note: This searches for pump.fun pairs on Solana

        Returns:
            List of token dictionaries
        """
        self._rate_limit()

        try:
            # Search for pump.fun tokens
            url = f"{DEXSCREENER_BASE_URL}/search?q=pump.fun"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])

                # Filter for Solana chain and pump.fun
                pumpfun_pairs = [
                    p for p in pairs
                    if p.get('chainId') == 'solana' and
                    'pump' in p.get('dexId', '').lower()
                ]

                return pumpfun_pairs[:20]  # Top 20
            else:
                print(f"DexScreener search error: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error searching DexScreener: {e}")
            return []

    def fetch_token_price_dexscreener(self, token_address: str) -> Optional[Dict]:
        """
        Fetch price for a single token from DexScreener

        Args:
            token_address: Solana token mint address

        Returns:
            Dictionary with price data
        """
        data = self.fetch_dexscreener_pairs(token_address)

        if not data or 'pairs' not in data:
            return None

        pairs = data['pairs']
        if not pairs:
            return None

        # Use first pair (usually highest liquidity)
        pair = pairs[0]

        return {
            'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
            'name': pair.get('baseToken', {}).get('name', 'Unknown'),
            'address': token_address,
            'price_usd': float(pair.get('priceUsd', 0)),
            'price_native': float(pair.get('priceNative', 0)),  # In SOL
            'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
            'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
            'dex': pair.get('dexId', 'unknown'),
            'pair_address': pair.get('pairAddress'),
            'fdv': float(pair.get('fdv', 0)),
            'market_cap': float(pair.get('marketCap', 0)),
            'timestamp': datetime.now().isoformat()
        }

    async def fetch_bonding_curve_price(self, mint_address: str) -> Optional[float]:
        """
        Fetch price directly from Pump.fun bonding curve on-chain
        Requires Solana libraries installed

        Args:
            mint_address: Token mint address

        Returns:
            Price in SOL or None
        """
        if not SOLANA_AVAILABLE or not self.solana_client:
            return None

        try:
            mint_pubkey = Pubkey.from_string(mint_address)
            pump_program = Pubkey.from_string(PUMP_PROGRAM_ADDRESS)

            # Derive bonding curve address
            curve_address = await self._find_pump_curve_address(
                mint_pubkey, pump_program
            )

            # Get curve state
            state = await self._get_pump_curve_state(curve_address)

            if state:
                return self._calculate_pump_curve_price(state)

            return None

        except Exception as e:
            print(f"Error fetching bonding curve: {e}")
            return None

    async def _find_pump_curve_address(
        self,
        mint_address: Pubkey,
        program_address: Pubkey
    ) -> Pubkey:
        """Derive the bonding curve PDA from mint address"""
        seeds = [b"bonding-curve", bytes(mint_address)]
        program_derived_address, _ = Pubkey.find_program_address(
            seeds, program_address
        )
        return program_derived_address

    async def _get_pump_curve_state(self, curve_address: Pubkey) -> Optional[Dict]:
        """Fetch and parse bonding curve account data"""
        import base64

        PUMP_CURVE_STATE_IDENTIFIER = bytes([
            0x17, 0xb7, 0xf8, 0x37, 0x60, 0xd8, 0xac, 0x60
        ])

        try:
            resp = await self.solana_client.get_account_info(curve_address)
            value = resp.value

            if not value or not value.data:
                return None

            # Handle base64-encoded response
            data_raw = value.data
            if isinstance(data_raw, list) and len(data_raw) == 2:
                b64_data = base64.b64decode(data_raw[0])
            elif isinstance(data_raw, str):
                b64_data = base64.b64decode(data_raw)
            else:
                b64_data = data_raw

            # Verify signature
            if b64_data[:8] != PUMP_CURVE_STATE_IDENTIFIER:
                return None

            # Parse reserves as little-endian 64-bit integers
            return {
                "virtualTokenReserves": int.from_bytes(
                    b64_data[0x08:0x10], 'little'
                ),
                "virtualSolReserves": int.from_bytes(
                    b64_data[0x10:0x18], 'little'
                ),
                "realTokenReserves": int.from_bytes(
                    b64_data[0x18:0x20], 'little'
                ),
                "realSolReserves": int.from_bytes(
                    b64_data[0x20:0x28], 'little'
                ),
                "tokenTotalSupply": int.from_bytes(
                    b64_data[0x28:0x30], 'little'
                ),
                "complete": b64_data[0x30] != 0,
            }

        except Exception as e:
            print(f"Error fetching curve state: {e}")
            return None

    def _calculate_pump_curve_price(self, curve_state: Dict) -> Optional[float]:
        """Calculate token price in SOL using bonding curve formula"""
        if not curve_state:
            return None

        getcontext().prec = 18

        virtual_token = Decimal(curve_state["virtualTokenReserves"])
        virtual_sol = Decimal(curve_state["virtualSolReserves"])

        sol_decimals = Decimal(1_000_000_000)  # 9 decimals
        token_factor = Decimal(10 ** PUMP_CURVE_TOKEN_DECIMALS)

        if virtual_token <= 0 or virtual_sol <= 0:
            return None

        # Price formula: (virtual_sol / 1e9) / (virtual_tokens / 1e6)
        price = (virtual_sol / sol_decimals) / (virtual_token / token_factor)
        return float(price)

    def fetch_multiple_tokens(self, token_addresses: List[str]) -> Dict[str, Dict]:
        """
        Fetch prices for multiple tokens

        Args:
            token_addresses: List of token mint addresses

        Returns:
            Dictionary mapping addresses to price data
        """
        results = {}

        for address in token_addresses:
            price_data = self.fetch_token_price_dexscreener(address)
            if price_data:
                results[address] = price_data
            time.sleep(REQUEST_INTERVAL)  # Rate limiting

        return results

    def detect_dex_arbitrage(
        self,
        prices: Dict[str, Dict],
        fee_percent: float = 0.3
    ) -> List[Dict]:
        """
        Detect arbitrage opportunities between DEX pairs
        Note: For Pump.fun, this would compare against Raydium/Orca after migration

        Args:
            prices: Dictionary of token prices from different sources
            fee_percent: Trading fee percentage

        Returns:
            List of arbitrage opportunities
        """
        opportunities = []

        # For DEX arbitrage, we'd compare same token on different DEXs
        # This is simplified - real implementation would need pair addresses
        token_addresses = list(prices.keys())

        for i, addr1 in enumerate(token_addresses):
            for addr2 in token_addresses[i+1:]:
                if prices[addr1] and prices[addr2]:
                    # Check if same token on different DEXs
                    price1 = prices[addr1]['price_usd']
                    price2 = prices[addr2]['price_usd']

                    if price1 and price2 and price1 > 0:
                        gross_profit = ((price2 - price1) / price1) * 100
                        net_profit = gross_profit - (fee_percent * 2)

                        if abs(net_profit) > 0.5:  # Minimum 0.5% profit
                            opportunities.append({
                                'token_1': prices[addr1]['symbol'],
                                'token_2': prices[addr2]['symbol'],
                                'price_1': price1,
                                'price_2': price2,
                                'gross_profit_pct': abs(gross_profit),
                                'net_profit_pct': abs(net_profit),
                                'buy_from': 'lower',
                                'sell_to': 'higher'
                            })

        return sorted(opportunities, key=lambda x: x['net_profit_pct'], reverse=True)


def display_token_data(token_data: Dict):
    """Display token data in formatted table"""
    print("\n" + "="*100)
    print(f"Token: {token_data['name']} ({token_data['symbol']})")
    print("="*100)
    print(f"Address:        {token_data['address']}")
    print(f"Price (USD):    ${token_data['price_usd']:.10f}")
    print(f"Price (SOL):    {token_data['price_native']:.10f} SOL")
    print(f"Liquidity:      ${token_data['liquidity_usd']:,.2f}")
    print(f"24h Volume:     ${token_data['volume_24h']:,.2f}")
    print(f"24h Change:     {token_data['price_change_24h']:.2f}%")
    print(f"Market Cap:     ${token_data['market_cap']:,.0f}")
    print(f"FDV:            ${token_data['fdv']:,.0f}")
    print(f"DEX:            {token_data['dex']}")
    print(f"Pair:           {token_data['pair_address']}")
    print("-"*100)


def display_trending_tokens(tokens: List[Dict]):
    """Display trending tokens in table format"""
    print("\n" + "="*120)
    print("TRENDING PUMP.FUN TOKENS")
    print("="*120)
    print(f"{'#':<4} {'Symbol':<12} {'Price (USD)':<15} {'Price (SOL)':<15} {'24h Vol':<15} {'Liq (USD)':<15}")
    print("-"*120)

    for i, token in enumerate(tokens[:10], 1):
        base = token.get('baseToken', {})
        symbol = base.get('symbol', 'UNKNOWN')
        price_usd = float(token.get('priceUsd', 0))
        price_sol = float(token.get('priceNative', 0))
        volume = float(token.get('volume', {}).get('h24', 0))
        liquidity = float(token.get('liquidity', {}).get('usd', 0))

        print(f"{i:<4} {symbol:<12} ${price_usd:<14.8f} {price_sol:<14.8f} ${volume:<14,.0f} ${liquidity:<14,.0f}")


def main():
    """Main monitoring loop - demonstrates functionality"""
    print("="*100)
    print("🚀 PUMP.FUN MONITOR - Solana Memecoin Price Tracker")
    print("="*100)
    print("\nFeatures:")
    print("  ✓ DexScreener API integration (free, no auth required)")
    print("  ✓ Real-time price monitoring")
    print("  ✓ Trending token discovery")
    print("  ✓ On-chain bonding curve queries (optional)")
    print(f"  ✓ Solana libraries: {'AVAILABLE' if SOLANA_AVAILABLE else 'NOT INSTALLED'}")
    print("="*100)

    monitor = PumpFunMonitor(demo_mode=False)

    # Example token addresses (real Pump.fun tokens)
    # These are examples - replace with current tokens
    EXAMPLE_TOKENS = [
        "GjSn1XHncttWZtx9u6JB9BNM3QYqiumXfGbtkm4ypump",  # Example
        "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
        "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn",  # ANALOS
        "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",  # WEN
    ]

    print("\n📊 Fetching prices for sample tokens...")
    print("(Note: Some tokens may not be found if they've migrated or are inactive)\n")

    try:
        # Fetch multiple token prices
        token_count = 0
        for i, token_address in enumerate(EXAMPLE_TOKENS, 1):
            print(f"\n[{i}/{len(EXAMPLE_TOKENS)}] Fetching {token_address}...")
            token_data = monitor.fetch_token_price_dexscreener(token_address)

            if token_data:
                display_token_data(token_data)
                token_count += 1
            else:
                print(f"  ❌ Token not found or no active pairs")

            time.sleep(1)  # Rate limiting

        print(f"\n✓ Successfully fetched {token_count}/{len(EXAMPLE_TOKENS)} tokens")

        # Fetch trending tokens
        print("\n" + "="*100)
        print("🔥 Fetching trending Pump.fun tokens...")
        trending = monitor.fetch_trending_pumpfun_tokens()

        if trending:
            display_trending_tokens(trending)
            print(f"\n✓ Found {len(trending)} trending tokens")
        else:
            print("❌ No trending tokens found")

        print("\n" + "="*100)
        print("✅ Demo completed successfully!")
        print("\nNOTE: For continuous monitoring, integrate this with multi_coin_dashboard.py")
        print("      or create a dedicated Pump.fun dashboard.")
        print("="*100)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
