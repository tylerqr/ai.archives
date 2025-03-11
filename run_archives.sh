#!/bin/bash
# run_archives.sh
# 
# This script ensures the correct Python interpreter is used for AI Archives commands
# It prevents the common error where 'python' command isn't found

# Set default port (avoiding port 5000 which conflicts with AirPlay Receiver on macOS)
PORT=5001
SERVER_URL="http://localhost:$PORT"

# Find the Python interpreter to use
if [ -f ".venv/bin/python" ]; then
    # First try .venv directory (common venv location)
    PYTHON=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    # Fall back to system python3
    PYTHON="python3"
else
    # Last resort - try python
    PYTHON="python"
fi

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to start the server
start_server() {
    echo "Starting AI Archives server on port $PORT..."
    # Set PORT environment variable
    export PORT=$PORT
    $PYTHON "$SCRIPT_DIR/server.py" &
    sleep 2
    echo "Server started in background on port $PORT."
}

# Function to check if server is running
check_server() {
    if curl -s $SERVER_URL/ping > /dev/null; then
        echo "Server is running on port $PORT."
        return 0
    else
        echo "Server is not running on port $PORT."
        return 1
    fi
}

# Function to generate cursorrules
generate_cursorrules() {
    output_path=""
    if [ ! -z "$1" ]; then
        output_path="--output $1"
    fi
    
    # Make sure server is running
    if ! check_server; then
        start_server
    fi
    
    # Try using the REST API first
    echo "Generating cursorrules file..."
    # Set server URL as environment variable
    export ARCHIVES_SERVER_URL="$SERVER_URL"
    if $PYTHON "$SCRIPT_DIR/ai_archives.py" generate $output_path; then
        echo "Successfully generated cursorrules file."
    else
        echo "Error using REST API. Falling back to direct method..."
        # Fallback to the direct method
        if [ -f "$SCRIPT_DIR/scripts/integrate_cursorrules.py" ]; then
            $PYTHON "$SCRIPT_DIR/scripts/integrate_cursorrules.py" $output_path
        else
            echo "Error: Fallback script not found."
            return 1
        fi
    fi
}

# Function to search archives
search_archives() {
    if [ -z "$1" ]; then
        echo "Error: Search query required."
        return 1
    fi
    
    # Make sure server is running
    if ! check_server; then
        start_server
    fi
    
    # Run search with server URL as environment variable
    export ARCHIVES_SERVER_URL="$SERVER_URL"
    $PYTHON "$SCRIPT_DIR/ai_archives.py" search "$1"
}

# Function to add to archives
add_to_archives() {
    if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
        echo "Error: Project, section and content required."
        echo "Usage: ./run_archives.sh add <project> <section> <content> [title]"
        return 1
    fi
    
    project="$1"
    section="$2"
    content="$3"
    title="${4:-}"
    
    # Make sure server is running
    if ! check_server; then
        start_server
    fi
    
    # Run add with server URL as environment variable
    export ARCHIVES_SERVER_URL="$SERVER_URL"
    if [ -z "$title" ]; then
        $PYTHON "$SCRIPT_DIR/ai_archives.py" add "$project" "$section" "$content"
    else
        $PYTHON "$SCRIPT_DIR/ai_archives.py" add "$project" "$section" "$content" "$title"
    fi
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: ./run_archives.sh <command> [arguments]"
    echo ""
    echo "Available commands:"
    echo "  server             - Start the archives server"
    echo "  generate [output]  - Generate combined cursorrules file"
    echo "  search <query>     - Search the archives"
    echo "  add <project> <section> <content> [title] - Add to archives"
    exit 1
fi

command="$1"
shift

case "$command" in
    server)
        start_server
        ;;
    generate)
        generate_cursorrules "$1"
        ;;
    search)
        search_archives "$1"
        ;;
    add)
        add_to_archives "$1" "$2" "$3" "$4"
        ;;
    *)
        echo "Unknown command: $command"
        exit 1
        ;;
esac 