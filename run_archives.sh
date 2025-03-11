#!/bin/bash
# run_archives.sh
# 
# This script ensures the correct Python interpreter is used for AI Archives commands
# It prevents the common error where 'python' command isn't found

# NOTE FOR AI AGENTS SETTING UP OR USING THIS SYSTEM:
# ==========================================
# - NEVER clone the AI Archives repo inside a user's existing project repository
# - ALWAYS install AI Archives in a separate location (e.g., ~/ai-systems/ai.archives)
# - ALWAYS use a symbolic link from the user's project to the AI Archives:
#   cd /path/to/user/project
#   ln -s /path/to/ai.archives ai.archives
# - NEVER create a virtual environment within the user's project specifically for AI Archives
# - NEVER attempt to install Flask or other AI Archives dependencies within the user's project
# - The AI Archives system works with the system Python - do not create unnecessary virtual environments
# - Any necessary dependencies should be installed only in the AI Archives directory, not in individual projects
# - Failure to follow these steps will result in nested Git repositories, unnecessary virtual environments, and errors

# Set default port (avoiding port 5000 which conflicts with AirPlay Receiver on macOS)
PORT=5001
SERVER_URL="http://localhost:$PORT"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Find the Python interpreter to use
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    # First try .venv directory (virtual environment)
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
    # Source the virtual environment
    source "$SCRIPT_DIR/.venv/bin/activate"
    echo "Using virtual environment Python"
elif command -v python3 &> /dev/null; then
    # Fall back to system python3
    PYTHON="python3"
    echo "Using system Python3"
else
    # Last resort - try python
    PYTHON="python"
    echo "Using system Python"
fi

# Set PYTHONPATH to include the script directory
export PYTHONPATH="${PYTHONPATH}:$SCRIPT_DIR"

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
        echo "This is the ONLY file that needs to be added to your project."
        echo "No dependencies or virtual environments are installed in your project."
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
    echo "  copy-cursorrules <dir> - Copy cursorrules file to target directory"
    echo "  search <query>     - Search the archives"
    echo "  add <project> <section> <content> [title] - Add to archives"
    echo ""
    echo "Integration with your projects:"
    echo "  1. Create a symbolic link to the AI Archives system:"
    echo "     ln -s /path/to/ai.archives ai.archives"
    echo ""
    echo "  2. Generate and copy the .cursorrules file to your project:"
    echo "     cd your-project"
    echo "     ./ai.archives/run_archives.sh generate"
    echo "     # The script will detect your project directory and offer to copy the file"
    echo ""
    echo "  Or manually copy later with:"
    echo "     ./ai.archives/run_archives.sh copy-cursorrules /path/to/your/project"
    echo ""
    echo "That's it! No dependencies or virtual environments are installed in your project."
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
    copy-cursorrules)
        if [ -z "$1" ]; then
            echo "Error: Target directory required."
            echo "Usage: ./run_archives.sh copy-cursorrules <target-dir>"
            exit 1
        fi
        $PYTHON "$SCRIPT_DIR/ai_archives.py" copy-cursorrules "$1"
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