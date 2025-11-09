#!/bin/bash
# Quick start script for the Crypto Arbitrage Bot Dashboard

echo "🤖 Crypto Arbitrage Bot - Dashboard Launcher"
echo "=============================================="
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install Flask==3.0.0
    echo ""
fi

# Check if ccxt is installed
if ! python3 -c "import ccxt" 2>/dev/null; then
    echo "⚠️  ccxt not found. Installing all dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "🚀 Starting dashboard..."
echo ""

# Run the dashboard
cd src
python3 dashboard.py
