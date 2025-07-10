#!/usr/bin/env python3
"""
Script that takes a file path as input and returns its content.
"""

import sys
import os
from pathlib import Path


def get_file_content(file_path, allowed_base_path=None):
    """
    Read and return the content of a file with security checks.
    
    Args:
        file_path (str): Path to the file to read
        allowed_base_path (str): Optional base path to restrict file access
        
    Returns:
        str: Content of the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permissions
        IsADirectoryError: If the path points to a directory
        ValueError: If the path is outside allowed base path or contains suspicious patterns
    """
    # Security: Resolve to absolute path and check for path traversal
    path = Path(file_path).resolve()
    
    # Security: Check for suspicious patterns
    suspicious_patterns = ['..', '~', '$', '|', ';', '&', '>', '<', '`']
    if any(pattern in str(file_path) for pattern in suspicious_patterns):
        raise ValueError(f"Suspicious pattern detected in path: {file_path}")
    
    # Security: Restrict to allowed base path if specified
    if allowed_base_path:
        allowed_base = Path(allowed_base_path).resolve()
        try:
            path.relative_to(allowed_base)
        except ValueError:
            raise ValueError(f"Path {file_path} is outside allowed base path {allowed_base_path}")
    
    # Security: Prevent access to sensitive system files
    sensitive_paths = ['/etc/passwd', '/etc/shadow', '/.ssh/', '/.gnupg/', '/.aws/']
    path_str = str(path)
    if any(sensitive in path_str for sensitive in sensitive_paths):
        raise PermissionError(f"Access to sensitive file denied: {file_path}")
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
    
    if not os.access(path, os.R_OK):
        raise PermissionError(f"No read permission for file: {file_path}")
    
    # Security: Limit file size to prevent memory exhaustion
    max_size = 100 * 1024 * 1024  # 100MB
    file_size = path.stat().st_size
    if file_size > max_size:
        raise ValueError(f"File too large ({file_size} bytes). Maximum allowed: {max_size} bytes")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try reading as binary if UTF-8 fails
        try:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            # Return binary representation if text reading fails
            with open(path, 'rb') as f:
                content = f.read()
                return f"[Binary file, size: {len(content)} bytes]"


def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python get_file_content.py <file_path> [allowed_base_path]", file=sys.stderr)
        print("  file_path: Path to the file to read", file=sys.stderr)
        print("  allowed_base_path: Optional base path to restrict file access", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    allowed_base_path = sys.argv[2] if len(sys.argv) == 3 else None
    
    try:
        content = get_file_content(file_path, allowed_base_path)
        print(content)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)
    except IsADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(4)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(5)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(6)


if __name__ == "__main__":
    main()