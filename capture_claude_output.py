#!/usr/bin/env python3
"""
Script to capture Claude's output by running it directly in the current terminal
instead of opening a new window.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import click


def run_claude_with_capture(path, input_string, wait_time=5, verbose=False):
    """
    Run Claude and capture its output.
    
    Args:
        path: Directory to run Claude in
        input_string: Input to send to Claude
        wait_time: Time to wait before sending input
        verbose: Enable verbose output
        
    Returns:
        tuple: (stdout, stderr, return_code)
    """
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        raise ValueError(f"Path '{path}' does not exist")
    
    # Full path to claude
    claude_path = "/home/laurelin/.npm-global/bin/claude"
    
    if verbose:
        print(f"Running Claude in: {path}")
        print(f"Input: {input_string}")
        print(f"Wait time: {wait_time}s")
    
    # Create a process that runs claude with piped input
    # We'll use echo to send the input after a delay
    cmd = f"cd {path} && (sleep {wait_time} && echo '{input_string}') | {claude_path}"
    
    if verbose:
        print(f"Command: {cmd}")
    
    # Run the command and capture output
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the process to complete
    stdout, stderr = process.communicate()
    
    return stdout, stderr, process.returncode


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('input_string')
@click.option('--wait-time', default=5, help='Wait time before sending input (seconds)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--save-to', type=click.Path(), help='Save output to file')
def main(path, input_string, wait_time, verbose, save_to):
    """
    Capture Claude's output when running with automated input.
    
    Example:
        python capture_claude_output.py /home/user/project "Hello Claude" --save-to output.txt
    """
    try:
        # Run Claude and capture output
        stdout, stderr, return_code = run_claude_with_capture(
            path, input_string, wait_time, verbose
        )
        
        # Display results
        if stdout:
            print("=== CLAUDE OUTPUT ===")
            print(stdout)
            print("===================")
        
        if stderr:
            print("=== ERRORS ===", file=sys.stderr)
            print(stderr, file=sys.stderr)
            print("==============", file=sys.stderr)
        
        if return_code != 0:
            print(f"\nClaude exited with code: {return_code}", file=sys.stderr)
        
        # Save to file if requested
        if save_to:
            with open(save_to, 'w') as f:
                f.write("=== CLAUDE OUTPUT ===\n")
                f.write(stdout)
                if stderr:
                    f.write("\n=== ERRORS ===\n")
                    f.write(stderr)
            print(f"\nOutput saved to: {save_to}")
        
        # Return the output (useful when imported as a module)
        return stdout
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def capture_claude_output(path, input_string, wait_time=5):
    """
    Function to use when importing this module.
    
    Example:
        from capture_claude_output import capture_claude_output
        output = capture_claude_output("/path/to/project", "Hello Claude")
        print(f"Claude said: {output}")
    """
    stdout, stderr, return_code = run_claude_with_capture(
        path, input_string, wait_time, False
    )
    
    if return_code != 0:
        raise RuntimeError(f"Claude failed with code {return_code}: {stderr}")
    
    return stdout


if __name__ == "__main__":
    main()