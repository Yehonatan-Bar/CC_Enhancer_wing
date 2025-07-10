#!/usr/bin/env python3
"""
Advanced terminal automation script with comprehensive error handling,
logging, and configuration options.
"""

import sys
import os
import time
import json
import logging
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

import click
import pyautogui


def convert_wsl_path(linux_path: str) -> str:
    """Convert WSL Linux path to Windows path format."""
    try:
        result = subprocess.run(['wslpath', '-w', linux_path], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If conversion fails, return original path
        return linux_path


# Configure logging
def setup_logging(verbose: bool, log_file: Optional[str] = None):
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = logging.DEBUG if verbose else logging.INFO
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


class Config:
    """Configuration management for the automation script."""
    
    DEFAULT_CONFIG = {
        "terminal_spawn_delay": 2,
        "claude_wait_time": 5,
        "failsafe": False,
        "terminal_preferences": {
            "wsl": ["wt.exe"],
            "linux": ["gnome-terminal", "konsole", "xterm", "terminator"],
            "darwin": ["Terminal"],
            "windows": ["cmd", "powershell"]
        },
        "keyboard_delay": 0.1
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
    
    def load_config(self, config_file: str):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
        except Exception as e:
            logging.warning(f"Failed to load config file: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)


class TerminalDetector:
    """Detect and manage terminal emulators across platforms."""
    
    @staticmethod
    def get_platform() -> str:
        """Get normalized platform name."""
        system = platform.system().lower()
        
        # Check if running in WSL
        if system == "linux" and os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
            return "wsl"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        elif system in ["windows", "win32"]:
            return "windows"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
    
    @staticmethod
    def find_terminal(preferences: List[str]) -> Optional[Tuple[str, List[str]]]:
        """Find available terminal from preferences list."""
        for terminal in preferences:
            if TerminalDetector._is_terminal_available(terminal):
                return terminal, TerminalDetector._get_terminal_command(terminal)
        return None
    
    @staticmethod
    def _is_terminal_available(terminal: str) -> bool:
        """Check if terminal is available on the system."""
        try:
            if platform.system().lower() == "windows":
                return True  # Assume cmd/powershell are always available
            
            # Special handling for wt.exe in WSL
            if terminal == "wt.exe":
                # Check if wt.exe is accessible
                result = subprocess.run(
                    ["which", "wt.exe"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            
            subprocess.run(
                [terminal, "--version"],
                capture_output=True,
                check=True,
                timeout=2
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def _get_terminal_command(terminal: str) -> List[str]:
        """Get the command to open terminal at specific directory."""
        commands = {
            "gnome-terminal": ["gnome-terminal", "--working-directory={path}"],
            "konsole": ["konsole", "--workdir", "{path}"],
            "xterm": ["xterm", "-e", "bash -c 'cd {path} && bash'"],
            "terminator": ["terminator", "--working-directory={path}"],
            "xfce4-terminal": ["xfce4-terminal", "--working-directory={path}"],
            "Terminal": ["open", "-a", "Terminal", "-n"],  # macOS
            "cmd": ["cmd", "/c", "start", "cmd", "/k", "cd /d {path}"],
            "powershell": ["powershell", "-Command", "Start-Process", "powershell", 
                          "-ArgumentList", "'-NoExit', '-Command', 'cd {path}'"],
            "wt.exe": ["wt.exe", "-d", "{path}"]  # Windows Terminal in WSL
        }
        return commands.get(terminal, [terminal])


class ClaudeAutomation:
    """Main automation class for running Claude in terminal."""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.platform = TerminalDetector.get_platform()
        
        # Configure pyautogui
        pyautogui.FAILSAFE = config.get("failsafe", False)
        pyautogui.PAUSE = config.get("keyboard_delay", 0.1)
    
    def validate_path(self, path: str) -> Path:
        """Validate and resolve the given path."""
        path_obj = Path(path).resolve()
        
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        # Check if path is accessible
        if not os.access(path_obj, os.R_OK | os.X_OK):
            raise PermissionError(f"No read/execute permission for: {path}")
        
        return path_obj
    
    def open_terminal(self, path: Path) -> bool:
        """Open terminal at the specified path."""
        self.logger.info(f"Opening terminal at: {path}")
        
        # Get terminal preferences for platform
        preferences = self.config.get("terminal_preferences", {}).get(self.platform, [])
        
        # Find available terminal
        terminal_info = TerminalDetector.find_terminal(preferences)
        if not terminal_info:
            raise RuntimeError(f"No supported terminal found for {self.platform}")
        
        terminal_name, command_template = terminal_info
        self.logger.debug(f"Using terminal: {terminal_name}")
        
        # Build command
        command = []
        path_str = str(path)
        
        # Convert path for WSL if using Windows Terminal
        if self.platform == "wsl" and terminal_name == "wt.exe":
            path_str = convert_wsl_path(path_str)
            self.logger.debug(f"Converted WSL path to: {path_str}")
        
        for part in command_template:
            if "{path}" in part:
                command.append(part.format(path=path_str))
            else:
                command.append(part)
        
        try:
            # Special handling for macOS
            if self.platform == "darwin":
                apple_script = f'tell application "Terminal" to do script "cd {path}"'
                subprocess.Popen(["osascript", "-e", apple_script])
            else:
                subprocess.Popen(command)
            
            self.logger.info("Terminal opened successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open terminal: {e}")
            raise
    
    def execute_automation(self, path: str, input_string: str, dry_run: bool = False):
        """Execute the main automation sequence."""
        # Validate path
        validated_path = self.validate_path(path)
        
        if dry_run:
            self.logger.info("DRY RUN MODE - No actions will be performed")
            self.logger.info(f"Would open terminal at: {validated_path}")
            self.logger.info(f"Would type: claude")
            self.logger.info(f"Would wait: {self.config.get('claude_wait_time')} seconds")
            self.logger.info(f"Would type: {input_string}")
            self.logger.info("Would press: Enter")
            return
        
        # Open terminal
        self.open_terminal(validated_path)
        
        # Wait for terminal to spawn
        spawn_delay = self.config.get("terminal_spawn_delay", 2)
        self.logger.info(f"Waiting {spawn_delay}s for terminal to spawn...")
        time.sleep(spawn_delay)
        
        # Type claude command with full path
        self.logger.info("Typing 'claude' command...")
        # Use full path to claude to avoid PATH issues
        claude_path = "/home/laurelin/.npm-global/bin/claude"
        if os.path.exists(claude_path):
            pyautogui.typewrite(claude_path)
        else:
            # Fallback to just 'claude' if full path doesn't exist
            pyautogui.typewrite("claude")
        pyautogui.press("enter")
        
        # Wait as specified
        wait_time = self.config.get("claude_wait_time", 5)
        self.logger.info(f"Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
        # Type input string
        self.logger.info(f"Typing input: {input_string}")
        pyautogui.typewrite(input_string)
        
        # Press Enter
        self.logger.info("Pressing Enter...")
        pyautogui.press("enter")
        
        self.logger.info("Automation completed successfully!")


@click.command()
@click.argument('path', type=click.Path(exists=False))  # We'll validate manually
@click.argument('input_string')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--dry-run', is_flag=True, help='Show what would be done without doing it')
@click.option('--config', type=click.Path(exists=True), help='Path to JSON config file')
@click.option('--log-file', type=click.Path(), help='Path to log file')
@click.option('--spawn-delay', type=float, help='Override terminal spawn delay (seconds)')
@click.option('--wait-time', type=float, help='Override Claude wait time (seconds)')
def main(path, input_string, verbose, dry_run, config, log_file, spawn_delay, wait_time):
    """
    Advanced Claude terminal automation with comprehensive error handling.
    
    Opens a terminal at PATH, runs 'claude' command, waits 5 seconds,
    then enters INPUT_STRING and presses Enter.
    
    Examples:
    
        # Basic usage
        python run_claude_advanced.py /home/user/project "Hello Claude"
        
        # With verbose output
        python run_claude_advanced.py -v /home/user/project "Hello Claude"
        
        # Dry run to see what would happen
        python run_claude_advanced.py --dry-run /home/user/project "Test"
        
        # With custom config file
        python run_claude_advanced.py --config config.json /path "Input"
    """
    
    # Set up logging
    logger = setup_logging(verbose, log_file)
    
    # Load configuration
    config_obj = Config(config)
    
    # Override config with command line options
    if spawn_delay is not None:
        config_obj.config["terminal_spawn_delay"] = spawn_delay
    if wait_time is not None:
        config_obj.config["claude_wait_time"] = wait_time
    
    # Create automation instance
    automation = ClaudeAutomation(config_obj, logger)
    
    try:
        # Execute automation
        automation.execute_automation(path, input_string, dry_run)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
        
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        if verbose:
            logger.exception("Full error trace:")
        sys.exit(1)


if __name__ == "__main__":
    main()