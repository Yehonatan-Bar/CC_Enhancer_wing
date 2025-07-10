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

2. Run the WSL-optimized automation (recommended for all platforms):
   ```bash
   python run_claude_wsl.py "/path/to/your/project" "Your prompt here"
   ```

### Usage Examples

```bash
# Basic usage
python run_claude_wsl.py /home/user/project "Explain this code"

# With different methods
python run_claude_wsl.py --method direct /path "Your prompt"     # Default, recommended
python run_claude_wsl.py --method interactive /path "Your prompt" # Uses interactive shell
python run_claude_wsl.py --method script /path "Your prompt"      # Creates temp script

# With custom wait time
python run_claude_wsl.py --wait-time 10 /path "Your prompt"

# Verbose output for debugging
python run_claude_wsl.py --verbose /path "Your prompt"
```

## Usage

### Available Scripts

#### Main Script

**run_claude_wsl.py** - WSL-optimized automation (works on all platforms)
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
├── run_claude_wsl.py          # Main WSL-optimized automation script
├── config.json                # Default configuration
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
├── project_structure.json     # Project metadata
├── bin/                       # Auxiliary and deprecated scripts
│   ├── run_claude.py          # Basic terminal automation (deprecated)
│   ├── run_claude_advanced.py # Full-featured implementation (deprecated)
│   ├── run_claude_pexpect.py  # Output capture version
│   ├── run_claude_fixed.py    # PATH-aware version
│   ├── diagnose_claude.py     # Diagnostic tool
│   └── ...                    # Other utilities
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