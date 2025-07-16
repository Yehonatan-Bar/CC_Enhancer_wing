#!/usr/bin/env python3
"""
Test raw Claude subprocess to see all output
"""

import subprocess
import threading
import time
import sys

def read_stream(stream, name):
    """Read from a stream and print with labels"""
    try:
        while True:
            data = stream.read(1)  # Read one character at a time
            if not data:
                break
            print(f"[{name}] {repr(data)}", end='', flush=True)
    except Exception as e:
        print(f"\n[{name} ERROR] {e}")

def main():
    print("Starting raw Claude subprocess test")
    print("-" * 50)
    
    # Start Claude
    proc = subprocess.Popen(
        ['claude'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    print(f"Process started with PID: {proc.pid}")
    
    # Start threads to read output
    stdout_thread = threading.Thread(target=read_stream, args=(proc.stdout, 'STDOUT'))
    stderr_thread = threading.Thread(target=read_stream, args=(proc.stderr, 'STDERR'))
    
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    
    stdout_thread.start()
    stderr_thread.start()
    
    # Wait a bit to see initial output
    print("\nWaiting 5 seconds for initial output...")
    time.sleep(5)
    
    # Send test input
    print("\n\nSending test input: 'echo test'")
    proc.stdin.write("echo test\n")
    proc.stdin.flush()
    
    # Wait for response
    print("\nWaiting 5 seconds for response...")
    time.sleep(5)
    
    # Terminate
    print("\n\nTerminating process...")
    proc.terminate()
    proc.wait(timeout=5)
    
    print("\nTest complete")

if __name__ == "__main__":
    main()