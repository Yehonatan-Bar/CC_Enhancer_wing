#!/usr/bin/env python3
"""
Test Claude auto-responder with enhanced logging to diagnose issues.
"""

from claude_auto_responder import ClaudeAutoResponder
import sys
import json

def main():
    print("Testing Claude auto-responder with detailed logging")
    print("-" * 50)
    
    # Create responder with verbose mode
    responder = ClaudeAutoResponder(verbose=True)
    
    # Simple test command
    test_input = "echo 'Hello from Claude!'"
    
    try:
        print(f"\nRunning test with input: {test_input}")
        print("-" * 50)
        
        # Run with shorter timeout for testing
        output, return_code = responder.run_claude_interactive(
            path=".",
            initial_input=test_input,
            wait_time=2,
            timeout=30  # 30 second timeout
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
    
    finally:
        # Always save logs for analysis
        log_file = "claude_debug_logs.json"
        responder.save_logs(log_file)
        print(f"\n\nDebug logs saved to: {log_file}")
        
        # Print summary of logs
        print("\nLog Summary:")
        print("-" * 30)
        by_feature = {}
        for log in responder.logs:
            feature = log['feature']
            if feature not in by_feature:
                by_feature[feature] = 0
            by_feature[feature] += 1
        
        for feature, count in sorted(by_feature.items()):
            print(f"  {feature}: {count} entries")

if __name__ == "__main__":
    main()