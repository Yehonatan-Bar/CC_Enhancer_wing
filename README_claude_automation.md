# Claude Terminal Automation Scripts

This repository contains Python scripts to automate running the Claude CLI with automatic input in a new terminal window.

## Setup

### 1. Create and activate virtual environment

```bash
# Virtual environment already created as venv_cc_enhancer
source venv_cc_enhancer/bin/activate  # On Linux/Mac
# OR
venv_cc_enhancer\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Available Scripts

### 1. `run_claude_wsl.py` - WSL-Optimized Script (Recommended for WSL users)
Reliable script designed specifically for Windows Subsystem for Linux.

**Usage:**
```bash
# Direct method (recommended) - runs command directly
python run_claude_wsl.py /path/to/directory "Your input string"

# Script method - creates temporary bash script
python run_claude_wsl.py --method script /path/to/directory "Your input"

# With custom wait time
python run_claude_wsl.py --wait-time 10 /path/to/directory "Your input"

# Keep terminal open after execution
python run_claude_wsl.py --keep-open /path/to/directory "Your input"
```

**Features:**
- Direct command execution in Windows Terminal
- No dependency on GUI automation
- Multiple execution methods
- Automatic WSL path conversion
- More reliable than pyautogui approach

### 2. `run_claude.py` - Basic GUI Automation
Simple script using pyautogui for keyboard automation.

**Usage:**
```bash
python run_claude.py /path/to/directory "Your input string"

# With options
python run_claude.py --verbose /path/to/directory "Hello Claude"
python run_claude.py --delay 3 /path/to/directory "Custom delay"
```

**Features:**
- Cross-platform terminal detection
- Automatic keyboard input simulation
- Configurable delays

### 3. `run_claude_pexpect.py` - Terminal Control (Linux/Mac)
Uses pexpect for better terminal interaction control.

**Usage:**
```bash
python run_claude_pexpect.py /path/to/directory "Your input string"

# With verbose output
python run_claude_pexpect.py --verbose /path/to/directory "Hello Claude"
```

**Features:**
- More reliable terminal interaction
- Better output capture capabilities
- Fallback to GUI automation on Windows

### 4. `run_claude_advanced.py` - Full-Featured Solution
Advanced script with comprehensive error handling, logging, and configuration.

**Usage:**
```bash
# Basic usage
python run_claude_advanced.py /path/to/directory "Your input string"

# Dry run (see what would happen)
python run_claude_advanced.py --dry-run /path/to/directory "Test"

# With logging
python run_claude_advanced.py --log-file automation.log /path "Input"

# Custom delays
python run_claude_advanced.py --spawn-delay 3 --wait-time 10 /path "Input"

# With config file
python run_claude_advanced.py --config myconfig.json /path "Input"
```

**Features:**
- Comprehensive error handling
- Configurable via JSON file
- Dry-run mode for testing
- Detailed logging
- Platform-specific terminal detection
- Permission and path validation

## Configuration

Create a `config.json` file for `run_claude_advanced.py`:

```json
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
```

## Platform Support

- **WSL (Windows Subsystem for Linux)**: Uses Windows Terminal (wt.exe) with automatic path conversion
- **Linux**: Supports gnome-terminal, konsole, xterm, terminator, xfce4-terminal
- **macOS**: Uses Terminal.app via AppleScript
- **Windows**: Uses cmd or PowerShell

## Requirements

- Python 3.7+
- Terminal emulator (platform-specific)
- Claude CLI installed and in PATH

## Troubleshooting

### Linux
- Install `python3-tk` if pyautogui fails: `sudo apt-get install python3-tk`
- For X11 issues: `sudo apt-get install python3-xlib`

### macOS
- Grant Terminal/Python accessibility permissions in System Preferences > Security & Privacy

### Windows
- Run as administrator if permission issues occur
- pexpect-based script will fallback to GUI automation

### WSL (Windows Subsystem for Linux)
- Windows Terminal (wt.exe) must be installed (usually pre-installed with WSL2)
- The scripts automatically convert Linux paths to Windows format
- If you see path errors, ensure Windows Terminal has access to WSL filesystem
- **If pyautogui doesn't type commands**: Use `run_claude_wsl.py` instead - it's more reliable
- **PowerShell opens but nothing happens**: The terminal might not have focus. Try:
  - Using `run_claude_wsl.py` with the direct method
  - Running with `--keep-open` flag to debug
  - Ensuring no other windows steal focus during execution
- **"claude: command not found" error**: This happens when claude is installed via npm but PATH isn't set in non-interactive shells
  - Run `python bin/diagnose_claude.py` to diagnose the issue
  - Use `python bin/run_claude_fixed.py` which handles PATH issues automatically
  - Or use the `--use-full-path` flag with other scripts

## Example Use Cases

1. **Automated testing:**
   ```bash
   python run_claude.py /home/user/test-project "run tests"
   ```

2. **Batch processing:**
   ```bash
   for dir in project1 project2 project3; do
       python run_claude.py "/home/user/$dir" "analyze code"
   done
   ```

3. **Scheduled tasks:**
   Add to crontab or task scheduler for regular automated Claude interactions.

## Security Notes

- Scripts simulate keyboard input, so ensure no sensitive information is visible
- The input string is typed in plain text
- Consider using environment variables for sensitive data

## License

MIT License - See LICENSE file for details