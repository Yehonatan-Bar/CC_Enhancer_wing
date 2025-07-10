#!/usr/bin/env python3
"""
Simple Claude wrapper that always auto-approves permissions.
For when you trust the operations and want minimal friction.
"""

import sys
sys.path.insert(0, 'bin')
from capture_claude_simple import capture_claude_print


def main():
    if len(sys.argv) < 2:
        print("Usage: python claude_auto.py <prompt>")
        print("\nThis always runs with auto-permissions enabled!")
        print("Example: python claude_auto.py 'create hello.py'")
        sys.exit(1)
    
    prompt = ' '.join(sys.argv[1:])  # Join all args as prompt
    
    # Always use permissions
    output, code = capture_claude_print(
        prompt,
        skip_permissions=True,
        verbose=False
    )
    
    if code == 0:
        print(output)
    else:
        print(f"Error: Claude returned code {code}", file=sys.stderr)
        sys.exit(code)


if __name__ == "__main__":
    main()