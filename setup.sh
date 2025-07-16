#!/bin/bash

echo "Claude Terminal Automation Setup"
echo "================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [ $? -eq 0 ]; then
    echo "✓ Found: $python_version"
else
    echo "✗ Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv_cc_enhancer" ]; then
    echo "✓ Virtual environment 'venv_cc_enhancer' already exists"
else
    echo "Creating virtual environment..."
    python3 -m venv venv_cc_enhancer
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv_cc_enhancer/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_claude.py
chmod +x run_claude_pexpect.py
chmod +x run_claude_advanced.py
echo "✓ Scripts are now executable"

# Platform-specific checks
platform=$(uname -s)
echo ""
echo "Platform detected: $platform"

if [ "$platform" = "Linux" ]; then
    echo "Checking Linux dependencies..."
    
    # Check for terminal emulators
    for term in gnome-terminal konsole xterm; do
        if command -v $term &> /dev/null; then
            echo "✓ Found terminal: $term"
            break
        fi
    done
    
    # Check for X11 libraries
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "⚠ tkinter not found. Install with: sudo apt-get install python3-tk"
    fi
    
elif [ "$platform" = "Darwin" ]; then
    echo "✓ macOS detected - Terminal.app will be used"
    echo "⚠ Make sure to grant accessibility permissions to Terminal/Python"
    
else
    echo "⚠ Windows users: Run scripts with Python directly"
fi

# Create example config
if [ ! -f "config.json" ]; then
    echo ""
    echo "Creating example configuration file..."
    cat > config.json << 'EOF'
{
    "terminal_spawn_delay": 2,
    "claude_wait_time": 5,
    "failsafe": false,
    "terminal_preferences": {
        "linux": ["gnome-terminal", "konsole", "xterm"],
        "darwin": ["Terminal"],
        "windows": ["cmd", "powershell"]
    },
    "keyboard_delay": 0.1
}
EOF
    echo "✓ Created config.json"
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "To use the scripts:"
echo "1. Activate the virtual environment:"
echo "   source venv_cc_enhancer/bin/activate"
echo ""
echo "2. Run a script:"
echo "   python run_claude.py /path/to/project \"Your command\""
echo ""
echo "See README_claude_automation.md for detailed usage instructions."