#!/usr/bin/env python3
"""
Test script demonstrating how to capture Claude's output.
"""

import subprocess
import os
import json


def test_method_1():
    """Test using capture_claude_output.py"""
    print("Method 1: Using capture_claude_output.py")
    print("-" * 50)
    
    # Run the capture script
    result = subprocess.run([
        "python3", "capture_claude_output.py",
        os.getcwd(),
        "What is 2+2?",
        "--wait-time", "2"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print()


def test_method_2():
    """Test using run_claude_capture.py with JSON output"""
    print("Method 2: Using run_claude_capture.py with JSON")
    print("-" * 50)
    
    # Run with JSON output for easy parsing
    result = subprocess.run([
        "python3", "run_claude_capture.py",
        os.getcwd(),
        "List Python files",
        "--json-output",
        "--wait-time", "2"
    ], capture_output=True, text=True)
    
    try:
        # Parse JSON output
        output_data = json.loads(result.stdout)
        print(f"Success: {output_data['success']}")
        print(f"Return code: {output_data['returncode']}")
        print(f"Output length: {len(output_data['stdout'])} characters")
        
        # Store Claude's response in a variable
        claude_response = output_data['stdout']
        print(f"\nClaude's response (first 200 chars):")
        print(claude_response[:200] + "..." if len(claude_response) > 200 else claude_response)
        
    except json.JSONDecodeError:
        print("Failed to parse JSON output")
        print(result.stdout)
    print()


def test_method_3():
    """Test programmatic import"""
    print("Method 3: Direct import and function call")
    print("-" * 50)
    
    try:
        from capture_claude_output import capture_claude_output
        
        # Call Claude and get output directly
        output = capture_claude_output(
            path=os.getcwd(),
            input_string="Show me the current directory",
            wait_time=2
        )
        
        # Now 'output' contains Claude's response
        print(f"Captured output (first 200 chars):")
        print(output[:200] + "..." if len(output) > 200 else output)
        
        # You can process this output however you need
        lines = output.strip().split('\n')
        print(f"\nNumber of lines in response: {len(lines)}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Testing Claude output capture methods\n")
    
    # Test each method
    test_method_1()
    test_method_2()
    test_method_3()
    
    print("\nAll tests completed!")