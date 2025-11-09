#!/usr/bin/env python3
"""
Quick start script for the WebSocket price monitor
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from websocket_monitor import main
import asyncio

if __name__ == "__main__":
    print("Starting WebSocket Price Monitor...")
    print("="*80)
    asyncio.run(main())
