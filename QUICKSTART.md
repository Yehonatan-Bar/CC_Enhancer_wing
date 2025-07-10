# Quick Start Guide

## Setup (One Time)
```bash
# 1. Run setup script
./setup.sh

# 2. Activate virtual environment
source venv_cc_enhancer/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### For WSL Users (Recommended)
```bash
# Run claude with your input
python run_claude_wsl.py /path/to/project "Your command here"

# Example
python run_claude_wsl.py /home/user/myproject "Tell me about this code"
```

### If you get "claude: command not found"
```bash
# Use interactive method
python run_claude_wsl.py --method interactive /path/to/project "Your command"
```

## Common Examples

```bash
# Ask claude to analyze current directory
python run_claude_wsl.py . "What does this project do?"

# Review code in specific directory
python run_claude_wsl.py ~/projects/myapp "Review this code for security issues"

# With custom wait time (default is 5 seconds)
python run_claude_wsl.py --wait-time 10 /path "Complex question here"

# Keep terminal open after execution
python run_claude_wsl.py --keep-open /path "Debug this error"
```

## Troubleshooting

If it doesn't work:
```bash
# Run diagnostic
python bin/diagnose_claude.py

# Use verbose mode to see what's happening
python run_claude_wsl.py --verbose /path "Test"
```

That's it! The script will:
1. Open Windows Terminal at your specified directory
2. Wait 5 seconds
3. Type your command to Claude
4. Press Enter