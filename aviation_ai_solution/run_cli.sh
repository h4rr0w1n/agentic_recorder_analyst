#!/bin/bash

# ==============================================================================
# Quick Start Script - Command Line Interface
# ==============================================================================

echo "🚀 Starting Aviation AI Solution (CLI Mode)..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Launch the CLI with passed arguments
python3 -m aviation_ai_solution.main "$@"
