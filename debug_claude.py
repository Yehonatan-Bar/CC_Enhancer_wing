#!/usr/bin/env python3
"""Debug script to test Claude execution."""

import subprocess
import os

git_bash = r'C:\Program Files\Git\bin\bash.exe'

# Test 1: Simple claude version
print("Test 1: claude --version")
result = subprocess.run(
    [git_bash, '-c', 'claude --version'],
    capture_output=True,
    text=True
)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
print("-" * 50)

# Test 2: claude with print
print("\nTest 2: claude --print 'test'")
result = subprocess.run(
    [git_bash, '-c', "claude --print 'test'"],
    capture_output=True,
    text=True
)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
print("-" * 50)

# Test 3: Set PATH and run claude
print("\nTest 3: With PATH set")
bash_script = '''
export PATH="/c/Users/yonzb/AppData/Roaming/npm:$PATH"
which claude
claude --version
'''
result = subprocess.run(
    [git_bash, '-c', bash_script],
    capture_output=True,
    text=True
)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
print("-" * 50)

# Test 4: Run with NODE_PATH
print("\nTest 4: With NODE_PATH set")
env = os.environ.copy()
env['NODE_PATH'] = r'C:\Users\yonzb\AppData\Roaming\npm\node_modules'
result = subprocess.run(
    [git_bash, '-c', 'claude --version'],
    capture_output=True,
    text=True,
    env=env
)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")