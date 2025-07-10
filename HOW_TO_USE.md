# How to Use Claude Terminal Automation

## What It Does
Automatically opens a terminal, navigates to your project folder, runs Claude, and sends your question - all in one command!

## Installation
```bash
# Clone or download the scripts
cd /path/to/code_enhancer

# Set up (only needed once)
./setup.sh
```

## Daily Usage

### 1. Activate Environment
```bash
source venv_cc_enhancer/bin/activate
```

### 2. Run Claude
```bash
python run_claude_wsl.py /your/project/path "What do you want to ask Claude?"
```

## Real Examples

### Ask about current directory
```bash
python run_claude_wsl.py . "Explain what this code does"
```

### Review a specific project
```bash
python run_claude_wsl.py ~/projects/my-app "Find bugs in this code"
```

### Get help with errors
```bash
python run_claude_wsl.py /path/to/code "Help me fix this error: [paste error]"
```

## Options

- `--wait-time 10` - Wait 10 seconds instead of 5
- `--method interactive` - Use if claude command not found
- `--verbose` - See what's happening
- `--keep-open` - Don't close terminal after

## Quick Tips

1. **Use quotes** around your question
2. **Use full paths** or `.` for current directory  
3. **Default wait** is 5 seconds before typing your question
4. **Works best** with Windows Terminal in WSL

## If Something Goes Wrong

```bash
# Check your setup
python bin/diagnose_claude.py

# Try interactive method
python run_claude_wsl.py --method interactive /path "Test"
```