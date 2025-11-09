# Crypto Arbitrage Bot - Testnet

Multi-platform cryptocurrency arbitrage monitoring system with **three live web dashboards** for real-time analysis.

## 🚀 What's New

✅ **Three live dashboards** for CEX + DEX arbitrage monitoring
✅ **25 cryptocurrencies** tracked across 5 centralized exchanges
✅ **Solana DEX integration** (Pump.fun + Raydium)
✅ **Real arbitrage opportunities** detected (found 0.441% profit on BONK!)
✅ **Slippage analysis** for DEX trades
✅ **Demo mode** for presentations

## Project Overview

Built by Ben & David for David's meeting (Nov 9, 2025 @ 11 AM), this system:
- Monitors real-time cryptocurrency prices across **CEXs and DEXs**
- Detects arbitrage opportunities with net profit calculations
- Provides **three specialized dashboards** for different markets
- Analyzes slippage impact for DEX trades

## 🎯 Three Live Dashboards

### 1. CEX Multi-Coin Dashboard (Port 5001)
- **25 cryptocurrencies** across 5 USA-friendly exchanges
- **Exchanges**: Kraken, Coinbase, Gemini, KuCoin, Bitstamp
- **Features**: Sortable tables, demo mode, real-time arbitrage detection
- **Best for**: High-cap coins on centralized exchanges

### 2. Pump.fun DEX Dashboard (Port 5002)
- **5 Solana tokens**: BONK, WEN, POPCAT, WIF, MEW
- **DEXs**: Orca, Meteora, Raydium, Jupiter
- **Features**: Multi-DEX arbitrage, liquidity tracking, 5-second updates
- **Best for**: Solana memecoin traders

### 3. Raydium DEX Dashboard (Port 5003)
- **10 Raydium pools**: SOL, RAY, JUP, ORCA, WIF, and more
- **Features**: Slippage analysis, CEX comparison, pool health metrics
- **Best for**: Understanding slippage before large DEX trades

📖 **[Complete Dashboard Guide](DASHBOARD_GUIDE.md)**

## Features

- **Multi-Platform Support**: CEX (5 exchanges) + DEX (Solana ecosystem)
- **Real-Time Data**: Live price streaming and updates
- **Arbitrage Detection**: Net profit calculations (accounting for fees)
- **Slippage Analysis**: Calculate impact for different trade sizes
- **Demo Mode**: Simulate opportunities for presentations
- **Zero Setup**: Free APIs, no authentication required

## Tech Stack

- **Language**: Python 3.9+
- **Exchange Library**: CCXT (Cryptocurrency Exchange Trading)
- **Data Processing**: Pandas, NumPy
- **Real-Time**: WebSocket-client
- **Database**: PostgreSQL / MongoDB
- **Caching**: Redis
- **Deployment**: Docker
- **Monitoring**: Grafana / Custom Dashboard

## Sunday Meeting - November 9, 2025 @ 11:00 AM

### Agenda
1. Demo the prototype (15 min)
2. Review architecture and tech stack (15 min)
3. Divide responsibilities (10 min)
4. Set milestone dates and deliverables (10 min)
5. Identify blockers and research needs (10 min)

### Pre-Meeting Goals
- [x] Research and test API connections
- [ ] Build price comparison prototype
- [ ] Test WebSocket connections
- [ ] Document API requirements

## Milestones

### Phase 1: Foundation (Week 1)
- [ ] Set up development environment
- [ ] Create exchange API wrapper classes
- [ ] Implement basic price fetching from 3+ exchanges
- [ ] Build data storage system
- [ ] Create logging framework
- [ ] Set up testnet accounts

### Phase 2: Data Analysis (Week 2)
- [ ] Implement real-time price monitoring (WebSockets)
- [ ] Build arbitrage opportunity detection
- [ ] Calculate fees, slippage, and net profit
- [ ] Create alert system
- [ ] Build visualization dashboard
- [ ] Backtest strategy on historical data

### Phase 3: Trading Logic (Week 3)
- [ ] Implement testnet order placement
- [ ] Build risk management system
- [ ] Create order execution engine
- [ ] Implement transaction tracking
- [ ] Add error handling and retry logic
- [ ] Test full arbitrage cycle

### Phase 4: Optimization (Week 4)
- [ ] Optimize execution speed and latency
- [ ] Implement advanced technical indicators
- [ ] Build comprehensive monitoring dashboard
- [ ] Add performance analytics
- [ ] Stress test with various market conditions
- [ ] Documentation

### Phase 5: Deployment
- [ ] Set up production environment (VPS/cloud)
- [ ] Deploy with Docker
- [ ] Configure monitoring and alerts
- [ ] Run parallel testing
- [ ] Gradual rollout with small positions
- [ ] Continuous optimization

## 📊 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/BunPrinceton/crypto-bot-testnet.git
cd crypto-bot-testnet

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run All Three Dashboards

Open **three separate terminals** and run:

```bash
# Terminal 1: CEX Dashboard (Port 5001)
python src/multi_coin_dashboard.py

# Terminal 2: Pump.fun Dashboard (Port 5002)
python src/pump_fun_dashboard.py

# Terminal 3: Raydium Dashboard (Port 5003)
python src/raydium_dashboard.py
```

Then open in your browser:
- **CEX Dashboard**: http://localhost:5001
- **Pump.fun Dashboard**: http://localhost:5002
- **Raydium Dashboard**: http://localhost:5003

### Quick CLI Examples

```bash
# Monitor Solana tokens (no dashboard)
python examples/pump_fun_basic_example.py

# Detect arbitrage opportunities
python examples/pump_fun_arbitrage_example.py

# Analyze Raydium pools
python src/raydium_monitor.py
```

## Key Challenges

1. **Speed/Latency**: Arbitrage opportunities last seconds - need <500ms execution
2. **Transfer Times**: Crypto transfers take 10-60 min (requires capital on both exchanges)
3. **Fees**: Trading fees ~0.1% per trade, need >0.5% spread to profit
4. **Rate Limits**: Most exchanges limit to 1200 req/min
5. **Slippage**: Displayed price ≠ execution price

## API Documentation

- [CCXT Documentation](https://docs.ccxt.com/)
- [Binance Testnet](https://testnet.binance.vision/)
- [Coinbase Sandbox](https://docs.cloud.coinbase.com/)
- [Python WebSockets](https://websockets.readthedocs.io/)

## Security Notes

- Never commit API keys to git (use .env files)
- Start with testnet only - no real funds
- Keep .env in .gitignore
- Use environment variables for all secrets

## Success Metrics

- Successfully detect arbitrage opportunities in real-time
- Execute complete arbitrage cycle on testnet
- Achieve >60% success rate on profitable trades
- Maintain <500ms average execution latency
- Zero critical errors in 24-hour operation

## Team

- **Ben**: [Role TBD at Sunday meeting]
- **David**: [Role TBD at Sunday meeting]

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Project Timeline

- **Start Date**: November 8, 2025
- **Prototype Demo**: November 9, 2025 @ 11:00 AM
- **Target Deployment**: 4-5 weeks from start

---

**Note**: This is a testnet project for learning and experimentation. No real funds will be used during development.

---

## For Claude Code Instances

**Version Control Guidelines:** See [`.github/VERSION_CONTROL.md`](.github/VERSION_CONTROL.md) for complete versioning guidelines.

### Quick Reference
- **New features**: Always create feature branch (`git checkout -b feature/name`)
- **Feature complete**: Tag working state (`git tag -a v0.X.0 -m "description"`)
- **Before risky changes**: Tag current state as backup
- **Rollback**: `git checkout <tag-name>` to return to working version

### Current Version
Check latest tag: `git describe --tags --abbrev=0`

