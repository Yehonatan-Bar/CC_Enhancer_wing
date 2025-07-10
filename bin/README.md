# Auxiliary Scripts

This directory contains helper scripts and alternative implementations that are not part of the main workflow.

## Contents

### Diagnostic Tools
- `diagnose_claude.py` - Diagnose PATH and environment issues
- `test_claude_automation.sh` - Test all automation methods

### Alternative Implementations
- `run_claude_pexpect.py` - Uses pexpect for terminal control (Linux/Mac)
- `run_claude_fixed.py` - Handles PATH issues automatically
- `run_claude.sh` - Original bash script implementation
- `run_claude_xdotool.sh` - Uses xdotool for keyboard automation

## Usage

These scripts are for troubleshooting or special cases. For normal use, stick to the main scripts in the parent directory:
- `run_claude_wsl.py` (recommended for WSL)
- `run_claude.py` (basic pyautogui version)
- `run_claude_advanced.py` (full-featured with logging)