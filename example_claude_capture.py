#!/usr/bin/env python3
"""
Examples of capturing Claude's output programmatically.
"""

import sys
import time
sys.path.insert(0, 'bin')
from capture_claude_simple import capture_claude_print


def example_simple_capture():
    """Example 1: Simple capture using --print mode (recommended)"""
    print("Example 1: Simple Claude capture (using --print mode)")
    print("-" * 60)
    
    # Example prompts
    prompts = [
        "echo 'Hello World'",
        "What is 2 + 2?",
        "List 3 benefits of Python"
    ]
    
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        print("Response: ", end="")
        
        # Capture Claude's response
        output, return_code = capture_claude_print(prompt, verbose=False)
        
        if return_code == 0:
            # Process the output
            lines = output.strip().split('\n')
            if len(lines) == 1:
                print(lines[0])
            else:
                print(f"\n{output.strip()}")
        else:
            print(f"[Error: Claude returned code {return_code}]")
        
        time.sleep(1)  # Be nice to the API


def example_batch_processing():
    """Example 2: Batch processing multiple files"""
    print("\n\nExample 2: Batch processing with Claude")
    print("-" * 60)
    
    # Simulate processing multiple files
    files_to_analyze = [
        "claude_auto_responder.py",
        "capture_claude_simple.py"
    ]
    
    for filename in files_to_analyze:
        prompt = f"Briefly describe what {filename} does in one sentence"
        print(f"\nAnalyzing: {filename}")
        
        output, return_code = capture_claude_print(prompt)
        
        if return_code == 0:
            print(f"Description: {output.strip()}")
        else:
            print(f"Failed to analyze {filename}")


def example_code_generation():
    """Example 3: Using Claude for code generation"""
    print("\n\nExample 3: Code generation with Claude")
    print("-" * 60)
    
    prompt = "Write a Python function that calculates factorial recursively"
    
    print("Requesting code generation...")
    output, return_code = capture_claude_print(prompt)
    
    if return_code == 0:
        print("\nGenerated code:")
        print(output)
        
        # You could save this to a file
        # with open('generated_factorial.py', 'w') as f:
        #     f.write(output)
    else:
        print("Code generation failed")


def example_with_context():
    """Example 4: Running Claude with specific directory context"""
    print("\n\nExample 4: Claude with directory context")
    print("-" * 60)
    
    # Run Claude in the current directory to analyze project
    prompt = "What type of project is this based on the files you can see?"
    
    print("Analyzing current directory...")
    output, return_code = capture_claude_print(
        prompt, 
        path=".",  # Current directory
        verbose=True
    )
    
    if return_code == 0:
        print(f"\nAnalysis: {output.strip()}")


def main():
    """Run all examples"""
    print("Claude Output Capture Examples")
    print("=" * 60)
    
    # Run examples
    example_simple_capture()
    example_batch_processing()
    example_code_generation()
    example_with_context()
    
    print("\n\nAll examples completed!")
    print("\nNote: For interactive mode with permission prompts, use claude_auto_responder_pty.py")


if __name__ == "__main__":
    main()