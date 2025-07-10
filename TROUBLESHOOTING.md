# Troubleshooting Guide for Claude Terminal Automation

## Common Issues and Solutions

### 1. "claude: command not found" Error

**Problem**: When the script runs, you see `claude: command not found` even though `claude` works in your regular terminal.

**Cause**: The claude command is in your PATH when using an interactive shell, but not in non-interactive shells spawned by the script.

**Solutions**:

#### Option A: Use the interactive method (Recommended)
```bash
python run_claude_wsl.py --method interactive /path "Your command"
```
This uses `bash -i` which sources your shell configuration files.

#### Option B: Use the fixed script
```bash
python bin/run_claude_fixed.py /path "Your command"
```
This script automatically handles PATH issues.

#### Option C: Use full path to claude
First, find where claude is installed:
```bash
which claude
```
Then use the full path in scripts or modify the scripts to use it.

### 2. Terminal Opens But Nothing Happens

**Problem**: Windows Terminal opens at the correct directory but no commands are typed.

**Cause**: The pyautogui library can't type into the window because:
- The terminal doesn't have keyboard focus
- Windows security is blocking automated input
- There's a timing issue

**Solutions**:

#### Use command execution instead of keyboard automation:
```bash
# Use the WSL script with direct method
python run_claude_wsl.py --method direct /path "Your command"

# Or use interactive method
python run_claude_wsl.py --method interactive /path "Your command"
```

### 3. Diagnosing Issues

Run the diagnostic tool to understand your setup:
```bash
python bin/diagnose_claude.py
```

This will show you:
- Where claude is installed
- Whether it's in your PATH
- How different shell types behave
- Specific recommendations for your system

### 4. Windows-Specific Issues

#### PowerShell vs WSL Path Issues
- WSL paths (`/home/user/...`) need to be converted to Windows paths (`\\wsl.localhost\Ubuntu\...`)
- The scripts handle this automatically, but ensure Windows Terminal has access to WSL filesystem

#### Focus Issues
- Ensure no other applications steal focus when the script runs
- Try running with fewer applications open
- Use the `--verbose` flag to see what's happening

### 5. Quick Fixes

#### Test if claude works in different shell contexts:
```bash
# Interactive shell (should work)
bash -ic 'which claude'

# Non-interactive shell (might fail)
bash -c 'which claude'

# With sourced bashrc (should work)
bash -c 'source ~/.bashrc && which claude'
```

#### Add claude to PATH permanently:
Add this to your `~/.bashrc`:
```bash
export PATH=$PATH:~/.npm-global/bin
```

### 6. Alternative Approaches

If automation continues to fail, consider:

1. **Manual wrapper script**: Create a simple bash script that runs claude:
   ```bash
   #!/bin/bash
   source ~/.bashrc
   cd "$1"
   sleep 5
   echo "$2" | claude
   ```

2. **Use Windows Terminal profiles**: Create a custom profile that runs claude directly

3. **Use tmux or screen**: Run claude in a persistent session

## Debug Mode

Run scripts with verbose output to see exactly what's happening:
```bash
python run_claude_wsl.py --verbose --keep-open /path "Test"
```

The `--keep-open` flag prevents the terminal from closing, letting you see any error messages.