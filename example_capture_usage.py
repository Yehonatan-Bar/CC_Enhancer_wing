#!/usr/bin/env python3
"""
Example of how to capture Claude's output programmatically.
"""

from capture_claude_output import capture_claude_output
from claude_auto_responder import ClaudeAutoResponder
import os


def main():
    # Example 1: Simple capture with auto-response to permission prompts
    print("Example 1: Capturing Claude's response with auto-responder")
    print("-" * 50)
    
    try:
        # Create auto-responder instance
        responder = ClaudeAutoResponder(verbose=True)
        
        # Run Claude with auto-response capability
        output, return_code = responder.run_claude_interactive(
            path="/home/laurelin/projects/code_enhancer",  # Current directory
            initial_input="create an empty file with the name 'test.txt' ",
            wait_time=3
        )
        
        # Store in a variable
        claude_response = output.strip()
        print(f"\nClaude's response captured successfully!")
        print(f"Return code: {return_code}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50 + "\n")
    
    # Example 2: More complex interaction
    print("Example 2: Asking Claude to analyze a file")
    print("-" * 50)
    
    try:
        # Prepare a more complex query
        query = "tell me about this app"
        
        # Capture Claude's output
        output = capture_claude_output(
            path="/home/laurelin/projects/code_enhancer",
            input_string=query,
            wait_time=3
        )
        
        # Process the output
        lines = output.strip().split('\n')
        print(f"Claude provided {len(lines)} lines of output")
        print(f"First line: {lines[0] if lines else 'No output'}")
        
        # You can now parse or process claude_response as needed
        # For example, extract file names, parse structured data, etc.
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()