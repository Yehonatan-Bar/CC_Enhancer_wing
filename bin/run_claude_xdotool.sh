#!/bin/bash

# Check if both parameters are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <path> <string>"
    exit 1
fi

PATH_PARAM="$1"
STRING_PARAM="$2"

# Check if the path exists
if [ ! -d "$PATH_PARAM" ]; then
    echo "Error: Directory '$PATH_PARAM' does not exist"
    exit 1
fi

# Open a new terminal window
gnome-terminal --working-directory="$PATH_PARAM" &

# Wait for terminal to open
sleep 2

# Type the claude command
xdotool type "claude"
xdotool key Return

# Wait 5 seconds
sleep 5

# Type the string parameter
xdotool type "$STRING_PARAM"

# Press Enter
xdotool key Return