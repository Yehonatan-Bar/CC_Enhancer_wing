#!/usr/bin/env python3
"""
Test if Claude needs a pseudo-terminal (PTY)
"""

import os
import pty
import subprocess
import select
import time
import sys

def test_with_pty():
    """Test Claude with a pseudo-terminal"""
    print("Testing Claude with PTY")
    print("-" * 50)
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    try:
        # Start Claude with PTY
        proc = subprocess.Popen(
            ['claude'],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            close_fds=True
        )
        
        print(f"Process started with PID: {proc.pid}")
        
        # Close slave end in parent
        os.close(slave)
        
        # Make master non-blocking
        import fcntl
        flags = fcntl.fcntl(master, fcntl.F_GETFL)
        fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Read initial output
        print("\nReading initial output...")
        time.sleep(2)
        
        output = []
        while True:
            try:
                data = os.read(master, 1024).decode('utf-8', errors='replace')
                if data:
                    output.append(data)
                    print(f"Got: {repr(data)}")
                else:
                    break
            except BlockingIOError:
                break
        
        if output:
            print(f"\nInitial output received ({len(''.join(output))} chars)")
        else:
            print("\nNo initial output")
        
        # Send test command
        print("\nSending command: 'echo test'")
        os.write(master, b"echo test\n")
        
        # Read response
        time.sleep(3)
        print("\nReading response...")
        
        response = []
        while True:
            try:
                data = os.read(master, 1024).decode('utf-8', errors='replace')
                if data:
                    response.append(data)
                    print(f"Got: {repr(data)}")
                else:
                    break
            except BlockingIOError:
                break
                
        if response:
            print(f"\nResponse received ({len(''.join(response))} chars)")
        else:
            print("\nNo response")
        
        # Cleanup
        proc.terminate()
        proc.wait(timeout=5)
        os.close(master)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_pty()