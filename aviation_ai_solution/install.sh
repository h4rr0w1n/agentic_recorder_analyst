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
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
    echo "✅ Virtual environment created."
else
    echo "ℹ️  Virtual environment already exists."
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing required packages (this may take a few minutes)..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        exit 1
    fi
    echo "✅ Dependencies installed successfully."
else
    echo "⚠️  requirements.txt not found. Skipping dependency installation."
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
echo "     ./run_ui.sh"
echo ""
echo "  2. Or run via Command Line:"
echo "     ./run_cli.sh --help"
echo ""
echo "  3. For detailed instructions, read: USER_MANUAL.md"
echo ""
echo "=========================================="
