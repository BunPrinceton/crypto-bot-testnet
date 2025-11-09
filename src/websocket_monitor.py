#!/usr/bin/env python3
"""
WebSocket-based real-time price monitor for cryptocurrency arbitrage detection
Connects to exchange WebSocket APIs for instant price updates with data logging
"""

import asyncio
import json
import csv
import os
from datetime import datetime
from pathlib import Path
import websockets
import aiohttp


class WebSocketPriceMonitor:
    """Real-time price monitor using WebSocket connections"""

    def __init__(self, symbol='BTC/USDT', data_dir='data'):
        self.symbol = symbol
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Convert symbol format for different exchanges
        self.binance_symbol = symbol.replace('/', '').lower()  # btcusdt
        self.kraken_symbol = symbol.replace('/', '').upper()   # BTCUSDT

        # Storage for latest prices
        self.prices = {
            'binance': None,
            'kraken': None,
            'coinbase': None
        }

        # Initialize CSV loggers
        self.setup_logging()

    def setup_logging(self):
        """Set up CSV and JSON logging files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # CSV file for price data
        self.csv_file = self.data_dir / f'prices_{timestamp}.csv'
        self.csv_headers = ['timestamp', 'exchange', 'bid', 'ask', 'last', 'volume']

        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_headers)
            writer.writeheader()

        # JSON file for arbitrage opportunities
        self.json_file = self.data_dir / f'arbitrage_{timestamp}.json'
        self.opportunities_log = []

        print(f"📁 Logging prices to: {self.csv_file}")
        print(f"📁 Logging arbitrage to: {self.json_file}")

    def log_price(self, exchange, bid, ask, last, volume=0):
        """Log price data to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writerow({
                    'timestamp': datetime.now().isoformat(),
                    'exchange': exchange,
                    'bid': bid,
                    'ask': ask,
                    'last': last,
                    'volume': volume
                })
        except Exception as e:
            print(f"Error logging price: {e}")

    def log_arbitrage(self, opportunity):
        """Log arbitrage opportunity to JSON file"""
        try:
            opportunity['timestamp'] = datetime.now().isoformat()
            self.opportunities_log.append(opportunity)

            with open(self.json_file, 'w') as f:
                json.dump(self.opportunities_log, f, indent=2)
        except Exception as e:
            print(f"Error logging arbitrage: {e}")

    async def connect_binance(self):
        """Connect to Binance WebSocket stream"""
        uri = f"wss://stream.binance.com:9443/ws/{self.binance_symbol}@ticker"

        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ Connected to Binance WebSocket")

                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)

                    bid = float(data['b'])
                    ask = float(data['a'])
                    last = float(data['c'])
                    volume = float(data['v'])

                    self.prices['binance'] = {
                        'bid': bid,
                        'ask': ask,
                        'last': last,
                        'volume': volume,
                        'timestamp': datetime.now()
                    }

                    self.log_price('binance', bid, ask, last, volume)

        except Exception as e:
            error_msg = str(e)
            if "451" in error_msg:
                print(f"⚠️  Binance WebSocket unavailable (geo-restricted)")
                print(f"    Continuing with other exchanges...")
            else:
                print(f"❌ Binance WebSocket error: {e}")
            # Don't retry if geo-blocked
            return

    async def connect_kraken(self):
        """Connect to Kraken WebSocket stream"""
        uri = "wss://ws.kraken.com"

        try:
            async with websockets.connect(uri) as websocket:
                # Subscribe to ticker
                subscribe_msg = {
                    "event": "subscribe",
                    "pair": [self.kraken_symbol],
                    "subscription": {"name": "ticker"}
                }
                await websocket.send(json.dumps(subscribe_msg))
                print(f"✅ Connected to Kraken WebSocket")

                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)

                    # Kraken sends various message types
                    if isinstance(data, list) and len(data) >= 2:
                        ticker_data = data[1]
                        if isinstance(ticker_data, dict) and 'b' in ticker_data:
                            bid = float(ticker_data['b'][0])
                            ask = float(ticker_data['a'][0])
                            last = float(ticker_data['c'][0])
                            volume = float(ticker_data['v'][1])  # 24h volume

                            self.prices['kraken'] = {
                                'bid': bid,
                                'ask': ask,
                                'last': last,
                                'volume': volume,
                                'timestamp': datetime.now()
                            }

                            self.log_price('kraken', bid, ask, last, volume)

        except Exception as e:
            print(f"❌ Kraken WebSocket error: {e}")
            await asyncio.sleep(5)

    async def connect_coinbase(self):
        """Connect to Coinbase WebSocket stream"""
        uri = "wss://ws-feed.exchange.coinbase.com"

        # Coinbase uses BTC-USD format
        product_id = self.symbol.replace('/', '-').replace('USDT', 'USD')

        try:
            async with websockets.connect(uri) as websocket:
                # Subscribe to ticker
                subscribe_msg = {
                    "type": "subscribe",
                    "product_ids": [product_id],
                    "channels": ["ticker"]
                }
                await websocket.send(json.dumps(subscribe_msg))
                print(f"✅ Connected to Coinbase WebSocket")

                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)

                    if data.get('type') == 'ticker':
                        bid = float(data.get('best_bid', 0))
                        ask = float(data.get('best_ask', 0))
                        last = float(data.get('price', 0))
                        volume = float(data.get('volume_24h', 0))

                        self.prices['coinbase'] = {
                            'bid': bid,
                            'ask': ask,
                            'last': last,
                            'volume': volume,
                            'timestamp': datetime.now()
                        }

                        self.log_price('coinbase', bid, ask, last, volume)

        except Exception as e:
            print(f"❌ Coinbase WebSocket error: {e}")
            await asyncio.sleep(5)

    def calculate_arbitrage(self, fee_percent=0.1):
        """Calculate potential arbitrage opportunities"""
        opportunities = []

        # Only calculate if we have data from all exchanges
        if not all(self.prices.values()):
            return opportunities

        exchange_names = list(self.prices.keys())

        for i, buy_exchange in enumerate(exchange_names):
            for sell_exchange in exchange_names[i+1:]:
                buy_data = self.prices[buy_exchange]
                sell_data = self.prices[sell_exchange]

                if buy_data and sell_data:
                    buy_price = buy_data['ask']
                    sell_price = sell_data['bid']

                    # Calculate profit percentage after fees
                    gross_profit = ((sell_price - buy_price) / buy_price) * 100
                    fees = fee_percent * 2  # Buy fee + sell fee
                    net_profit = gross_profit - fees

                    if net_profit > 0:
                        opportunity = {
                            'buy_from': buy_exchange,
                            'sell_to': sell_exchange,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'gross_profit_pct': gross_profit,
                            'net_profit_pct': net_profit
                        }
                        opportunities.append(opportunity)
                        self.log_arbitrage(opportunity)

        return opportunities

    def display_prices(self):
        """Display current prices from all exchanges"""
        print("\n" + "="*80)
        print(f"Real-time Prices for {self.symbol} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(f"{'Exchange':<15} {'Bid':<12} {'Ask':<12} {'Last':<12} {'Volume':<15}")
        print("-"*80)

        for exchange, data in self.prices.items():
            if data:
                age = (datetime.now() - data['timestamp']).total_seconds()
                freshness = "🟢" if age < 5 else "🟡" if age < 30 else "🔴"
                print(f"{exchange.capitalize():<15} ${data['bid']:<11.2f} ${data['ask']:<11.2f} ${data['last']:<11.2f} {data['volume']:<14.2f} {freshness}")
            else:
                print(f"{exchange.capitalize():<15} {'WAITING...':>12}")

    def display_opportunities(self, opportunities):
        """Display arbitrage opportunities"""
        if not opportunities:
            print("\nNo arbitrage opportunities detected")
            return

        print("\n" + "="*80)
        print("ARBITRAGE OPPORTUNITIES DETECTED!")
        print("="*80)

        for i, opp in enumerate(opportunities, 1):
            print(f"\nOpportunity #{i}:")
            print(f"  Buy from:  {opp['buy_from']:<15} @ ${opp['buy_price']:.2f}")
            print(f"  Sell to:   {opp['sell_to']:<15} @ ${opp['sell_price']:.2f}")
            print(f"  Gross Profit: {opp['gross_profit_pct']:.3f}%")
            print(f"  Net Profit:   {opp['net_profit_pct']:.3f}%")

    async def monitor_and_display(self, interval=5):
        """Periodically display prices and calculate arbitrage"""
        await asyncio.sleep(3)  # Wait for initial data

        while True:
            self.display_prices()
            opportunities = self.calculate_arbitrage()
            self.display_opportunities(opportunities)
            await asyncio.sleep(interval)

    async def run(self):
        """Start all WebSocket connections and monitoring"""
        print("🤖 Crypto Arbitrage Bot - WebSocket Monitor")
        print("="*80)
        print(f"Monitoring {self.symbol} in real-time")
        print("Press Ctrl+C to stop\n")

        # Start all connections concurrently
        tasks = [
            asyncio.create_task(self.connect_binance()),
            asyncio.create_task(self.connect_kraken()),
            asyncio.create_task(self.connect_coinbase()),
            asyncio.create_task(self.monitor_and_display())
        ]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n\nShutting down gracefully...")
            print(f"Data saved to:")
            print(f"  - {self.csv_file}")
            print(f"  - {self.json_file}")
            print("Thanks for using the Crypto Arbitrage Bot!")


async def main():
    """Main entry point"""
    monitor = WebSocketPriceMonitor(symbol='BTC/USDT', data_dir='data')
    await monitor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
