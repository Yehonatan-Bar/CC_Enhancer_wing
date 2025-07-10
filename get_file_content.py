#!/usr/bin/env python3
"""
Script that takes a file path as input and returns its content.
"""

import sys
import os
from pathlib import Path


def get_file_content(file_path):
    """
    Read and return the content of a file.
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: Content of the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permissions
        IsADirectoryError: If the path points to a directory
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"No read permission for file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try reading as binary if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            # Return binary representation if text reading fails
            with open(file_path, 'rb') as f:
                content = f.read()
                return f"[Binary file, size: {len(content)} bytes]"


def main():
    """Main function to handle command line usage."""
    if len(sys.argv) != 2:
        print("Usage: python get_file_content.py <file_path>", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        content = get_file_content(file_path)
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
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    main()