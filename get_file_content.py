#!/usr/bin/env python3
"""
Script to get file content by providing a file path.
Usage: python get_file_content.py <file_path>
"""
import sys
import os

def get_file_content(file_path):
    """Read and return the content of a file given its path."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return f"Error: '{file_path}' is not a file."
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return content
    
    except PermissionError:
        return f"Error: Permission denied to read '{file_path}'."
    except UnicodeDecodeError:
        # Try reading as binary if UTF-8 fails
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            return f"Note: File is binary. Content (bytes):\n{content}"
        except Exception as e:
            return f"Error reading binary file: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python get_file_content.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    content = get_file_content(file_path)
    print(content)

if __name__ == "__main__":
    main()