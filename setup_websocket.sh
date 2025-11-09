#!/bin/bash
# Quick setup script for WebSocket monitor demo

echo "=================================="
echo "WebSocket Monitor - Quick Setup"
echo "=================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Installing dependencies..."
./venv/bin/pip install -q websockets aiohttp
echo "✓ Dependencies installed"

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "To run the WebSocket monitor:"
echo "  ./venv/bin/python run_websocket_monitor.py"
echo ""
echo "Or activate the virtual environment first:"
echo "  source venv/bin/activate"
echo "  python run_websocket_monitor.py"
echo ""
