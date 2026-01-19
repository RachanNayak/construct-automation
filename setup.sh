#!/bin/bash

# CONSTRUCT Login Automation - Quick Start Script

echo "========================================"
echo "CONSTRUCT Login Automation Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

echo "✓ Python3 found"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✓ pip found"

# Install requirements
echo ""
echo "Installing Python packages..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Install playwright browser
echo ""
echo "Installing Playwright browser..."
python3 -m playwright install chromium

if [ $? -eq 0 ]; then
    echo "✓ Playwright browser installed"
else
    echo "❌ Failed to install Playwright browser"
    exit 1
fi

echo ""
echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""
echo "To run tests:"
echo "  pytest tests/test_login.py -v"
echo ""
echo "To run with details:"
echo "  pytest tests/test_login.py -v -s"
echo ""
