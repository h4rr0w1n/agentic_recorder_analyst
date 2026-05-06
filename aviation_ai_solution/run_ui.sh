#!/bin/bash

# ==============================================================================
# Quick Start Script - Launch User Interface
# ==============================================================================

echo "🚀 Starting Aviation AI Solution..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Launch the UI
python3 -m aviation_ai_solution.ui.app
