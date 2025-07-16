#!/usr/bin/env python3
"""
Script to interact with Claude and automatically respond to permission prompts.
Detects when Claude asks "Do you want to..." and responds with "1".
"""

import subprocess
import sys
import os
import time
import select
import threading
import queue
from pathlib import Path
import click
import re
from datetime import datetime
import json


class ClaudeAutoResponder:
    """Handles automated responses to Claude's permission prompts."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.permission_pattern = re.compile(r'Do you want to.*\?', re.IGNORECASE)
        self.output_queue = queue.Queue()
        self.process = None
        self.logs = []
        
    def log(self, message, feature="subprocess", module="auto_responder", **kwargs):
        """Enhanced logging with tags and parameters."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "feature": feature,
            "module": module,
            "message": message,
            "parameters": kwargs
        }
        self.logs.append(log_entry)
        
        if self.verbose:
            params_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            if params_str:
                print(f"[{timestamp}] [{feature}:{module}] {message} ({params_str})", file=sys.stderr)
            else:
                print(f"[{timestamp}] [{feature}:{module}] {message}", file=sys.stderr)
    
    def detect_permission_prompt(self, text):
        """Check if the text contains a permission prompt."""
        return bool(self.permission_pattern.search(text))
    
    def read_output(self, pipe, name):
        """Read output from a pipe in a separate thread."""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    self.output_queue.put((name, line))
                    if name == 'stderr' and self.verbose:
                        self.log("Received stderr output", feature="output", module="reader", content=line.strip())
        except Exception as e:
            if self.verbose:
                self.log("Error reading pipe", feature="error", module="reader", pipe_name=name, error=str(e))
        finally:
            pipe.close()
    
    def save_logs(self, filepath):
        """Save logs to a JSON file for analysis."""
        with open(filepath, 'w') as f:
            json.dump(self.logs, f, indent=2)
        self.log("Logs saved", feature="logging", module="saver", filepath=filepath, count=len(self.logs))
    
    def run_claude_interactive(self, path, initial_input, wait_time=5, timeout=300):
        """
        Run Claude interactively and respond to permission prompts.
        
        Args:
            path: Directory to run Claude in
            initial_input: Initial input to send to Claude
            wait_time: Time to wait before sending initial input
            timeout: Maximum time to wait for Claude response (default 300s)
            
        Returns:
            tuple: (full_output, return_code)
        """
        # Validate path
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValueError(f"Path '{path}' does not exist")
        
        # Full path to claude
        claude_path = "/home/laurelin/.npm-global/bin/claude"
        
        self.log("Starting Claude subprocess", feature="startup", module="main", path=str(path), input=initial_input)
        
        # Start Claude process
        self.log("Creating subprocess", feature="startup", module="main", command=claude_path)
        try:
            self.process = subprocess.Popen(
                [claude_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=path,
                bufsize=1,
                universal_newlines=True
            )
            self.log("Subprocess created", feature="startup", module="main", pid=self.process.pid)
        except Exception as e:
            self.log("Failed to create subprocess", feature="error", module="main", error=str(e))
            raise
        
        # Start threads to read output
        stdout_thread = threading.Thread(
            target=self.read_output, 
            args=(self.process.stdout, 'stdout')
        )
        stderr_thread = threading.Thread(
            target=self.read_output,
            args=(self.process.stderr, 'stderr')
        )
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        # Show starting indicator
        print(f"Starting Claude instance...", file=sys.stderr)
        
        # Collect all output
        full_output = []
        permission_detected = False
        initial_sent = False
        start_time = time.time()
        last_wait_message = 0
        
        last_activity = time.time()
        output_count = 0
        initial_output_received = False
        
        try:
            while True:
                # Check if process has terminated
                poll_result = self.process.poll()
                if poll_result is not None:
                    self.log("Process terminated", feature="lifecycle", module="monitor", 
                            return_code=poll_result, duration=time.time()-start_time)
                    break
                
                # Check for timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    self.log("Process timeout", feature="timeout", module="monitor",
                            duration=elapsed_time, timeout=timeout)
                    print(f"\n[ERROR] Claude process timed out after {timeout} seconds", file=sys.stderr)
                    self.process.terminate()
                    break
                
                # Log process status periodically
                if time.time() - last_activity > 10:
                    self.log("Process still running", feature="heartbeat", module="monitor",
                            duration=elapsed_time, output_count=output_count)
                    last_activity = time.time()
                
                # Wait for initial output or timeout before sending input
                if not initial_sent:
                    elapsed = time.time() - start_time
                    
                    # Send input either after wait_time OR when we receive initial output
                    should_send = (elapsed >= wait_time) or (initial_output_received and elapsed >= 1)
                    
                    if should_send:
                        print(f"\nSending request to Claude: {initial_input[:50]}{'...' if len(initial_input) > 50 else ''}", file=sys.stderr)
                        self.log("Sending initial input", feature="input", module="main", 
                                input_length=len(initial_input), waited=elapsed, 
                                initial_output=initial_output_received)
                        self.process.stdin.write(initial_input + '\n')
                        self.process.stdin.flush()
                        initial_sent = True
                        print("Claude is processing your request...\n", file=sys.stderr)
                    else:
                        # Show waiting message
                        if elapsed - last_wait_message >= 1:  # Update every second
                            remaining = wait_time - elapsed
                            if remaining > 0:
                                status = " (waiting for prompt)" if not initial_output_received else ""
                                print(f"\rWaiting {remaining:.0f}s before sending input{status}...", end='', file=sys.stderr)
                                last_wait_message = elapsed
                
                # Process any output
                try:
                    source, line = self.output_queue.get(timeout=0.1)
                    full_output.append(line)
                    output_count += 1
                    last_activity = time.time()
                    
                    # Mark that we've received initial output
                    if not initial_output_received:
                        initial_output_received = True
                        self.log("Initial output received", feature="output", module="processor",
                                source=source, content_preview=line[:50])
                    
                    self.log("Received output", feature="output", module="processor", 
                            source=source, line_length=len(line), total_lines=output_count)
                    
                    # Print output in real-time
                    if source == 'stdout':
                        print(line, end='', flush=True)
                    elif source == 'stderr' and line.strip():
                        # Show stderr as well (might contain important info)
                        print(f"[STDERR] {line}", end='', file=sys.stderr, flush=True)
                    
                    # Check for permission prompt
                    if self.detect_permission_prompt(line):
                        self.log("Permission prompt detected", feature="permission", module="detector", prompt=line.strip())
                        permission_detected = True
                        
                        # Wait a moment for the full prompt to appear
                        time.sleep(0.5)
                        
                        # Send "1" as response
                        self.log("Auto-responding with '1'", feature="permission", module="responder")
                        self.process.stdin.write('1\n')
                        self.process.stdin.flush()
                        permission_detected = False
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    self.log("Error processing output", feature="error", module="main", error=str(e))
        
        except KeyboardInterrupt:
            self.log("Process interrupted by user", feature="interrupt", module="main")
            self.process.terminate()
            raise
        
        finally:
            # Wait for process to complete
            return_code = self.process.wait()
            
            # Drain any remaining output
            while not self.output_queue.empty():
                try:
                    source, line = self.output_queue.get_nowait()
                    full_output.append(line)
                    if source == 'stdout':
                        print(line, end='', flush=True)
                except:
                    break
        
        return ''.join(full_output), return_code


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('input_string')
@click.option('--wait-time', default=5, help='Wait time before sending initial input (seconds)')
@click.option('--timeout', default=300, help='Maximum time to wait for Claude response (seconds)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--save-to', type=click.Path(), help='Save output to file')
@click.option('--save-logs', type=click.Path(), help='Save debug logs to JSON file')
def main(path, input_string, wait_time, timeout, verbose, save_to, save_logs):
    """
    Run Claude with automatic response to permission prompts.
    
    When Claude asks "Do you want to...", this script automatically responds with "1".
    
    Examples:
        python claude_auto_responder.py /home/user/project "Implement feature X"
        python claude_auto_responder.py . "Fix the bug" --verbose
    """
    try:
        # Create auto-responder instance
        responder = ClaudeAutoResponder(verbose=verbose)
        
        # Run Claude with auto-response
        output, return_code = responder.run_claude_interactive(
            path, input_string, wait_time, timeout
        )
        
        if return_code != 0:
            print(f"\nClaude exited with code: {return_code}", file=sys.stderr)
        
        # Save to file if requested
        if save_to:
            with open(save_to, 'w') as f:
                f.write(output)
            print(f"\nOutput saved to: {save_to}")
        
        # Save logs if requested
        if save_logs:
            responder.save_logs(save_logs)
            print(f"Debug logs saved to: {save_logs}")
        
        return output
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()