#!/bin/bash

# Check if a directory argument was provided
if [[ -z "$1" ]]; then
    echo "Please provide a directory."
    exit 1
fi

# Convert the directory argument to an absolute path
dir=$(cd "$1"; pwd)

# Determine the OS and open a new terminal window at the specified directory
case "$(uname)" in
    "Linux")
        # For Ubuntu, using Terminator
        terminator --working-directory="$dir" &>/dev/null
        ;;
    "Darwin")
        # For macOS, using iTerm2
        osascript <<EOF
tell application "iTerm2"
    set newWindow to (create window with default profile)
    tell current session of newWindow
        write text "cd $dir"
    end tell
end tell
EOF
        ;;
    *)
        echo "Unsupported OS."
        exit 1
        ;;
esac
