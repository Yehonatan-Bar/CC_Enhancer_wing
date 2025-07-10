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
        TypeError: If input types are invalid
    """
    # Validate input types
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    if allowed_base_path is not None and not isinstance(allowed_base_path, str):
        raise TypeError("allowed_base_path must be a string or None")
    
    # Security: Resolve to absolute path and check for path traversal
    path = Path(file_path).resolve()
    
    # Security: Check for suspicious patterns in both original and resolved path
    suspicious_patterns = ['..', '~', '$', '|', ';', '&', '>', '<', '`']
    if any(pattern in str(file_path) for pattern in suspicious_patterns):
        raise ValueError("Invalid path pattern detected")
    if any(pattern in str(path) for pattern in suspicious_patterns):
        raise ValueError("Invalid resolved path pattern detected")
    
    # Security: Check for symbolic links
    if Path(file_path).exists() and Path(file_path).is_symlink():
        # Additional validation for symlink target
        link_target = path
        if any(pattern in str(link_target) for pattern in suspicious_patterns):
            raise ValueError("Symbolic link points to suspicious location")
    
    # Security: Restrict to allowed base path if specified
    if allowed_base_path:
        allowed_base = Path(allowed_base_path).resolve()
        if not allowed_base.exists() or not allowed_base.is_dir():
            raise ValueError("Invalid base path specified")
        try:
            path.relative_to(allowed_base)
        except ValueError:
            raise ValueError("Path is outside allowed base path")
    
    # Security: Prevent access to sensitive system files
    sensitive_paths = ['/etc/', '/root/', '/.ssh/', '/.kube/', '/.gnupg/', '/.aws/', 
                      '/proc/', '/sys/', '/dev/', '/var/log/', '/.config/',
                      'C:\\Windows\\System32\\', 'C:\\ProgramData\\', 'C:\\Users\\Administrator\\']
    path_str = str(path).replace('\\', '/')  # Normalize for comparison
    if any(path_str.startswith(sensitive) or sensitive in path_str for sensitive in sensitive_paths):
        raise PermissionError("Access to sensitive location denied")
    
    # Use a single file operation to minimize TOCTOU window
    try:
        # Get file stats in one operation
        stat_info = path.stat()
        
        if not path.exists():
            raise FileNotFoundError("File not found")
        
        if path.is_dir():
            raise IsADirectoryError("Path is a directory, not a file")
        
        if not os.access(path, os.R_OK):
            raise PermissionError("No read permission for file")
        
        # Security: Limit file size to prevent memory exhaustion
        max_size = 100 * 1024 * 1024  # 100MB
        file_size = stat_info.st_size
        if file_size > max_size:
            raise ValueError(f"File too large ({file_size} bytes). Maximum: {max_size} bytes")
        
        # Try to read as text first
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try reading as Latin-1 if UTF-8 fails
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                # For binary files, don't read entire content into memory
                with open(path, 'rb') as f:
                    # Read only first 1KB for sample
                    sample = f.read(1024)
                    return f"[Binary file, size: {file_size} bytes]"
    
    except (FileNotFoundError, PermissionError, IsADirectoryError, ValueError):
        # Re-raise these specific exceptions without exposing system paths
        raise
    except Exception as e:
        # Generic error without exposing system information
        raise Exception("Unable to read file") from None


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
    except TypeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(7)


if __name__ == "__main__":
    main()