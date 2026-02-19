#!/bin/bash
# Setup script for SharePoint File Automation

echo "SharePoint File Automation - Setup"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed"
echo ""

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your SharePoint credentials"
else
    echo ".env file already exists"
fi
echo ""

# Create directories
echo "Creating required directories..."
mkdir -p downloaded_files
mkdir -p logs
echo "Directories created"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your SharePoint credentials"
echo "2. Review and customize config.yaml"
echo "3. Run: python main.py"
echo ""
