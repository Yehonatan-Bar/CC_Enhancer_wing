#!/usr/bin/env python3
"""
Alternative terminal automation using pexpect for better control.
This approach provides more reliable terminal interaction.
"""

import sys
import os
import time
import click
import platform
from pathlib import Path

try:
    import pexpect
except ImportError:
    print("Error: pexpect not installed. Run: pip install pexpect")
    sys.exit(1)


class TerminalAutomation:
    """Handle terminal automation with pexpect."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.terminal = None
        
    def log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            click.echo(f"[DEBUG] {message}")
    
    def spawn_terminal(self, working_dir):
        """Spawn a new terminal session in the specified directory."""
        self.log(f"Spawning terminal in: {working_dir}")
        
        # Change to the specified directory first
        original_dir = os.getcwd()
        os.chdir(working_dir)
        
        try:
            if platform.system().lower() == "windows":
                # pexpect doesn't work well on Windows, use subprocess instead
                import subprocess
                subprocess.Popen(["cmd", "/k", "cd /d", working_dir])
                time.sleep(2)
                return None
            else:
                # Spawn a bash shell
                self.terminal = pexpect.spawn('/bin/bash', encoding='utf-8')
                self.terminal.setwinsize(24, 80)
                
                # Wait for prompt
                self.terminal.expect(['\\$', '#', '>'], timeout=5)
                
                # Ensure we're in the right directory
                self.terminal.sendline(f'cd "{working_dir}"')
                self.terminal.expect(['\\$', '#', '>'], timeout=5)
                
                self.log("Terminal spawned successfully")
                return self.terminal
        finally:
            os.chdir(original_dir)
    
    def run_claude_command(self, input_string, working_dir):
        """Run the claude command and send input after delay."""
        
        if platform.system().lower() == "windows":
            # Fallback to pyautogui on Windows
            self.log("Windows detected, using GUI automation fallback")
            self._windows_fallback(input_string)
            return None  # Can't capture output on Windows with pyautogui
        
        # Spawn terminal
        term = self.spawn_terminal(working_dir)
        if not term:
            raise RuntimeError("Failed to spawn terminal")
        
        captured_output = []
        
        try:
            # Send claude command
            self.log("Sending 'claude' command...")
            term.sendline('claude')
            
            # Wait 5 seconds as requested
            self.log("Waiting 5 seconds...")
            time.sleep(5)
            
            # Send the input string
            self.log(f"Sending input: {input_string}")
            term.sendline(input_string)
            
            # Capture output with a longer timeout
            self.log("Capturing Claude's response...")
            output_buffer = ""
            start_time = time.time()
            timeout_seconds = 30  # Maximum time to wait for Claude's response
            
            while time.time() - start_time < timeout_seconds:
                try:
                    # Try to read any available output
                    index = term.expect([pexpect.TIMEOUT, pexpect.EOF, '\n'], timeout=1)
                    if index == 0:  # Timeout - check if we should continue
                        if term.before:
                            output_buffer += term.before
                            term.before = ""
                        # Check if Claude seems to be done (no output for 2 seconds)
                        if len(captured_output) > 0 and time.time() - start_time > 5:
                            break
                    elif index == 1:  # EOF
                        if term.before:
                            output_buffer += term.before
                        break
                    elif index == 2:  # Newline
                        if term.before:
                            output_buffer += term.before + '\n'
                            captured_output.append(term.before)
                            term.before = ""
                except:
                    # Continue on any error
                    pass
            
            # Get any remaining output
            try:
                term.expect(pexpect.TIMEOUT, timeout=0.5)
                if term.before:
                    output_buffer += term.before
                    captured_output.extend(term.before.split('\n'))
            except:
                pass
            
            # Clean up the output
            full_output = '\n'.join(captured_output).strip()
            
            self.log("Command execution completed")
            self.log(f"Captured output length: {len(full_output)} characters")
            
            return full_output
            
        except pexpect.exceptions.TIMEOUT:
            self.log("Warning: Terminal response timeout")
            return '\n'.join(captured_output) if captured_output else None
        except Exception as e:
            self.log(f"Error during execution: {e}")
            raise
        finally:
            if term and term.isalive():
                term.close()
    
    def _windows_fallback(self, input_string):
        """Fallback method for Windows using pyautogui."""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            
            time.sleep(2)
            pyautogui.typewrite("claude")
            pyautogui.press("enter")
            time.sleep(5)
            pyautogui.typewrite(input_string)
            pyautogui.press("enter")
        except ImportError:
            raise RuntimeError("pyautogui required for Windows support")


@click.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, 
                                       dir_okay=True, resolve_path=True))
@click.argument('input_string')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--timeout', default=30, help='Overall timeout in seconds')
def main(path, input_string, verbose, timeout):
    """
    Run claude command in a terminal at PATH with automated input.
    
    This implementation uses pexpect for better terminal control
    compared to GUI automation.
    
    Example:
        python run_claude_pexpect.py /home/user/project "Hello Claude"
    """
    
    # Validate path
    path_obj = Path(path)
    if not path_obj.exists():
        click.echo(f"Error: Path '{path}' does not exist", err=True)
        sys.exit(1)
    
    if not path_obj.is_dir():
        click.echo(f"Error: Path '{path}' is not a directory", err=True)
        sys.exit(1)
    
    # Create automation instance
    automation = TerminalAutomation(verbose=verbose)
    
    try:
        # Set overall timeout
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Operation timed out")
        
        if platform.system().lower() != "windows":
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        # Run the automation
        output = automation.run_claude_command(input_string, str(path_obj))
        
        if platform.system().lower() != "windows":
            signal.alarm(0)  # Cancel timeout
        
        # Print the captured output to stdout
        if output:
            click.echo("\n=== Claude's Response ===")
            click.echo(output)
            click.echo("=== End of Response ===\n")
        else:
            if verbose:
                click.echo("No output captured from Claude")
        
        if verbose:
            click.echo("Automation completed successfully!")
            
    except TimeoutError:
        click.echo("Error: Operation timed out", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()