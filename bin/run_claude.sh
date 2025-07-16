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

# Use xdotool to automate terminal interaction
# This opens a new terminal, changes to the specified directory, runs claude,
# waits 5 seconds, types the string, and presses Enter
gnome-terminal -- bash -c "cd '$PATH_PARAM' && claude && sleep 5 && echo '$STRING_PARAM' && read -p 'Press Enter to exit...'"

# Alternative approach using expect if xdotool is not suitable
# Uncomment the following lines if you prefer to use expect:
# expect << EOF
# spawn gnome-terminal -- bash -c "cd '$PATH_PARAM' && claude"
# sleep 5
# send "$STRING_PARAM\r"
# expect eof
# EOF