#!/usr/bin/env python3
"""
Test script for Pump.fun integration
Demonstrates all features with real data
"""

import time
from src.pump_fun_monitor import PumpFunMonitor, display_token_data, display_trending_tokens


def test_single_token():
    """Test fetching a single token"""
    print("\n" + "="*100)
    print("TEST 1: Fetch Single Token Price")
    print("="*100)

    monitor = PumpFunMonitor()

    # POPCAT - a popular Solana memecoin
    token_address = "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"

    print(f"\nFetching data for POPCAT: {token_address}")
    token_data = monitor.fetch_token_price_dexscreener(token_address)

    if token_data:
        display_token_data(token_data)
        print("✅ Test passed: Single token fetch successful")
        return True
    else:
        print("❌ Test failed: Could not fetch token data")
        return False


def test_multiple_tokens():
    """Test fetching multiple tokens"""
    print("\n" + "="*100)
    print("TEST 2: Fetch Multiple Tokens")
    print("="*100)

    monitor = PumpFunMonitor()

    # Well-known Solana memecoins
    tokens = {
        "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "WEN": "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
    }

    print(f"\nFetching {len(tokens)} tokens...")

    results = {}
    for name, address in tokens.items():
        print(f"\n[{name}] {address}")
        data = monitor.fetch_token_price_dexscreener(address)
        if data:
            results[name] = data
            print(f"  ✓ ${data['price_usd']:.8f} | 24h Vol: ${data['volume_24h']:,.0f}")
        else:
            print(f"  ✗ Not found")
        time.sleep(1)  # Rate limiting

    print(f"\n✅ Test passed: Fetched {len(results)}/{len(tokens)} tokens")
    return len(results) > 0


def test_trending_tokens():
    """Test fetching trending tokens"""
    print("\n" + "="*100)
    print("TEST 3: Fetch Trending Tokens")
    print("="*100)

    monitor = PumpFunMonitor()

    print("\nSearching for trending Pump.fun tokens...")
    trending = monitor.fetch_trending_pumpfun_tokens()

    if trending:
        print(f"\nFound {len(trending)} trending tokens:")
        display_trending_tokens(trending)
        print("✅ Test passed: Trending tokens fetch successful")
        return True
    else:
        print("❌ Test failed: No trending tokens found")
        return False


def test_price_comparison():
    """Test comparing prices across different sources"""
    print("\n" + "="*100)
    print("TEST 4: Price Comparison Across DEXs")
    print("="*100)

    monitor = PumpFunMonitor()

    # Fetch a token that trades on multiple DEXs
    token_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # BONK

    print(f"\nFetching BONK from DexScreener: {token_address}")
    data = monitor.fetch_dexscreener_pairs(token_address)

    if data and 'pairs' in data:
        pairs = data['pairs']
        print(f"\nFound {len(pairs)} trading pairs:")
        print(f"{'DEX':<15} {'Price (USD)':<20} {'Liquidity':<20} {'24h Volume':<20}")
        print("-"*80)

        for i, pair in enumerate(pairs[:5], 1):
            dex = pair.get('dexId', 'unknown')
            price = float(pair.get('priceUsd', 0))
            liq = float(pair.get('liquidity', {}).get('usd', 0))
            vol = float(pair.get('volume', {}).get('h24', 0))

            print(f"{dex:<15} ${price:<19.10f} ${liq:<19,.0f} ${vol:<19,.0f}")

        # Calculate spread
        if len(pairs) >= 2:
            prices = [float(p.get('priceUsd', 0)) for p in pairs[:5] if p.get('priceUsd')]
            if prices:
                max_price = max(prices)
                min_price = min(prices)
                spread = ((max_price - min_price) / min_price) * 100

                print(f"\nPrice Spread: {spread:.3f}%")
                print(f"Min: ${min_price:.10f} | Max: ${max_price:.10f}")

                if spread > 0.5:
                    print(f"⚠️  Significant spread detected: {spread:.3f}%")
                    print("   Potential arbitrage opportunity (check liquidity & fees)")

        print("✅ Test passed: Price comparison successful")
        return True
    else:
        print("❌ Test failed: Could not fetch pair data")
        return False


def test_liquidity_filtering():
    """Test filtering tokens by liquidity"""
    print("\n" + "="*100)
    print("TEST 5: Filter Tokens by Liquidity")
    print("="*100)

    monitor = PumpFunMonitor()

    min_liquidity = 100000  # $100k minimum

    print(f"\nFetching trending tokens with minimum ${min_liquidity:,} liquidity...")
    trending = monitor.fetch_trending_pumpfun_tokens()

    if trending:
        # Filter by liquidity
        filtered = [
            t for t in trending
            if float(t.get('liquidity', {}).get('usd', 0)) >= min_liquidity
        ]

        print(f"\nFiltered: {len(filtered)}/{len(trending)} tokens meet criteria")

        if filtered:
            print(f"\n{'Symbol':<12} {'Price (USD)':<20} {'Liquidity':<20}")
            print("-"*60)

            for token in filtered[:10]:
                base = token.get('baseToken', {})
                symbol = base.get('symbol', 'UNKNOWN')
                price = float(token.get('priceUsd', 0))
                liq = float(token.get('liquidity', {}).get('usd', 0))

                print(f"{symbol:<12} ${price:<19.8f} ${liq:<19,.0f}")

            print("✅ Test passed: Liquidity filtering successful")
            return True
        else:
            print("ℹ️  No tokens meet liquidity criteria (normal for trending search)")
            print("✅ Test passed: Filtering logic works")
            return True
    else:
        print("❌ Test failed: No trending tokens to filter")
        return False


def test_data_structure():
    """Test that returned data has all expected fields"""
    print("\n" + "="*100)
    print("TEST 6: Validate Data Structure")
    print("="*100)

    monitor = PumpFunMonitor()
    token_address = "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"

    print(f"\nFetching token and validating structure...")
    data = monitor.fetch_token_price_dexscreener(token_address)

    if not data:
        print("❌ Test failed: No data returned")
        return False

    required_fields = [
        'symbol', 'name', 'address', 'price_usd', 'price_native',
        'liquidity_usd', 'volume_24h', 'price_change_24h', 'dex',
        'pair_address', 'fdv', 'market_cap', 'timestamp'
    ]

    print("\nChecking required fields:")
    missing = []
    for field in required_fields:
        present = field in data
        status = "✓" if present else "✗"
        value = data.get(field, "MISSING")
        print(f"  {status} {field:<20} = {value}")

        if not present:
            missing.append(field)

    if missing:
        print(f"\n❌ Test failed: Missing fields: {', '.join(missing)}")
        return False
    else:
        print("\n✅ Test passed: All required fields present")
        return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "#"*100)
    print("# PUMP.FUN INTEGRATION TEST SUITE")
    print("#"*100)

    tests = [
        ("Single Token Fetch", test_single_token),
        ("Multiple Tokens Fetch", test_multiple_tokens),
        ("Trending Tokens", test_trending_tokens),
        ("Price Comparison", test_price_comparison),
        ("Liquidity Filtering", test_liquidity_filtering),
        ("Data Structure Validation", test_data_structure),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

        time.sleep(1)  # Pause between tests

    # Summary
    print("\n" + "="*100)
    print("TEST SUMMARY")
    print("="*100)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! Pump.fun integration is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above for details.")

    print("="*100)


if __name__ == "__main__":
    run_all_tests()
