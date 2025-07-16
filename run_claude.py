#!/usr/bin/env python3
"""
Simple script to run Claude and print the response.
Sets up the required environment for Claude on Windows.
Supports role-based prompting with git diff integration.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
import xml.etree.ElementTree as ET


def setup_claude_environment():
    """Set up CLAUDE_CODE_GIT_BASH_PATH if not already set."""
    if 'CLAUDE_CODE_GIT_BASH_PATH' in os.environ:
        return True
        
    # Find Git Bash
    git_bash_paths = [
        r'C:\Program Files\Git\bin\bash.exe',
        r'C:\Program Files (x86)\Git\bin\bash.exe',
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Git', 'bin', 'bash.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Git', 'bin', 'bash.exe'),
    ]
    
    git_bash = None
    for path in git_bash_paths:
        if os.path.exists(path):
            git_bash = path
            break
    
    if not git_bash:
        print("Error: Git Bash not found. Please install Git for Windows from https://git-scm.com/download/win")
        return False
    
    # Set the environment variable for the current session
    os.environ['CLAUDE_CODE_GIT_BASH_PATH'] = git_bash
    
    # Try to set it permanently for the user
    try:
        subprocess.run([
            'powershell', '-Command',
            f'[Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", "{git_bash}", "User")'
        ], capture_output=True)
        print(f"Set CLAUDE_CODE_GIT_BASH_PATH to: {git_bash}")
        print("Note: You may need to restart your terminal for the permanent setting to take effect.")
    except:
        pass
    
    return True


def run_claude_windows(prompt, skip_permissions=False, timeout=300):
    """Run Claude on Windows."""
    # Ensure environment is set up
    if not setup_claude_environment():
        return "", -1
    
    # Build command
    cmd = ['claude', '--print']
    if skip_permissions:
        cmd.append('--dangerously-skip-permissions')
    cmd.append(prompt)
    
    try:
        # Run claude with the environment variable set
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ,  # Use the modified environment
            shell=True  # Use shell to ensure PATH is resolved
        )
        
        return result.stdout, result.returncode
        
    except subprocess.TimeoutExpired:
        return "", -1
    except Exception as e:
        print(f"Error: {e}")
        return "", -3


def run_claude_unix(prompt, skip_permissions=False, timeout=300):
    """Run Claude on Unix-like systems."""
    cmd = ['claude', '--print']
    if skip_permissions:
        cmd.append('--dangerously-skip-permissions')
    cmd.append(prompt)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except FileNotFoundError:
        return "", -2
    except Exception:
        return "", -3


def get_git_diff():
    """Get the diff between the last commit and the previous one."""
    try:
        result = subprocess.run(
            ['python', 'git_diff_last_commit.py'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git_diff_last_commit.py: {e}", file=sys.stderr)
        return "Error retrieving git diff"


def load_prompts_from_xml(role):
    """Load prompts from prompt_library.xml for the given role."""
    try:
        tree = ET.parse('prompt_library.xml')
        root = tree.getroot()
        
        # Extract prompts from XML
        claude_pre_prompt = root.find(".//prompt[@key='claude pre prompt']").text
        pre_git_diff = root.find(".//prompt[@key='pre git diff']").text
        
        # Find role-specific prompt
        role_prompt_element = root.find(f".//roles/prompt[@key='{role}']")
        
        if role_prompt_element is None:
            available_roles = [elem.get('key') for elem in root.findall(".//roles/prompt")]
            print(f"Error: Role '{role}' not found in prompt_library.xml", file=sys.stderr)
            print(f"Available roles: {', '.join(available_roles)}")
            return None, None, None, available_roles
            
        role_prompt = role_prompt_element.text
        available_roles = [elem.get('key') for elem in root.findall(".//roles/prompt")]
        
        return claude_pre_prompt, pre_git_diff, role_prompt, available_roles
    except Exception as e:
        print(f"Error parsing prompt_library.xml: {e}", file=sys.stderr)
        return None, None, None, []


def main():
    """Main function to run Claude with a prompt and print the response."""
    # Default values
    prompt = "tell me about this project"
    skip_permissions = False
    use_role = False
    role = None
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Check for role usage (first arg is role)
    if len(args) >= 2 and not args[0].startswith('--'):
        # Role mode: python run_claude.py <role> <prompt>
        use_role = True
        role = args[0]
        prompt = ' '.join(args[1:])
    elif len(args) >= 1:
        # Normal mode: python run_claude.py <prompt>
        prompt = args[0]
    
    # Check for permission flags
    if '--skip-permissions' in sys.argv or '--force-permissions' in sys.argv:
        skip_permissions = True
    
    # If using role mode, build the combined prompt
    if use_role:
        claude_pre_prompt, pre_git_diff, role_prompt, available_roles = load_prompts_from_xml(role)
        
        if role_prompt is None:
            print("\nUsage: python run_claude.py <role> <prompt>")
            print("   or: python run_claude.py <prompt>")
            sys.exit(1)
        
        # Get git diff
        git_diff_output = get_git_diff()
        
        # Build combined prompt
        prompt = f"{claude_pre_prompt}: {prompt}\n\n{pre_git_diff}:\n{git_diff_output}\n\n{role_prompt}"
        
        print(f"Running Claude with role '{role}'")
        print(f"User prompt: {' '.join(args[1:])[:50]}{'...' if len(' '.join(args[1:])) > 50 else ''}")
    else:
        print(f"Running Claude with prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    
    print("Waiting for Claude's response...")
    
    # Run Claude based on platform
    if platform.system() == "Windows":
        output, code = run_claude_windows(prompt, skip_permissions)
    else:
        output, code = run_claude_unix(prompt, skip_permissions)
    
    if code == 0:
        print("\n" + "="*60)
        print("Claude's Response:")
        print("="*60)
        print(output)
        print("="*60)
    else:
        print(f"\nClaude failed with return code: {code}")
        if output:
            print(f"Output: {output}")
        if code == -1:
            print("Timeout occurred - Claude took too long to respond")
        elif code == -2:
            print("Claude command not found - ensure Claude Code is installed")
        elif code == -3:
            print("An unexpected error occurred")
        elif code == 1:
            print("\nTroubleshooting:")
            print("1. The CLAUDE_CODE_GIT_BASH_PATH environment variable has been set.")
            print("2. Try opening a new terminal window and running this script again.")
            print("3. Or run Claude directly: claude --print \"your prompt\"")
            print("4. If it still doesn't work, try running from Git Bash directly.")
            if use_role:
                print("\nUsage: python run_claude.py <role> <prompt>")
                print("   or: python run_claude.py <prompt>")
    
    # Exit with appropriate code
    sys.exit(code if code >= 0 else 1)


if __name__ == "__main__":
    main()