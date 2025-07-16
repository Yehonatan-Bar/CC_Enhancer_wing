#!/usr/bin/env python3
"""
Simple Claude output capture using --print mode.
This avoids the complexity of interactive mode.
"""

import subprocess
import sys
import time
import os
import shlex
import platform
from pathlib import Path
from datetime import datetime


def capture_claude_print(prompt, path=".", timeout=300, verbose=False, skip_permissions=False):
    """
    Capture Claude's output using --print mode.
    
    Args:
        prompt: The prompt to send to Claude
        path: Directory to run Claude in
        timeout: Maximum time to wait for response
        verbose: Enable verbose output
        skip_permissions: Skip permission prompts (use with caution)
        
    Returns:
        tuple: (output, return_code)
    """
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        raise ValueError(f"Path '{path}' does not exist")
    
    # Use Windows claude path if on Windows, otherwise use Linux path
    if platform.system() == "Windows":
        claude_path = "claude"  # Use claude from PATH on Windows
    else:
        claude_path = "/home/laurelin/.npm-global/bin/claude"
    
    if verbose:
        print(f"[{datetime.now().isoformat()}] Running Claude in print mode", file=sys.stderr)
        print(f"[{datetime.now().isoformat()}] Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", file=sys.stderr)
    
    try:
        # Build command
        if platform.system() == "Windows":
            # On Windows, we need to use git-bash to run claude
            git_bash = os.environ.get('CLAUDE_CODE_GIT_BASH_PATH', r'C:\Program Files\Git\bin\bash.exe')
            cmd = [git_bash, '-c', f'claude --print {"--dangerously-skip-permissions" if skip_permissions else ""} {shlex.quote(prompt)}']
        else:
            cmd = [claude_path, '--print']
            if skip_permissions:
                cmd.append('--dangerously-skip-permissions')
            cmd.append(prompt)
        
        if verbose:
            print(f"[{datetime.now().isoformat()}] Command: {' '.join(cmd)}", file=sys.stderr)
        
        # Run Claude with --print flag
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
            timeout=timeout
        )
        
        if verbose:
            print(f"[{datetime.now().isoformat()}] Claude completed with code: {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"[{datetime.now().isoformat()}] Stderr: {result.stderr}", file=sys.stderr)
        
        return result.stdout, result.returncode
        
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"[{datetime.now().isoformat()}] Claude timed out after {timeout} seconds", file=sys.stderr)
        return "", -1
    except Exception as e:
        if verbose:
            print(f"[{datetime.now().isoformat()}] Error: {e}", file=sys.stderr)
        raise


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python capture_claude_simple.py <prompt> [--skip-permissions]")
        print("  --skip-permissions: Automatically approve all tool use (use with caution)")
        sys.exit(1)
    
    prompt = sys.argv[1]
    skip_permissions = '--skip-permissions' in sys.argv
    
    if skip_permissions:
        print("Warning: Running with --skip-permissions flag")
    
    print("Capturing Claude's response...")
    output, code = capture_claude_print(prompt, verbose=True, skip_permissions=skip_permissions)
    
    if code == 0:
        print("\n--- Claude's Response ---")
        print(output)
        print("--- End of Response ---")
    else:
        print(f"\nClaude failed with code: {code}")


if __name__ == "__main__":
    main()