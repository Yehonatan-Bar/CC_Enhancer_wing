# Code Enhancer - Claude CLI Automation Toolkit

## Overview

Code Enhancer is a comprehensive automation toolkit for Anthropic's Claude CLI, enabling programmatic interaction with Claude through terminal automation. This project provides multiple implementation approaches to automate terminal operations, execute Claude commands, and send input across different platforms.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Platform Support](#platform-support)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-Platform Support**: Works on Linux, macOS, Windows, and WSL
- **Multiple Implementation Methods**: Choose from various automation approaches
- **Flexible Configuration**: Customize timing, terminals, and behavior
- **Output Capture**: Some implementations can capture Claude's responses
- **Robust Error Handling**: Advanced implementations include retry logic and diagnostics
- **Terminal Emulator Support**: Works with gnome-terminal, konsole, xterm, Terminal.app, CMD, PowerShell, and more

## Requirements

### System Requirements

- Python 3.8 or higher
- Claude CLI installed and configured
- Supported operating system (Linux, macOS, Windows, or WSL)

### Python Dependencies

```
pyautogui==0.9.54
pexpect==4.9.0
click==8.1.7
PyGetWindow==0.0.9
Pillow==10.2.0
python-xlib==0.33
pyperclip==1.8.2
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/code_enhancer.git
cd code_enhancer
```

### 2. Run the Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Check for Python 3.8+
- Create a virtual environment
- Install all dependencies
- Verify Claude CLI availability
- Set up the project structure

### 3. Manual Installation (Alternative)

If you prefer manual installation:

```bash
# Create virtual environment
python3 -m venv venv_cc_enhancer

# Activate virtual environment
# On Linux/macOS:
source venv_cc_enhancer/bin/activate
# On Windows:
venv_cc_enhancer\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

1. Activate the virtual environment:
   ```bash
   source venv_cc_enhancer/bin/activate
   ```

2. Capture Claude's output programmatically:

   ```bash
   # Smart capture with auto-permission detection
   python claude_capture.py "create a hello.py file"
   
   # Always auto-approve permissions (simpler)
   python claude_auto.py "create a test.txt file"
   ```

### Usage Examples

```bash
# Smart permission handling (recommended)
python claude_capture.py "What is 2+2?"                    # No permissions needed
python claude_capture.py "Create a Python hello world"      # Auto-detects need for permissions
python claude_capture.py "List files" --no-permissions     # Force no permissions

# Simple auto-approve mode
python claude_auto.py "create a hello.py file with print('Hello')"

# WSL terminal automation (for interactive use)
python run_claude_wsl.py /home/user/project "Explain this code"
```

## Usage

### Available Scripts

#### Main Scripts

1. **claude_capture.py** - Smart capture with automatic permission detection
   ```bash
   python claude_capture.py "Your prompt"
   ```
   
   Features:
   - Automatically detects when permissions are needed
   - Retries with permissions if Claude asks
   - Clear feedback about operation mode

2. **claude_auto.py** - Simple capture with auto-approved permissions
   ```bash
   python claude_auto.py "Your prompt"
   ```
   
   Features:
   - Always runs with permissions enabled
   - Minimal friction for trusted operations
   - Direct output to stdout

3. **run_claude_wsl.py** - WSL-optimized terminal automation
   ```bash
   python run_claude_wsl.py /path/to/project "Your prompt"
   ```
   
   Options:
   - `--method` - Choose automation method (direct, script, interactive, pyautogui)
   - `--wait-time` - Set wait time before sending input (default: 5 seconds)
   - `--verbose` - Enable verbose output for debugging
   - `--keep-open` - Keep terminal open after command execution

#### Auxiliary Scripts (in bin/)

1. **run_claude_pexpect.py** - Terminal control with output capture
   ```bash
   python bin/run_claude_pexpect.py "Your prompt"
   ```

2. **run_claude_fixed.py** - Handles PATH issues automatically
   ```bash
   python bin/run_claude_fixed.py "Your prompt"
   ```

3. **diagnose_claude.py** - Diagnostic tool
   ```bash
   python bin/diagnose_claude.py
   ```

4. **get_file_content.py** - Secure file reading utility
   ```bash
   python get_file_content.py <file_path> [allowed_base_path]
   ```
   
   Features:
   - Path traversal prevention
   - Symbolic link validation
   - Sensitive file protection
   - File size limits (100MB)
   - Optional base path restriction for sandboxing

### Command-Line Options

Most scripts support these common options:
- `--terminal` - Specify terminal emulator
- `--config` - Use custom configuration file
- `--log-level` - Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `--dry-run` - Test without executing commands

## Platform Support

### Linux
- Supported terminals: gnome-terminal, konsole, xterm, terminator
- Default: gnome-terminal

### macOS
- Supported terminals: Terminal.app, iTerm2
- Default: Terminal.app

### Windows
- Supported terminals: CMD, PowerShell, Windows Terminal
- Default: CMD

### WSL (Windows Subsystem for Linux)
- Special path conversion handling
- Windows Terminal integration
- Use `run_claude_wsl.py` for best results

## Project Structure

```
code_enhancer/
├── claude_capture.py          # Smart capture with auto-permission detection
├── claude_auto.py             # Simple capture with auto-permissions
├── run_claude_wsl.py          # WSL-optimized terminal automation
├── example_claude_capture.py  # Usage examples
├── CLAUDE_CAPTURE_GUIDE.md    # Detailed capture documentation
├── config.json                # Default configuration
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
├── project_structure.json     # Project metadata
├── General_instruction.txt    # Project guidelines
├── bin/                       # Auxiliary and utility scripts
│   ├── capture_claude_simple.py      # Core capture implementation
│   ├── claude_auto_responder.py      # Interactive auto-responder
│   ├── claude_auto_responder_pty.py  # PTY-based auto-responder
│   ├── run_claude.py                 # Basic terminal automation
│   ├── run_claude_advanced.py        # Full-featured implementation
│   ├── run_claude_pexpect.py         # Output capture version
│   ├── run_claude_fixed.py           # PATH-aware version
│   ├── diagnose_claude.py            # Diagnostic tool
│   └── test_*.py                     # Test scripts
├── venv_cc_enhancer/          # Virtual environment
└── docs/                      # Additional documentation
```

## Configuration

### config.json Structure

```json
{
  "terminal_spawn_delay": 3,
  "claude_wait_time": 2,
  "keyboard_delay": 0.1,
  "platforms": {
    "linux": {
      "default_terminal": "gnome-terminal",
      "terminals": {
        "gnome-terminal": {
          "command": ["gnome-terminal", "--"],
          "spawn_delay": 3
        }
      }
    }
  }
}
```

### Customizing Configuration

1. Copy the default config:
   ```bash
   cp config.json my_config.json
   ```

2. Edit timing and terminal preferences

3. Use with scripts:
   ```bash
   python run_claude_advanced.py --config my_config.json "Your prompt"
   ```

## Troubleshooting

### Common Issues

1. **Claude command not found**
   - Ensure Claude CLI is installed: `pip install claude-cli`
   - Check PATH: `which claude`
   - Use `run_claude_fixed.py` for automatic PATH resolution

2. **Terminal doesn't open**
   - Verify terminal emulator is installed
   - Check configuration for correct terminal command
   - Try a different terminal with `--terminal` option

3. **Timing issues**
   - Increase delays in config.json
   - Use `--log-level DEBUG` to diagnose
   - Adjust `terminal_spawn_delay` and `claude_wait_time`

4. **WSL-specific issues**
   - Use `run_claude_wsl.py` instead of base script
   - Ensure Windows Terminal is default terminal app
   - Check WSL path conversions

### Diagnostic Steps

1. Run the diagnostic tool:
   ```bash
   python bin/diagnose_claude.py
   ```

2. Check verbose output:
   ```bash
   python run_claude_advanced.py --log-level DEBUG "test"
   ```

3. Test with simple prompt:
   ```bash
   python run_claude.py "Hello"
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Update README.md and project_structure.json
5. Test on multiple platforms if possible
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Add docstrings to all functions
- Update documentation for new features
- Include error handling for platform-specific code
- Test on at least two different platforms

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- Anthropic for creating Claude and the Claude CLI
- Contributors and testers who helped improve cross-platform support
- The Python community for excellent automation libraries

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation in the docs/ folder
- Review TROUBLESHOOTING.md for common problems

---

**Note**: This tool automates terminal interactions and requires appropriate permissions for GUI automation on some systems. Ensure you understand the security implications before use in production environments.