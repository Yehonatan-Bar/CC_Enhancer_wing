#!/usr/bin/env python3
"""
Simple test to verify live output from Claude auto-responder.
"""

from claude_auto_responder import ClaudeAutoResponder
import sys

def main():
    print("Testing Claude auto-responder with live output")
    print("-" * 50)
    
    # Create responder with verbose mode
    responder = ClaudeAutoResponder(verbose=True)
    
    # Simple test command
    test_input = "echo 'Hello from Claude!'"
    
    try:
        print(f"\nRunning test with input: {test_input}")
        print("-" * 50)
        
        output, return_code = responder.run_claude_interactive(
            path=".",
            initial_input=test_input,
            wait_time=2  # Shorter wait time for testing
        )
        
        print("\n" + "-" * 50)
        print(f"Test completed with return code: {return_code}")
        print(f"Total output length: {len(output)} characters")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()