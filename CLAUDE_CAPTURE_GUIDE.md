# Claude Output Capture Guide

This guide explains different methods to capture Claude's output programmatically.

## Quick Start

### Method 1: Simple Capture with Auto-Permissions (Recommended)

```python
from capture_claude_simple import capture_claude_print

# Capture output with automatic permission approval
output, return_code = capture_claude_print(
    "create a hello.py file with a hello world function",
    skip_permissions=True
)

print(output)
```

### Method 2: Simple Capture (Read-Only)

```python
from capture_claude_simple import capture_claude_print

# For queries that don't require file operations
output, return_code = capture_claude_print("What is 2 + 2?")
print(output)
```

## Available Methods

### 1. **capture_claude_simple.py** - Simple Mode (Recommended)

Uses Claude's `--print` flag for straightforward output capture.

**Pros:**
- Simple and reliable
- Fast execution
- Can skip permissions with `--dangerously-skip-permissions`
- No terminal emulation complexity

**Cons:**
- No interactive prompts
- Must decide upfront whether to skip permissions

**Usage:**
```bash
# Basic usage
python capture_claude_simple.py "your prompt here"

# With auto-permissions (for file operations)
python capture_claude_simple.py "create test.txt" --skip-permissions
```

**Python API:**
```python
from capture_claude_simple import capture_claude_print

output, code = capture_claude_print(
    prompt="your prompt",
    path=".",                # Working directory
    timeout=300,            # Timeout in seconds
    verbose=False,          # Debug output
    skip_permissions=False  # Auto-approve permissions
)
```

### 2. **claude_auto_responder_pty.py** - Interactive Mode with PTY

Uses pseudo-terminal for full interactive mode with automatic "Do you want to..." responses.

**Pros:**
- Full interactive mode
- Can handle permission prompts dynamically
- Sees exactly what Claude outputs

**Cons:**
- More complex
- Requires PTY support
- Currently needs more work for reliable operation

**Usage:**
```bash
python claude_auto_responder_pty.py . "your prompt" --verbose
```

## Common Use Cases

### 1. Code Generation
```python
output, _ = capture_claude_print(
    "Write a Python function to calculate fibonacci numbers",
    skip_permissions=True
)
```

### 2. File Analysis
```python
output, _ = capture_claude_print(
    "Analyze the structure of main.py and suggest improvements"
)
```

### 3. Batch Processing
```python
files = ["file1.py", "file2.py", "file3.py"]
for file in files:
    output, _ = capture_claude_print(
        f"Add docstrings to all functions in {file}",
        skip_permissions=True
    )
```

### 4. Safe Queries (No File Access)
```python
# These don't need skip_permissions
output, _ = capture_claude_print("Explain Python decorators")
output, _ = capture_claude_print("What are the SOLID principles?")
```

## Security Considerations

⚠️ **Warning about `--dangerously-skip-permissions`:**
- This flag allows Claude to perform ALL file operations without asking
- Only use in controlled environments
- Consider the principle of least privilege
- For production use, consider implementing a custom permission handler

## Troubleshooting

### Issue: "I need permission to create the file"
**Solution:** Use `skip_permissions=True` or add `--skip-permissions` flag

### Issue: Command times out
**Solution:** Increase timeout parameter or check if Claude is installed correctly

### Issue: No output received
**Solution:** Check Claude installation with `claude --version`

## Advanced Usage

### Custom Permission Handling

For production use, you might want to implement custom permission logic:

```python
# Example: Only allow operations in specific directories
def safe_claude_capture(prompt, allowed_paths):
    # First, run without permissions to see what Claude wants to do
    output, _ = capture_claude_print(prompt, skip_permissions=False)
    
    # Parse output to check requested operations
    if "need permission" in output.lower():
        # Implement your logic here
        if is_safe_operation(output, allowed_paths):
            # Re-run with permissions
            output, _ = capture_claude_print(prompt, skip_permissions=True)
    
    return output
```

## Examples

See `example_claude_capture.py` for complete working examples including:
- Simple captures
- Batch processing
- Code generation
- Context-aware operations