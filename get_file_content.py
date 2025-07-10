#!/usr/bin/env python3
"""
Script to get file content by providing a file path.
Usage: python get_file_content.py <file_path>
"""
import sys
import os
import binascii
import argparse

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_BINARY_DISPLAY = 1024  # Max bytes to display for binary files

def validate_path(file_path):
    """Validate the file path for security issues."""
    # Get absolute path and resolve any symlinks
    try:
        real_path = os.path.realpath(file_path)
        abs_path = os.path.abspath(file_path)
    except Exception as e:
        return None, f"Error resolving path: {str(e)}"
    
    # Check for path traversal attempts
    if ".." in file_path or file_path.startswith("/etc/") or file_path.startswith("/root/"):
        return None, "Error: Potential path traversal detected."
    
    return real_path, None

def get_file_content(file_path, follow_symlinks=False):
    """Read and return the content of a file given its path."""
    try:
        # Validate path
        real_path, error = validate_path(file_path)
        if error:
            return None, error, 2
        
        # Check if file exists
        if not os.path.exists(file_path):
            return None, f"Error: File '{file_path}' does not exist.", 3
        
        # Check if it's a symlink
        if os.path.islink(file_path) and not follow_symlinks:
            return None, f"Error: '{file_path}' is a symbolic link. Use --follow-symlinks to read it.", 4
        
        # Check if it's a file (not directory)
        if not os.path.isfile(real_path):
            return None, f"Error: '{real_path}' is not a file.", 5
        
        # Check file size
        file_size = os.path.getsize(real_path)
        if file_size > MAX_FILE_SIZE:
            return None, f"Error: File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes).", 6
        
        # Read file content
        with open(real_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return content, None, 0
    
    except PermissionError:
        return None, f"Error: Permission denied to read '{file_path}'.", 7
    except UnicodeDecodeError:
        # Try reading as binary if UTF-8 fails
        try:
            with open(real_path, 'rb') as file:
                content = file.read(MAX_BINARY_DISPLAY)
                
            # Format binary content as hex
            hex_content = binascii.hexlify(content).decode('ascii')
            formatted_hex = ' '.join(hex_content[i:i+2] for i in range(0, len(hex_content), 2))
            
            result = f"Note: File is binary. First {min(len(content), MAX_BINARY_DISPLAY)} bytes (hex):\n{formatted_hex}"
            if file_size > MAX_BINARY_DISPLAY:
                result += f"\n... ({file_size - MAX_BINARY_DISPLAY} more bytes)"
            
            return result, None, 0
        except Exception as e:
            return None, f"Error reading binary file: {str(e)}", 8
    except Exception as e:
        return None, f"Error reading file: {str(e)}", 9

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Get file content by providing a file path.")
    parser.add_argument('file_path', help='Path to the file to read')
    parser.add_argument('--follow-symlinks', action='store_true', 
                        help='Follow symbolic links')
    
    args = parser.parse_args()
    
    # Get file content
    content, error, exit_code = get_file_content(args.file_path, args.follow_symlinks)
    
    if error:
        print(error, file=sys.stderr)
        sys.exit(exit_code)
    else:
        print(content)
        sys.exit(0)

if __name__ == "__main__":
    main()