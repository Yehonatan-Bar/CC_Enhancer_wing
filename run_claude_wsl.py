#!/usr/bin/env python3
"""
WSL-optimized script for running Claude with automated input.
Uses Windows Terminal's command execution instead of keyboard automation.
"""

import sys
import os
import subprocess
import click
import shlex
from pathlib import Path
import time
import tempfile


def convert_wsl_path(linux_path):
    """Convert WSL Linux path to Windows path format."""
    try:
        result = subprocess.run(['wslpath', '-w', linux_path], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return linux_path


def create_bash_wrapper(path, input_string, wait_time=5):
    """Create a temporary bash script that runs claude with delayed input."""
    script_content = f"""#!/bin/bash
# Source .bashrc to ensure PATH is set correctly
source ~/.bashrc

cd "{path}"
(
    echo "Running claude in {path}..."
    sleep {wait_time}
    echo "{input_string}"
) | /home/laurelin/.npm-global/bin/claude
"""
    
    # Create temporary script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    return script_path


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, 
                                       dir_okay=True, resolve_path=True))
@click.argument('input_string')
@click.option('--method', type=click.Choice(['direct', 'script', 'interactive', 'pyautogui']), 
              default='direct', help='Method to use for automation')
@click.option('--wait-time', default=5, help='Wait time before sending input (seconds)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--keep-open', is_flag=True, help='Keep terminal open after command')
def main(path, input_string, method, wait_time, verbose, keep_open):
    """
    Run Claude in Windows Terminal with automated input (WSL-optimized).
    
    This script provides multiple methods for running Claude:
    
    1. direct: Uses bash command with input piping (recommended)
    2. script: Creates a temporary bash script
    3. interactive: Uses interactive bash shell (bash -i) - best for PATH issues
    4. pyautogui: Falls back to keyboard automation with window focus
    
    Examples:
    
        # Default method (direct)
        python run_claude_wsl.py /home/user/project "Hello Claude"
        
        # Using script method
        python run_claude_wsl.py --method script /path "Input"
        
        # With custom wait time
        python run_claude_wsl.py --wait-time 10 /path "Input"
    """
    
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        click.echo(f"Error: Path '{path}' does not exist", err=True)
        sys.exit(1)
    
    # Check if running in WSL
    if not os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
        click.echo("Warning: This script is optimized for WSL but WSL not detected", err=True)
    
    if verbose:
        click.echo(f"Method: {method}")
        click.echo(f"Path: {path}")
        click.echo(f"Input: {input_string}")
        click.echo(f"Wait time: {wait_time}s")
    
    try:
        if method == 'direct':
            # Method 1: Direct command with bash -c
            # This creates a bash command that changes directory and pipes input to claude
            windows_path = convert_wsl_path(str(path_obj))
            
            # Escape the input string for bash
            escaped_input = shlex.quote(input_string)
            
            # Build the bash command
            # Use full path to claude to avoid PATH issues
            claude_path = "/home/laurelin/.npm-global/bin/claude"
            bash_cmd = f"cd {shlex.quote(str(path_obj))} && echo 'Waiting {wait_time} seconds...' && sleep {wait_time} && echo {escaped_input} | {claude_path}"
            
            if keep_open:
                bash_cmd += " && echo 'Press Enter to exit...' && read"
            
            # Build the full Windows Terminal command
            cmd = [
                "wt.exe",
                "-d", windows_path,
                "--",
                "bash", "-c", bash_cmd
            ]
            
            if verbose:
                click.echo(f"Running command: {' '.join(cmd)}")
            
            subprocess.Popen(cmd)
            
        elif method == 'script':
            # Method 2: Create a temporary script
            script_path = create_bash_wrapper(str(path_obj), input_string, wait_time)
            windows_path = convert_wsl_path(str(path_obj))
            
            try:
                # Run the script in Windows Terminal
                cmd = [
                    "wt.exe",
                    "-d", windows_path,
                    "--",
                    "bash", script_path
                ]
                
                if keep_open:
                    cmd[-1] += " && echo 'Press Enter to exit...' && read"
                
                if verbose:
                    click.echo(f"Created script: {script_path}")
                    click.echo(f"Running command: {' '.join(cmd)}")
                
                subprocess.Popen(cmd)
                
                # Give it time to start before cleanup
                time.sleep(2)
                
            finally:
                # Clean up temporary script
                if not verbose:  # Keep script for debugging if verbose
                    try:
                        os.unlink(script_path)
                    except:
                        pass
                        
        elif method == 'interactive':
            # Method 3: Use interactive bash shell
            windows_path = convert_wsl_path(str(path_obj))
            escaped_input = shlex.quote(input_string)
            
            # Build command using interactive shell with full path
            claude_path = "/home/laurelin/.npm-global/bin/claude"
            bash_cmd = f"cd {shlex.quote(str(path_obj))} && echo 'Waiting {wait_time} seconds...' && sleep {wait_time} && echo {escaped_input} | {claude_path}"
            
            if keep_open:
                bash_cmd += " && echo 'Press Enter to exit...' && read"
            
            # Use bash -i for interactive shell that sources .bashrc
            cmd = [
                "wt.exe",
                "-d", windows_path,
                "--",
                "bash", "-i", "-c", bash_cmd
            ]
            
            if verbose:
                click.echo("Using interactive bash shell (-i flag)")
                click.echo(f"Running command: {' '.join(cmd)}")
            
            subprocess.Popen(cmd)
            
        elif method == 'pyautogui':
            # Method 3: Fall back to pyautogui with better window handling
            try:
                import pyautogui
                pyautogui.FAILSAFE = False
                
                # Open terminal
                windows_path = convert_wsl_path(str(path_obj))
                cmd = ["wt.exe", "-d", windows_path]
                
                if verbose:
                    click.echo("Opening terminal with pyautogui method...")
                
                subprocess.Popen(cmd)
                
                # Wait for terminal and ensure it has focus
                time.sleep(2)
                
                # Try to focus the window (Windows-specific)
                # This attempts to bring the window to front
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.5)
                
                # Type claude command with full path
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
                
                # Wait specified time
                if verbose:
                    click.echo(f"Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                
                # Type input
                if verbose:
                    click.echo(f"Typing input: {input_string}")
                pyautogui.typewrite(input_string)
                pyautogui.press("enter")
                
            except ImportError:
                click.echo("Error: pyautogui not installed. Use --method direct or script", err=True)
                sys.exit(1)
        
        if verbose:
            click.echo("Command launched successfully!")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()