#!/usr/bin/env python3
"""
Quick test script to verify WebSocket connections work
Runs for 15 seconds then exits
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from websocket_monitor import WebSocketPriceMonitor


async def test_monitor():
    """Run monitor for 15 seconds to test connections"""
    monitor = WebSocketPriceMonitor(symbol='BTC/USDT', data_dir='data')

    print("Starting WebSocket monitor test...")
    print("Will run for 15 seconds to verify connections\n")

    # Start all connections
    tasks = [
        asyncio.create_task(monitor.connect_binance()),
        asyncio.create_task(monitor.connect_kraken()),
        asyncio.create_task(monitor.connect_coinbase()),
        asyncio.create_task(monitor.monitor_and_display())
    ]

    try:
        # Run for 15 seconds
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=15)
    except asyncio.TimeoutError:
        print("\n\nTest completed!")
        print(f"Data logged to:")
        print(f"  - {monitor.csv_file}")
        print(f"  - {monitor.json_file}")

        # Check if we got data
        if any(monitor.prices.values()):
            print("\nWebSocket connections working!")
            for exchange, data in monitor.prices.items():
                if data:
                    print(f"  {exchange}: Last price ${data['last']:.2f}")
        else:
            print("\nWarning: No data received from exchanges")


if __name__ == "__main__":
    asyncio.run(test_monitor())
