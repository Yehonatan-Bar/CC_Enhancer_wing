#!/usr/bin/env python3
"""
Fixed version of Claude automation that handles PATH issues properly.
Automatically detects claude location and ensures it's accessible.
"""

import sys
import os
import subprocess
import click
import shlex
from pathlib import Path
import time


def find_claude_command():
    """Find the claude command location."""
    # First try which command
    try:
        result = subprocess.run(['which', 'claude'], 
                              capture_output=True, text=True, check=True)
        claude_path = result.stdout.strip()
        if claude_path:
            return claude_path
    except subprocess.CalledProcessError:
        pass
    
    # Common locations to check
    common_paths = [
        os.path.expanduser("~/.npm-global/bin/claude"),
        "/usr/local/bin/claude",
        "/usr/bin/claude",
        os.path.expanduser("~/.local/bin/claude"),
    ]
    
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


def convert_wsl_path(linux_path):
    """Convert WSL Linux path to Windows path format."""
    try:
        result = subprocess.run(['wslpath', '-w', linux_path], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return linux_path


def get_shell_init_command():
    """Get the command to initialize the shell environment."""
    # Check which shell configuration files exist
    configs = [
        "~/.bashrc",
        "~/.bash_profile",
        "~/.profile",
        "~/.zshrc",
    ]
    
    for config in configs:
        config_path = os.path.expanduser(config)
        if os.path.exists(config_path):
            return f"source {config}"
    
    return ""


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, 
                                       dir_okay=True, resolve_path=True))
@click.argument('input_string')
@click.option('--wait-time', default=5, help='Wait time before sending input (seconds)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--use-full-path', is_flag=True, help='Use full path to claude command')
@click.option('--claude-path', help='Specify claude command path explicitly')
def main(path, input_string, wait_time, verbose, use_full_path, claude_path):
    """
    Run Claude with proper PATH handling in WSL/Linux environments.
    
    This script automatically detects the claude command location and
    ensures it's accessible in the spawned terminal.
    
    Examples:
    
        # Auto-detect claude location
        python run_claude_fixed.py /home/user/project "Hello Claude"
        
        # Use full path to claude
        python run_claude_fixed.py --use-full-path /path "Input"
        
        # Specify claude path explicitly
        python run_claude_fixed.py --claude-path /usr/bin/claude /path "Input"
    """
    
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        click.echo(f"Error: Path '{path}' does not exist", err=True)
        sys.exit(1)
    
    # Determine claude command
    if claude_path:
        claude_cmd = claude_path
    elif use_full_path:
        claude_cmd = find_claude_command()
        if not claude_cmd:
            click.echo("Error: Could not find claude command. Use --claude-path to specify.", err=True)
            sys.exit(1)
    else:
        claude_cmd = "claude"
    
    # Get shell initialization command
    shell_init = get_shell_init_command()
    
    if verbose:
        click.echo(f"Claude command: {claude_cmd}")
        click.echo(f"Shell init: {shell_init}")
        click.echo(f"Path: {path}")
        click.echo(f"Input: {input_string}")
        click.echo(f"Wait time: {wait_time}s")
    
    try:
        # Check if running in WSL
        is_wsl = os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop")
        
        if is_wsl:
            # Convert path for Windows Terminal
            windows_path = convert_wsl_path(str(path_obj))
            
            # Escape the input string for bash
            escaped_input = shlex.quote(input_string)
            
            # Build the bash command with proper initialization
            bash_cmd_parts = []
            
            # Add shell initialization if found
            if shell_init:
                bash_cmd_parts.append(shell_init)
            
            # Change directory
            bash_cmd_parts.append(f"cd {shlex.quote(str(path_obj))}")
            
            # Run claude with input
            bash_cmd_parts.append(f"echo 'Waiting {wait_time} seconds...' && sleep {wait_time} && echo {escaped_input} | {claude_cmd}")
            
            # Join all parts
            bash_cmd = " && ".join(bash_cmd_parts)
            
            # Build Windows Terminal command
            cmd = [
                "wt.exe",
                "-d", windows_path,
                "--",
                "bash", "-c", bash_cmd
            ]
            
            if verbose:
                click.echo(f"Running command: {' '.join(cmd)}")
            
            subprocess.Popen(cmd)
            
        else:
            # For non-WSL Linux, use a different approach
            # Try to open terminal emulator directly
            terminals = [
                ["gnome-terminal", "--", "bash", "-c"],
                ["konsole", "-e", "bash", "-c"],
                ["xterm", "-e", "bash", "-c"],
            ]
            
            terminal_found = False
            for terminal_cmd in terminals:
                try:
                    # Build bash command
                    bash_cmd_parts = []
                    if shell_init:
                        bash_cmd_parts.append(shell_init)
                    
                    bash_cmd_parts.append(f"cd {shlex.quote(str(path_obj))}")
                    bash_cmd_parts.append(f"sleep {wait_time} && echo {shlex.quote(input_string)} | {claude_cmd} && read -p 'Press Enter to exit...'")
                    
                    bash_cmd = " && ".join(bash_cmd_parts)
                    
                    full_cmd = terminal_cmd + [bash_cmd]
                    
                    if verbose:
                        click.echo(f"Trying: {terminal_cmd[0]}")
                    
                    subprocess.Popen(full_cmd)
                    terminal_found = True
                    break
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not terminal_found:
                click.echo("Error: No supported terminal emulator found", err=True)
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