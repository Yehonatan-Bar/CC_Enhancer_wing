#!/usr/bin/env python3
"""
Simple Claude wrapper that always auto-approves permissions.
For when you trust the operations and want minimal friction.
"""

import sys
import subprocess
import xml.etree.ElementTree as ET
sys.path.insert(0, 'bin')
from capture_claude_simple import capture_claude_print


def main():
    if len(sys.argv) < 3:
        print("Usage: python claude_auto.py <role> <prompt>")
        print("\nThis always runs with auto-permissions enabled!")
        print("Available roles: error handling, security review")
        print("Example: python claude_auto.py 'error handling' 'create hello.py'")
        sys.exit(1)
    
    # First, call git_diff_last_commit.py to get the diff
    try:
        result = subprocess.run(
            ['python', 'git_diff_last_commit.py'],
            capture_output=True,
            text=True,
            check=True
        )
        git_diff_output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git_diff_last_commit.py: {e}", file=sys.stderr)
        git_diff_output = "Error retrieving git diff"
    
    # Parse the prompt library XML
    try:
        tree = ET.parse('prompt_library.xml')
        root = tree.getroot()
        
        # Extract prompts from XML
        claude_pre_prompt = root.find(".//prompt[@key='claude pre prompt']").text
        pre_git_diff = root.find(".//prompt[@key='pre git diff']").text
        
        # Extract role parameter and find corresponding prompt
        role = sys.argv[1]
        role_prompt_element = root.find(f".//roles/prompt[@key='{role}']")
        
        if role_prompt_element is None:
            print(f"Error: Role '{role}' not found in prompt_library.xml", file=sys.stderr)
            print("Available roles: error handling, security review")
            sys.exit(1)
            
        role_prompt = role_prompt_element.text
    except Exception as e:
        print(f"Error parsing prompt_library.xml: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Build the combined prompt
    user_prompt = ' '.join(sys.argv[2:])  # Join all args after role as prompt
    
    combined_prompt = f"{claude_pre_prompt}: {user_prompt}\n\n{pre_git_diff}:\n{git_diff_output}\n\n{role_prompt}"
    
    # Send to Claude
    output, code = capture_claude_print(
        combined_prompt,
        skip_permissions=True,
        verbose=False
    )
    
    if code == 0:
        print(output)
    else:
        print(f"Error: Claude returned code {code}", file=sys.stderr)
        sys.exit(code)


if __name__ == "__main__":
    main()