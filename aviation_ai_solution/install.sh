#!/bin/bash

# ==============================================================================
# Aviation AI Solution - Automated Installation Script
# Designed for ATC Operators and Team Leaders (No IT Knowledge Required)
# ==============================================================================

echo "=========================================="
echo "  Aviation AI Solution Installer"
echo "  Version 1.0.0"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.8 or higher first."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Remove broken virtual environment if it exists
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    echo "🔧 Removing broken virtual environment..."
    rm -rf venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        echo "   Try running: python3 -m venv venv"
        exit 1
    fi
    echo "✅ Virtual environment created."
else
    echo "ℹ️  Virtual environment already exists."
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip using python -m pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies using a minimal set first to save space
echo "📥 Installing core packages (this may take a few minutes)..."

# Install only essential packages for basic functionality
pip install streamlit numpy pandas scikit-learn networkx pyyaml loguru tqdm python-dateutil pytz requests matplotlib plotly pytest --quiet

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Some packages failed to install."
    echo "   You can still use basic features."
fi

# Check if requirements.txt exists and has additional packages
if [ -f "requirements.txt" ]; then
    echo "ℹ️  Note: Full requirements include advanced features."
    echo "   For production use with all features, contact IT support."
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data_lake models output logs
echo "✅ Directories ready."

# Set permissions
chmod +x run_ui.sh 2>/dev/null || true
chmod +x run_cli.sh 2>/dev/null || true

echo ""
echo "=========================================="
echo "  🎉 Installation Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "  1. To start the User Interface (Recommended):"
echo "     Double-click: run_ui.sh"
echo "     Or run: ./run_ui.sh"
echo ""
echo "  2. Or run via Command Line:"
echo "     ./run_cli.sh --help"
echo ""
echo "  3. For detailed instructions, read: USER_MANUAL.md"
echo ""
echo "💡 Tip: The application will open in your web browser."
echo "   Access it at: http://localhost:8501"
echo "=========================================="

