#!/usr/bin/env python3
"""
Test Claude with simple non-interactive mode
"""

import subprocess
import sys

def test_claude_print_mode():
    """Test Claude in print mode (non-interactive)"""
    print("Testing Claude in print mode")
    print("-" * 50)
    
    test_prompt = "echo 'Hello from Claude!'"
    
    try:
        # Use --print flag for non-interactive mode
        result = subprocess.run(
            ['claude', '--print', test_prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"\nStdout ({len(result.stdout)} chars):")
        print(result.stdout)
        print(f"\nStderr ({len(result.stderr)} chars):")
        print(result.stderr)
        
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_claude_print_mode()