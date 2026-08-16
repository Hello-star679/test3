#!/bin/bash
# Start the Adversarial Test Framework GUI
# Requires: Python 3.8+, Streamlit, and dependencies

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if dependencies are installed
echo "🔍 Checking dependencies..."

if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip install --break-system-packages streamlit plotly pandas 2>/dev/null
fi

if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "📦 Installing python-dotenv..."
    pip install --break-system-packages python-dotenv 2>/dev/null
fi

# Start GUI
echo ""
echo "🚀 Starting Adversarial Test Framework GUI..."
echo ""
echo "📍 Access the GUI at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$SCRIPT_DIR"
STREAMLIT_SERVER_HEADLESS=true streamlit run gui.py --logger.level=error
