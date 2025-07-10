#!/usr/bin/env python3
"""
Terminal automation script to run Claude CLI with automated input.
"""

import sys
import os
import time
import subprocess
import platform
import click
import pyautogui
from pathlib import Path


def convert_wsl_path(linux_path):
    """Convert WSL Linux path to Windows path format."""
    try:
        result = subprocess.run(['wslpath', '-w', linux_path], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If conversion fails, return original path
        return linux_path


def get_terminal_command():
    """Get the appropriate terminal command based on the platform."""
    system = platform.system().lower()
    
    # Check if running in WSL
    if system == "linux" and os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
        # Running in WSL, use Windows Terminal
        return ["wt.exe", "-d"]
    
    if system == "linux":
        # Try different terminal emulators in order of preference
        terminals = [
            ["gnome-terminal", "--working-directory"],
            ["konsole", "--workdir"],
            ["xterm", "-e", "cd {} &&"],
            ["terminator", "--working-directory"],
            ["xfce4-terminal", "--working-directory"]
        ]
        
        for terminal in terminals:
            try:
                subprocess.run([terminal[0], "--version"], 
                             capture_output=True, check=True)
                return terminal
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
                
        raise RuntimeError("No supported terminal emulator found")
    
    elif system == "darwin":  # macOS
        return ["open", "-a", "Terminal", "-n", "--args"]
    
    elif system == "windows":
        return ["cmd", "/c", "start", "cmd", "/k", "cd /d {} &&"]
    
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def open_terminal_at_path(path):
    """Open a new terminal window at the specified path."""
    terminal_cmd = get_terminal_command()
    
    # Check if running in WSL
    if platform.system().lower() == "linux" and os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
        # Use Windows Terminal in WSL - convert path to Windows format
        windows_path = convert_wsl_path(path)
        cmd = [terminal_cmd[0], terminal_cmd[1], windows_path]
    elif platform.system().lower() == "linux":
        if len(terminal_cmd) == 2:  # gnome-terminal style
            cmd = [terminal_cmd[0], f"{terminal_cmd[1]}={path}"]
        else:  # xterm style
            cmd = [terminal_cmd[0], terminal_cmd[1], 
                   terminal_cmd[2].format(path), "bash"]
    elif platform.system().lower() == "darwin":
        # macOS requires a different approach
        script = f'tell application "Terminal" to do script "cd {path}"'
        cmd = ["osascript", "-e", script]
    else:  # Windows
        cmd = ["cmd", "/c", "start", "cmd", "/k", f"cd /d {path}"]
    
    subprocess.Popen(cmd)


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, 
                                       dir_okay=True, resolve_path=True))
@click.argument('input_string')
@click.option('--delay', default=2, help='Delay before typing (seconds)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def main(path, input_string, delay, verbose):
    """
    Open a terminal at PATH, run 'claude' command, wait 5 seconds,
    then enter INPUT_STRING and press Enter.
    
    Example:
        python run_claude.py /home/user/project "Hello Claude"
    """
    
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        click.echo(f"Error: Path '{path}' does not exist", err=True)
        sys.exit(1)
    
    if not path_obj.is_dir():
        click.echo(f"Error: Path '{path}' is not a directory", err=True)
        sys.exit(1)
    
    if verbose:
        click.echo(f"Opening terminal at: {path}")
        click.echo(f"Will enter string: {input_string}")
    
    try:
        # Open terminal at specified path
        open_terminal_at_path(str(path_obj))
        
        # Wait for terminal to open
        if verbose:
            click.echo(f"Waiting {delay} seconds for terminal to open...")
        time.sleep(delay)
        
        # Try to ensure the terminal window has focus
        # This is especially important in WSL/Windows environments
        if platform.system().lower() == "linux" and os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
            # For WSL, try to bring window to front
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
        
        # Type the claude command with full path
        if verbose:
            click.echo("Typing 'claude' command...")
        # Use full path to claude to avoid PATH issues
        claude_path = "/home/laurelin/.npm-global/bin/claude"
        if os.path.exists(claude_path):
            pyautogui.typewrite(claude_path)
        else:
            # Fallback to just 'claude' if full path doesn't exist
            pyautogui.typewrite("claude")
        pyautogui.press("enter")
        
        # Wait 5 seconds as requested
        if verbose:
            click.echo("Waiting 5 seconds...")
        time.sleep(5)
        
        # Type the input string
        if verbose:
            click.echo(f"Typing input string: {input_string}")
        pyautogui.typewrite(input_string)
        
        # Press Enter
        pyautogui.press("enter")
        
        if verbose:
            click.echo("Done!")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    # Disable pyautogui failsafe for better automation
    pyautogui.FAILSAFE = False
    main()