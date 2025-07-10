#!/usr/bin/env python3
"""
Diagnose Claude CLI behavior
"""

import subprocess
import sys
import time
import os

def test_claude_direct():
    """Test Claude with direct subprocess call"""
    print("Test 1: Direct subprocess call")
    print("-" * 50)
    
    try:
        # Test if claude command exists
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        print(f"Claude path: {result.stdout.strip()}")
        
        # Check if it's executable
        claude_path = result.stdout.strip()
        if os.path.exists(claude_path):
            print(f"Executable: {os.access(claude_path, os.X_OK)}")
            
        # Try running claude with --help
        print("\nTesting 'claude --help':")
        result = subprocess.run(['claude', '--help'], capture_output=True, text=True, timeout=5)
        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr length: {len(result.stderr)}")
        if result.stderr:
            print(f"Stderr: {result.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
    except Exception as e:
        print(f"ERROR: {e}")

def test_claude_interactive():
    """Test Claude in interactive mode"""
    print("\n\nTest 2: Interactive mode test")
    print("-" * 50)
    
    try:
        # Start claude process
        proc = subprocess.Popen(
            ['claude'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        print(f"Process started with PID: {proc.pid}")
        
        # Check if process is running
        time.sleep(1)
        poll = proc.poll()
        print(f"Process status after 1s: {'Running' if poll is None else f'Exited with code {poll}'}")
        
        # Try to read any initial output
        print("\nChecking for initial output...")
        proc.stdout.flush()
        
        # Send a simple command
        print("\nSending test input...")
        proc.stdin.write("echo test\n")
        proc.stdin.flush()
        
        # Wait and check status
        time.sleep(2)
        poll = proc.poll()
        print(f"Process status after input: {'Running' if poll is None else f'Exited with code {poll}'}")
        
        # Terminate
        proc.terminate()
        proc.wait(timeout=5)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_claude_env():
    """Check environment variables"""
    print("\n\nTest 3: Environment check")
    print("-" * 50)
    
    important_vars = ['PATH', 'NODE_PATH', 'npm_config_prefix', 'HOME']
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        if var == 'PATH':
            # Show only paths containing node/npm
            paths = value.split(':')
            relevant = [p for p in paths if 'node' in p or 'npm' in p]
            print(f"{var}: {':'.join(relevant)}")
        else:
            print(f"{var}: {value}")

if __name__ == "__main__":
    test_claude_direct()
    test_claude_interactive()
    test_claude_env()