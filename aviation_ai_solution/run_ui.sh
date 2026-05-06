#!/bin/bash

# ==============================================================================
# Quick Start Script - Launch User Interface
# Designed for ATC Operators (No IT Knowledge Required)
# ==============================================================================

echo "🚀 Starting Aviation AI Solution..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./install.sh first."
    echo "   Or double-click install.sh to install."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH to include the current directory
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Launch the UI with clear instructions
echo "ℹ️  Opening web browser..."
echo "💡 The application will be available at: http://localhost:8501"
echo "⏳ Please wait while the application loads..."
echo ""

# Run Streamlit
streamlit run ui/app.py --server.headless true --server.port 8501

