#!/usr/bin/env python3
"""
Diagnostic script to help troubleshoot Claude command issues.
"""

import os
import subprocess
import sys


def check_claude():
    """Run various checks to diagnose Claude command issues."""
    print("Claude Command Diagnostic Tool")
    print("=" * 50)
    
    # Check 1: Which claude
    print("\n1. Checking 'which claude':")
    try:
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ Found: {result.stdout.strip()}")
        else:
            print("   ✗ 'which claude' failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Check 2: Direct execution
    print("\n2. Testing direct execution:")
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✓ Claude runs directly: {result.stdout.strip()[:50]}...")
        else:
            print(f"   ✗ Direct execution failed: {result.stderr}")
    except FileNotFoundError:
        print("   ✗ Claude command not found in PATH")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Check 3: PATH environment
    print("\n3. Current PATH:")
    path = os.environ.get('PATH', '')
    npm_global_in_path = False
    for p in path.split(':'):
        if 'npm-global' in p:
            print(f"   ✓ npm-global in PATH: {p}")
            npm_global_in_path = True
    if not npm_global_in_path:
        print("   ✗ npm-global directory not found in PATH")
    
    # Check 4: npm global directory
    print("\n4. Checking npm global directory:")
    npm_global_path = os.path.expanduser("~/.npm-global/bin/claude")
    if os.path.exists(npm_global_path):
        print(f"   ✓ Found claude at: {npm_global_path}")
        print(f"   ✓ Executable: {os.access(npm_global_path, os.X_OK)}")
    else:
        print("   ✗ Claude not found in ~/.npm-global/bin/")
    
    # Check 5: Shell initialization files
    print("\n5. Shell configuration files:")
    configs = ['.bashrc', '.bash_profile', '.profile', '.zshrc']
    for config in configs:
        config_path = os.path.expanduser(f"~/{config}")
        if os.path.exists(config_path):
            print(f"   ✓ {config} exists")
            # Check if npm-global is added in the file
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                    if 'npm-global' in content:
                        print(f"     └─ Contains npm-global PATH setup")
            except:
                pass
    
    # Check 6: Interactive vs non-interactive shell
    print("\n6. Testing shell environments:")
    
    # Non-interactive shell
    print("   Non-interactive shell (bash -c):")
    try:
        result = subprocess.run(['bash', '-c', 'which claude'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"     ✓ Found: {result.stdout.strip()}")
        else:
            print("     ✗ Claude not found in non-interactive shell")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # Interactive shell
    print("   Interactive shell (bash -ic):")
    try:
        result = subprocess.run(['bash', '-ic', 'which claude'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"     ✓ Found: {result.stdout.strip()}")
        else:
            print("     ✗ Claude not found in interactive shell")
    except Exception as e:
        print(f"     ✗ Error: {e}")
    
    # Check 7: WSL detection
    print("\n7. Environment:")
    if os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
        print("   ✓ Running in WSL")
    else:
        print("   ✓ Not running in WSL")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS:")
    
    if not npm_global_in_path:
        print("\n⚠️  Add npm global directory to PATH:")
        print("   Add this to your ~/.bashrc:")
        print("   export PATH=$PATH:~/.npm-global/bin")
    
    print("\n⚠️  For automation scripts, use one of these approaches:")
    print("   1. Source .bashrc: bash -c 'source ~/.bashrc && claude'")
    print("   2. Use full path: /home/$USER/.npm-global/bin/claude")
    print("   3. Use interactive shell: bash -ic 'claude'")


if __name__ == "__main__":
    check_claude()