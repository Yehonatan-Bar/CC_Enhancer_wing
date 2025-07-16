#!/usr/bin/env python3
"""
Script to show the differences between the last commit and the previous one.
"""

import subprocess
import sys


def get_git_diff():
    """Get the diff between the last commit and the previous one."""
    try:
        # Get the diff between HEAD and HEAD~1
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("Differences between the last commit and the previous one:")
            print("-" * 80)
            print(result.stdout)
        else:
            print("No differences found between the last commit and the previous one.")
            
    except subprocess.CalledProcessError as e:
        if "ambiguous argument 'HEAD~1'" in e.stderr:
            print("Error: This appears to be the first commit (no previous commit exists).")
        else:
            print(f"Git error: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.")
        sys.exit(1)


def get_commit_info():
    """Get information about the last two commits."""
    try:
        # Get info about the last two commits
        result = subprocess.run(
            ['git', 'log', '--oneline', '-2'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("\nLast two commits:")
            print(result.stdout)
            print()
            
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit info: {e.stderr}")


if __name__ == "__main__":
    get_commit_info()
    get_git_diff()