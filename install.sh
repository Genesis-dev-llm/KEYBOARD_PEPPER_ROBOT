#!/bin/bash
# Pepper Control System Installation Script

echo "=========================================="
echo "  🤖 Pepper Control System Installer"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 required!"; exit 1; }

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
    fi
else
    python3 -m venv venv
fi
echo "✓ Virtual environment ready"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || { echo "❌ Failed to activate venv"; exit 1; }
echo "✓ Activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install core dependencies
echo "Installing core dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Core dependencies installed"
else
    echo "❌ Failed to install core dependencies"
    exit 1
fi
echo ""

# Install GUI dependencies (optional)
echo "Installing GUI dependencies..."
read -p "Install GUI support? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    pip install -r requirements_gui.txt
    if [ $? -eq 0 ]; then
        echo "✓ GUI dependencies installed"
    else
        echo "⚠️  GUI installation failed (you can use --no-gui mode)"
    fi
fi
echo ""

# Create directories
echo "Creating directories..."
mkdir -p assets/tablet_images/custom
mkdir -p telemetry
mkdir -p recordings
mkdir -p logs
echo "✓ Directories created"
echo ""

# Check for Pepper IP
if [ -f ".pepper_ip" ]; then
    SAVED_IP=$(cat .pepper_ip)
    echo "Found saved Pepper IP: $SAVED_IP"
else
    read -p "Enter Pepper's IP address (optional, can set later): " PEPPER_IP
    if [ ! -z "$PEPPER_IP" ]; then
        echo "$PEPPER_IP" > .pepper_ip
        echo "✓ IP saved to .pepper_ip"
    fi
fi
echo ""

# Download sample images (optional)
read -p "Download sample tablet images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading samples..."
    # Add actual download commands here
    echo "⚠️  Sample download not yet implemented"
fi
echo ""

# Success message
echo "=========================================="
echo "  ✅ Installation Complete!"
echo "=========================================="
echo ""
echo "To start using Pepper Control:"
echo ""
echo "  1. Activate environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the controller:"
echo "     python test_keyboard_control.py YOUR_PEPPER_IP"
echo ""
echo "  3. Or use GUI:"
echo "     python launch_gui.py YOUR_PEPPER_IP"
echo ""
echo "  4. Or keyboard-only:"
echo "     python test_keyboard_control.py YOUR_PEPPER_IP --no-gui"
echo ""
echo "For help:"
echo "  python test_keyboard_control.py --help"
echo ""
echo "📚 Check README.md for full documentation"
echo "=========================================="