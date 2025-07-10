#!/bin/bash
# Test script for Claude automation

echo "Testing Claude Automation Scripts"
echo "================================="

# Activate virtual environment
source venv_cc_enhancer/bin/activate

# Test 1: WSL direct method
echo -e "\n1. Testing WSL direct method:"
python run_claude_wsl.py --method direct /home/laurelin/projects/code_enhancer "Test direct method"
echo "✓ Direct method launched"
sleep 2

# Test 2: WSL script method  
echo -e "\n2. Testing WSL script method:"
python run_claude_wsl.py --method script /home/laurelin/projects/code_enhancer "Test script method"
echo "✓ Script method launched"
sleep 2

# Test 3: Original pyautogui method
echo -e "\n3. Testing pyautogui method:"
python run_claude.py /home/laurelin/projects/code_enhancer "Test pyautogui method"
echo "✓ Pyautogui method launched"

echo -e "\nAll tests launched! Check if terminals opened and commands executed correctly."