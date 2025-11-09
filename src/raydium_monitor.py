#!/usr/bin/env python3
"""
Raydium DEX Monitor for Arbitrage Detection
Monitors Raydium liquidity pools and detects arbitrage opportunities vs CEX
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


class RaydiumMonitor:
    """
    Monitor Raydium DEX pools for price data and arbitrage opportunities
    """

    # Major DEX pool addresses (using token address method - works across DEXs)
    # These use token mints, not specific pool IDs
    MAJOR_TOKENS = {
        'SOL': 'So11111111111111111111111111111111111111112',
        'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        'USDT': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
        'RAY': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
        'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
        'JUP': 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',
        'ORCA': 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE',
        'PYTH': 'HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3',
        'JTO': 'jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL',
        'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
    }

    # Verified pool addresses from DexScreener
    MAJOR_POOLS = {
        'SOL/USDC': {
            'pool_id': 'Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE',  # Orca - highest liquidity
            'base_token': 'So11111111111111111111111111111111111111112',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'orca'
        },
        'SOL/USDT': {
            'pool_id': '3nMFwZXwY1s1M5s8vYAHqd4wGs4iSxXE4LRoUMMYqEgF',  # Raydium CLMM
            'base_token': 'So11111111111111111111111111111111111111112',
            'quote_token': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
            'dex': 'raydium'
        },
        'RAY/USDC': {
            'pool_id': '6UmmUiYoBjSrhakAobJw8BvkmJtDVxaeBtbt7rxWo1mg',
            'base_token': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'raydium'
        },
        'RAY/SOL': {
            'pool_id': 'AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA',
            'base_token': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
            'quote_token': 'So11111111111111111111111111111111111111112',
            'dex': 'raydium'
        },
        'BONK/USDC': {
            'pool_id': 'Hs97TCZeuYiJxooo3U73qEHXg3dKpRL4uYKYRryEK9CF',
            'base_token': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'raydium'
        },
        'JUP/USDC': {
            'pool_id': '2QdhepnKRTLjjSqPL1PtKNwqrUkoLee5Gqs8bvZhRdMv',
            'base_token': 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'raydium'
        },
        'ORCA/USDC': {
            'pool_id': '2p7nYbtPBgtmY69NsE8DAW6szpRJn7tQvDnqvoEWQvjY',
            'base_token': 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'orca'
        },
        'PYTH/USDC': {
            'pool_id': 'AujrCjx8bAUMvVT9EUjjcPGf8vqk8AJLp5U5nH5vgSU',
            'base_token': 'HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'raydium'
        },
        'JTO/USDC': {
            'pool_id': 'D8wAxwpH2aKaEGBKfeGdnQbCc2s54NrRvTDXCK98VAeT',
            'base_token': 'jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'raydium'
        },
        'WIF/USDC': {
            'pool_id': 'EP2ib6dYdEeqD8MfE2ezHCxX3kP3K2eLKkirfPm5eyMx',
            'base_token': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
            'quote_token': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'dex': 'raydium'
        },
    }

    # Raydium swap fee
    RAYDIUM_FEE_PERCENT = 0.25

    # Solana transaction fee (approximate in SOL)
    SOLANA_TX_FEE_SOL = 0.000005

    # DexScreener API
    DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"

    # Jupiter API for price quotes
    JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"

    def __init__(self, data_dir: str = "data"):
        """Initialize the Raydium monitor"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RaydiumMonitor/1.0',
            'Accept': 'application/json'
        })

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.21  # ~300 requests per minute = 0.2s per request

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def fetch_pool_data(self, pool_id: str, symbol: str) -> Optional[Dict]:
        """
        Fetch pool data from DexScreener API

        Args:
            pool_id: Raydium pool ID
            symbol: Trading pair symbol (e.g., 'SOL/USDC')

        Returns:
            Pool data dictionary or None if error
        """
        self._rate_limit()

        try:
            url = f"{self.DEXSCREENER_API}/pairs/solana/{pool_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data or 'pair' not in data:
                print(f"  Warning: No pair data for {symbol}")
                return None

            pair = data['pair']

            if pair is None:
                print(f"  Warning: Pair is None for {symbol}")
                return None

            # Extract relevant data
            pool_info = {
                'symbol': symbol,
                'pool_id': pool_id,
                'price_usd': float(pair.get('priceUsd', 0)),
                'price_native': float(pair.get('priceNative', 0)),
                'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0)),
                'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                'txns_24h_buys': int(pair.get('txns', {}).get('h24', {}).get('buys', 0)),
                'txns_24h_sells': int(pair.get('txns', {}).get('h24', {}).get('sells', 0)),
                'fdv': float(pair.get('fdv', 0)),
                'market_cap': float(pair.get('marketCap', 0)),
                'timestamp': datetime.now().isoformat(),
                'dex': pair.get('dexId', 'raydium'),
            }

            return pool_info

        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {symbol}: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"  Error parsing {symbol} data: {e}")
            return None

    def fetch_all_pools(self) -> Dict[str, Dict]:
        """
        Fetch data for all major pools

        Returns:
            Dictionary of pool data keyed by symbol
        """
        print(f"\nFetching Raydium pool data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        pools_data = {}

        for symbol, pool_config in self.MAJOR_POOLS.items():
            pool_id = pool_config['pool_id']
            data = self.fetch_pool_data(pool_id, symbol)

            if data:
                pools_data[symbol] = data
                print(f"  {symbol:<12} ${data['price_usd']:<12.6f} Liquidity: ${data['liquidity_usd']:>12,.0f}")
            else:
                print(f"  {symbol:<12} ERROR")

        return pools_data

    def calculate_slippage(self, liquidity_usd: float, trade_size_usd: float) -> float:
        """
        Calculate approximate slippage for a trade
        Uses constant product AMM formula approximation

        Args:
            liquidity_usd: Total liquidity in pool (USD)
            trade_size_usd: Trade size (USD)

        Returns:
            Estimated slippage percentage
        """
        if liquidity_usd <= 0:
            return 100.0  # Infinite slippage

        # Simplified slippage estimation: sqrt(1 + trade_size/liquidity) - 1
        # More accurate would require actual pool reserves
        k_ratio = trade_size_usd / liquidity_usd

        if k_ratio >= 1:
            return 100.0  # Trade too large

        # Approximate price impact using constant product formula
        slippage_pct = (k_ratio / (2 * (1 - k_ratio))) * 100

        return min(slippage_pct, 100.0)

    def calculate_effective_price(self, base_price: float, slippage_pct: float,
                                  fee_pct: float, is_buy: bool) -> float:
        """
        Calculate effective price after slippage and fees

        Args:
            base_price: Base pool price
            slippage_pct: Slippage percentage
            fee_pct: Fee percentage
            is_buy: True if buying, False if selling

        Returns:
            Effective price
        """
        if is_buy:
            # Buying: price increases with slippage, plus fees
            return base_price * (1 + slippage_pct/100) * (1 + fee_pct/100)
        else:
            # Selling: price decreases with slippage, minus fees
            return base_price * (1 - slippage_pct/100) * (1 - fee_pct/100)

    def display_pools_table(self, pools_data: Dict[str, Dict]):
        """Display pools in a formatted table"""
        print("\n" + "="*120)
        print("RAYDIUM POOLS SNAPSHOT")
        print("="*120)
        print(f"{'Symbol':<12} {'Price (USD)':<15} {'24h Change':<12} {'Liquidity':<15} {'24h Volume':<15} {'24h Txns':<10}")
        print("-"*120)

        for symbol, data in sorted(pools_data.items()):
            change_str = f"{data['price_change_24h']:+.2f}%"
            txns = data['txns_24h_buys'] + data['txns_24h_sells']

            print(f"{symbol:<12} ${data['price_usd']:<14.6f} {change_str:<12} "
                  f"${data['liquidity_usd']:>13,.0f} ${data['volume_24h']:>13,.0f} {txns:>9,}")

    def compare_with_cex(self, pools_data: Dict[str, Dict], cex_prices: Dict[str, float],
                        trade_size_usd: float = 1000) -> List[Dict]:
        """
        Compare Raydium prices with CEX prices to find arbitrage

        Args:
            pools_data: Raydium pool data
            cex_prices: CEX prices dict {symbol: price}
            trade_size_usd: Trade size for slippage calculation

        Returns:
            List of arbitrage opportunities
        """
        opportunities = []

        for symbol, pool_data in pools_data.items():
            # Convert symbol format: SOL/USDC -> SOL/USDT for CEX comparison
            # Most CEXs use USDT, so we approximate USDC = USDT
            cex_symbol = symbol.replace('/USDC', '/USDT')

            if cex_symbol not in cex_prices:
                continue

            cex_price = cex_prices[cex_symbol]
            dex_price = pool_data['price_usd']
            liquidity = pool_data['liquidity_usd']

            # Calculate slippage for trade size
            slippage = self.calculate_slippage(liquidity, trade_size_usd)

            if slippage >= 5.0:  # Skip if slippage too high
                continue

            # Scenario 1: Buy on DEX, sell on CEX
            dex_buy_price = self.calculate_effective_price(
                dex_price, slippage, self.RAYDIUM_FEE_PERCENT, is_buy=True
            )
            cex_sell_price = cex_price * 0.999  # Assume 0.1% CEX fee

            gross_profit_1 = ((cex_sell_price - dex_buy_price) / dex_buy_price) * 100

            # Scenario 2: Buy on CEX, sell on DEX
            cex_buy_price = cex_price * 1.001  # Assume 0.1% CEX fee
            dex_sell_price = self.calculate_effective_price(
                dex_price, slippage, self.RAYDIUM_FEE_PERCENT, is_buy=False
            )

            gross_profit_2 = ((dex_sell_price - cex_buy_price) / cex_buy_price) * 100

            # Take the better opportunity
            if gross_profit_1 > 0.1 or gross_profit_2 > 0.1:
                if gross_profit_1 > gross_profit_2:
                    opportunities.append({
                        'symbol': symbol,
                        'direction': 'DEX→CEX',
                        'buy_venue': f'Raydium',
                        'sell_venue': 'CEX',
                        'buy_price': dex_buy_price,
                        'sell_price': cex_sell_price,
                        'gross_profit_pct': gross_profit_1,
                        'slippage_pct': slippage,
                        'liquidity_usd': liquidity,
                        'trade_size_usd': trade_size_usd,
                    })
                else:
                    opportunities.append({
                        'symbol': symbol,
                        'direction': 'CEX→DEX',
                        'buy_venue': 'CEX',
                        'sell_venue': 'Raydium',
                        'buy_price': cex_buy_price,
                        'sell_price': dex_sell_price,
                        'gross_profit_pct': gross_profit_2,
                        'slippage_pct': slippage,
                        'liquidity_usd': liquidity,
                        'trade_size_usd': trade_size_usd,
                    })

        return sorted(opportunities, key=lambda x: x['gross_profit_pct'], reverse=True)

    def detect_triangle_arbitrage(self, pools_data: Dict[str, Dict]) -> List[Dict]:
        """
        Detect triangle arbitrage opportunities on Raydium
        Example: SOL → USDC → RAY → SOL

        Args:
            pools_data: Raydium pool data

        Returns:
            List of triangle arbitrage opportunities
        """
        opportunities = []

        # Define common triangle paths
        triangles = [
            {
                'path': ['SOL/USDC', 'RAY/USDC', 'RAY/SOL'],
                'route': 'SOL → USDC → RAY → SOL',
                'start': 'SOL'
            },
            {
                'path': ['SOL/USDC', 'JUP/USDC', 'SOL/USDC'],  # Simplified, would need JUP/SOL
                'route': 'SOL → USDC → JUP → SOL',
                'start': 'SOL'
            },
        ]

        for triangle in triangles:
            # Check if all pairs exist
            if not all(pair in pools_data for pair in triangle['path']):
                continue

            # Simple triangle calculation (rough estimate)
            # In reality, you'd need to track exact token amounts through each hop

            start_amount = 1.0  # Start with 1 unit
            final_amount = start_amount

            # Apply each leg of the triangle
            for i, pair_symbol in enumerate(triangle['path']):
                pool = pools_data[pair_symbol]
                price = pool['price_usd']

                # Apply fees
                final_amount *= (1 - self.RAYDIUM_FEE_PERCENT / 100)

            # Calculate profit
            profit_pct = ((final_amount - start_amount) / start_amount) * 100

            if profit_pct > 0.1:
                opportunities.append({
                    'type': 'triangle',
                    'route': triangle['route'],
                    'path': triangle['path'],
                    'profit_pct': profit_pct,
                    'start_token': triangle['start']
                })

        return opportunities

    def display_arbitrage_opportunities(self, opportunities: List[Dict]):
        """Display arbitrage opportunities"""
        if not opportunities:
            print("\nNo profitable arbitrage opportunities found")
            return

        print("\n" + "="*120)
        print(f"ARBITRAGE OPPORTUNITIES DETECTED ({len(opportunities)} total)")
        print("="*120)

        for i, opp in enumerate(opportunities, 1):
            print(f"\nOpportunity #{i}: {opp['symbol']} ({opp['direction']})")
            print(f"  Route: {opp['buy_venue']} → {opp['sell_venue']}")
            print(f"  Buy Price:  ${opp['buy_price']:.6f}")
            print(f"  Sell Price: ${opp['sell_price']:.6f}")
            print(f"  Gross Profit: {opp['gross_profit_pct']:.3f}%")
            print(f"  Slippage: {opp['slippage_pct']:.2f}%")
            print(f"  Trade Size: ${opp['trade_size_usd']:,.0f}")
            print(f"  Liquidity: ${opp['liquidity_usd']:,.0f}")

    def save_snapshot(self, pools_data: Dict[str, Dict], filename: str = None):
        """Save pool data snapshot to file"""
        if filename is None:
            filename = f"raydium_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.data_dir / filename

        with open(filepath, 'w') as f:
            json.dump(pools_data, f, indent=2)

        print(f"\nSnapshot saved to {filepath}")


def demo_monitor():
    """Demo function showing Raydium monitor capabilities"""
    print("="*120)
    print("RAYDIUM DEX MONITOR - DEMO")
    print("="*120)

    monitor = RaydiumMonitor()

    # Fetch pool data
    pools_data = monitor.fetch_all_pools()

    if not pools_data:
        print("\nError: Could not fetch pool data")
        return

    # Display pools table
    monitor.display_pools_table(pools_data)

    # Simulate CEX prices (in real use, fetch from CCXT)
    # Using approximate prices for demo
    cex_prices = {
        'SOL/USDT': pools_data.get('SOL/USDC', {}).get('price_usd', 0) * 1.002,  # CEX slightly higher
        'RAY/USDT': pools_data.get('RAY/USDC', {}).get('price_usd', 0) * 0.998,  # DEX slightly higher
    }

    # Find arbitrage opportunities
    print("\n" + "="*120)
    print("COMPARING WITH CEX PRICES")
    print("="*120)

    for symbol, price in cex_prices.items():
        print(f"  {symbol}: ${price:.6f}")

    opportunities = monitor.compare_with_cex(pools_data, cex_prices, trade_size_usd=1000)
    monitor.display_arbitrage_opportunities(opportunities)

    # Slippage analysis
    print("\n" + "="*120)
    print("SLIPPAGE ANALYSIS (for different trade sizes)")
    print("="*120)

    trade_sizes = [100, 1000, 5000, 10000, 50000]

    for symbol, data in list(pools_data.items())[:3]:  # Show for first 3 pairs
        print(f"\n{symbol} (Liquidity: ${data['liquidity_usd']:,.0f})")
        print(f"  Trade Size    Slippage    Effective Buy Price    Effective Sell Price")
        print(f"  {'-'*75}")

        for size in trade_sizes:
            slippage = monitor.calculate_slippage(data['liquidity_usd'], size)
            buy_price = monitor.calculate_effective_price(
                data['price_usd'], slippage, monitor.RAYDIUM_FEE_PERCENT, is_buy=True
            )
            sell_price = monitor.calculate_effective_price(
                data['price_usd'], slippage, monitor.RAYDIUM_FEE_PERCENT, is_buy=False
            )
            print(f"  ${size:>7,}      {slippage:>5.2f}%      ${buy_price:<18.6f}   ${sell_price:<18.6f}")

    # Save snapshot
    monitor.save_snapshot(pools_data)

    print("\n" + "="*120)
    print("Demo complete!")
    print("="*120)


if __name__ == "__main__":
    demo_monitor()
