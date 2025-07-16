#!/usr/bin/env python3
"""
Test script for the Claude auto-responder functionality.
"""

import sys
import re
import time


def simulate_claude_permission_prompt():
    """Simulate Claude's behavior with permission prompts."""
    print("Welcome to Claude!")
    print("Processing your request...")
    time.sleep(1)
    
    # Simulate a permission prompt
    print("\nDo you want to proceed with the following actions?")
    print("1. Create a new file")
    print("2. Modify existing code")
    print("3. Cancel")
    print("\nPlease enter your choice (1-3): ", end='', flush=True)
    
    # Wait for input
    choice = input()
    
    if choice == "1":
        print("\nGreat! Proceeding with the actions...")
        print("Creating new file...")
        print("Task completed successfully!")
    else:
        print(f"\nYou selected: {choice}")
        print("Operation cancelled.")


def test_pattern_detection():
    """Test the regex pattern for detecting permission prompts."""
    test_cases = [
        ("Do you want to proceed?", True),
        ("Do you want to create a new file?", True),
        ("Do you want to continue with these changes?", True),
        ("What do you think about this?", False),
        ("This is a normal message", False),
        ("I'll do this for you", False),
        ("DO YOU WANT TO PROCEED?", True),  # Case insensitive
    ]
    
    pattern = re.compile(r'Do you want to.*\?', re.IGNORECASE)
    
    print("Testing permission prompt detection:")
    print("-" * 50)
    
    for text, expected in test_cases:
        detected = bool(pattern.search(text))
        status = "✓" if detected == expected else "✗"
        print(f"{status} '{text}' -> Detected: {detected}")
    
    print("-" * 50)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test-pattern":
        test_pattern_detection()
    else:
        simulate_claude_permission_prompt()