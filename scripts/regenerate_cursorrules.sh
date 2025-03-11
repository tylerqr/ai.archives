#!/bin/bash
# Script to regenerate the .cursorrules file with proper error handling
# and environment setup

# Directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "=== AI Archives .cursorrules Regeneration Tool ==="
echo "Repository root: $REPO_ROOT"

# Find the right Python interpreter
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Could not find Python executable"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"
echo "Regenerating .cursorrules file..."

# Run the simple script that has no dependencies
(cd "$REPO_ROOT" && $PYTHON_CMD "$SCRIPT_DIR/simple_cursorrules.py")

# Check if it worked
if [ $? -eq 0 ] && [ -f "$REPO_ROOT/.cursorrules" ]; then
    echo "✅ .cursorrules file successfully generated!"
    echo "Size: $(wc -c < "$REPO_ROOT/.cursorrules") bytes"
    echo "Location: $REPO_ROOT/.cursorrules"
    echo "Done!"
    exit 0
else
    echo "❌ Failed to generate .cursorrules file"
    echo "Try running the Python script directly:"
    echo "  cd $REPO_ROOT && $PYTHON_CMD $SCRIPT_DIR/simple_cursorrules.py"
    exit 1
fi 