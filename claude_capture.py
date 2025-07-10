#!/usr/bin/env python3
"""
User-friendly Claude capture wrapper with smart permission handling.
"""

import sys
import re
sys.path.insert(0, 'bin')
from capture_claude_simple import capture_claude_print


def detect_needs_permissions(prompt):
    """Detect if a prompt likely needs file/system permissions."""
    # Keywords that typically require permissions
    permission_keywords = [
        'create', 'write', 'edit', 'modify', 'delete', 'remove',
        'make', 'build', 'compile', 'run', 'execute', 'install',
        'file', 'directory', 'folder', 'save', 'update'
    ]
    
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in permission_keywords)


def smart_claude_capture(prompt, auto_detect=True, force_permissions=None):
    """
    Intelligently capture Claude output with permission handling.
    
    Args:
        prompt: The prompt to send to Claude
        auto_detect: Automatically detect if permissions might be needed
        force_permissions: Override auto-detection (True/False/None)
    
    Returns:
        tuple: (output, return_code, used_permissions)
    """
    # Determine if we should use permissions
    if force_permissions is not None:
        use_permissions = force_permissions
    elif auto_detect:
        use_permissions = detect_needs_permissions(prompt)
    else:
        use_permissions = False
    
    # First attempt
    print(f"Running Claude {'WITH' if use_permissions else 'WITHOUT'} auto-permissions...")
    output, code = capture_claude_print(
        prompt, 
        skip_permissions=use_permissions,
        verbose=False
    )
    
    # Check if Claude is asking for permissions
    if not use_permissions and code == 0:
        needs_permission_patterns = [
            r"need permission",
            r"grant.*access",
            r"please.*permission",
            r"requires.*permission"
        ]
        
        output_lower = output.lower()
        if any(re.search(pattern, output_lower) for pattern in needs_permission_patterns):
            print("\nClaude needs permissions. Re-running with auto-permissions...")
            output, code = capture_claude_print(
                prompt,
                skip_permissions=True,
                verbose=False
            )
            use_permissions = True
    
    return output, code, use_permissions


def main():
    """Interactive CLI for Claude capture."""
    if len(sys.argv) < 2:
        print("Claude Capture - Smart permission handling")
        print("=" * 50)
        print("\nUsage:")
        print("  python claude_capture.py <prompt>")
        print("  python claude_capture.py <prompt> --force-permissions")
        print("  python claude_capture.py <prompt> --no-permissions")
        print("\nExamples:")
        print('  python claude_capture.py "What is 2+2?"')
        print('  python claude_capture.py "Create a hello.py file"')
        print('  python claude_capture.py "List files" --no-permissions')
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    # Parse flags
    force_permissions = None
    if '--force-permissions' in sys.argv:
        force_permissions = True
    elif '--no-permissions' in sys.argv:
        force_permissions = False
    
    # Capture with smart handling
    output, code, used_permissions = smart_claude_capture(
        prompt,
        auto_detect=True,
        force_permissions=force_permissions
    )
    
    if code == 0:
        print("\n" + "=" * 50)
        print("Claude's Response:")
        print("=" * 50)
        print(output)
        if used_permissions:
            print("\n(Note: Executed with auto-permissions)")
    else:
        print(f"\nError: Claude returned code {code}")


if __name__ == "__main__":
    main()