#!/usr/bin/env python3
"""
Alternative approach: Modified version of run_claude_wsl.py that captures output
instead of opening a new terminal window.
"""

import sys
import os
import subprocess
import click
import shlex
from pathlib import Path
import time
import tempfile
import json


def run_claude_direct(path, input_string, wait_time=5, capture=True):
    """
    Run Claude directly and optionally capture output.
    
    Returns:
        dict: Contains 'stdout', 'stderr', 'returncode', and 'success' keys
    """
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        return {
            'stdout': '',
            'stderr': f"Error: Path '{path}' does not exist",
            'returncode': 1,
            'success': False
        }
    
    # Full path to claude
    claude_path = "/home/laurelin/.npm-global/bin/claude"
    
    # Change to the specified directory and run claude
    cmd = f"cd {shlex.quote(str(path_obj))} && echo {shlex.quote(input_string)} | {claude_path}"
    
    if capture:
        # Run with output capture
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Add a small delay to let Claude initialize
        time.sleep(wait_time)
        
        # Get output
        stdout, stderr = process.communicate()
        
        return {
            'stdout': stdout,
            'stderr': stderr,
            'returncode': process.returncode,
            'success': process.returncode == 0
        }
    else:
        # Run without capture (interactive mode)
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        
        return {
            'stdout': '',
            'stderr': '',
            'returncode': process.returncode,
            'success': process.returncode == 0
        }


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('input_string')
@click.option('--wait-time', default=5, help='Wait time before sending input (seconds)')
@click.option('--capture/--no-capture', default=True, help='Capture output or run interactively')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.option('--save-to', type=click.Path(), help='Save output to file')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def main(path, input_string, wait_time, capture, json_output, save_to, verbose):
    """
    Run Claude with optional output capture.
    
    Examples:
        # Capture output and display
        python run_claude_capture.py /home/user/project "Hello Claude"
        
        # Save output to file
        python run_claude_capture.py /home/user/project "Hello" --save-to output.txt
        
        # Get JSON output for programmatic use
        python run_claude_capture.py /home/user/project "Hello" --json-output
        
        # Run interactively without capture
        python run_claude_capture.py /home/user/project "Hello" --no-capture
    """
    
    if verbose:
        click.echo(f"Running Claude in: {path}")
        click.echo(f"Input: {input_string}")
        click.echo(f"Capture mode: {capture}")
    
    # Run Claude
    result = run_claude_direct(path, input_string, wait_time, capture)
    
    if json_output:
        # Output as JSON for easy parsing
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        if result['stdout']:
            if not save_to:
                print("=== CLAUDE OUTPUT ===")
                print(result['stdout'])
                print("===================")
        
        if result['stderr']:
            print("=== ERRORS ===", file=sys.stderr)
            print(result['stderr'], file=sys.stderr)
            print("==============", file=sys.stderr)
        
        if not result['success']:
            print(f"\nClaude exited with code: {result['returncode']}", file=sys.stderr)
    
    # Save to file if requested
    if save_to and capture:
        with open(save_to, 'w') as f:
            if result['stdout']:
                f.write("=== CLAUDE OUTPUT ===\n")
                f.write(result['stdout'])
                f.write("\n===================\n")
            
            if result['stderr']:
                f.write("\n=== ERRORS ===\n")
                f.write(result['stderr'])
                f.write("\n==============\n")
        
        if verbose:
            print(f"\nOutput saved to: {save_to}")
    
    # Exit with same code as Claude
    sys.exit(result['returncode'])


# Function for programmatic use
def get_claude_output(path, input_string, wait_time=5):
    """
    Get Claude's output programmatically.
    
    Returns:
        str: Claude's stdout output
        
    Raises:
        RuntimeError: If Claude fails
    """
    result = run_claude_direct(path, input_string, wait_time, capture=True)
    
    if not result['success']:
        raise RuntimeError(f"Claude failed: {result['stderr']}")
    
    return result['stdout']


if __name__ == "__main__":
    main()