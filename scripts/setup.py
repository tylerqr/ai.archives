#!/usr/bin/env python3
"""
AI Archives System Setup Script

This script helps users set up the AI archives system in their projects.
It creates the necessary directory structure, initializes the archives,
and configures the data path.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
import json
import subprocess
import textwrap
import configparser
import re
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

# Try to import get_archives_manager from core directly
try:
    from core.archives_manager import get_archives_manager
except ImportError:
    # Fall back to old import path for backward compatibility
    from archives.core.archives_manager import get_archives_manager


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80 + "\n")


def prompt_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return the answer."""
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def check_prerequisites():
    """Check if all prerequisites are met"""
    print_header("Checking Prerequisites")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    print("✓ Python version OK")
    
    # Check Git installation
    try:
        git_version = subprocess.check_output(["git", "--version"]).decode().strip()
        print(f"Git version: {git_version}")
        print("✓ Git installation OK")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Git is not installed or not in PATH.")
        return False
    
    return True


def setup_data_directory(data_path=None, create_examples=True):
    """
    Set up the AI archives data directory structure

    Args:
        data_path: Path to the data directory. If None, uses repo root
        create_examples: Whether to create example archives

    Returns:
        Path to the data directory
    """
    print_header("Setting up AI Archives Data Directory")
    
    # Use repo root as the data directory if not specified
    if data_path is None:
        data_path = repo_root
    
    data_path = os.path.abspath(data_path)
    print(f"Setting up archives at: {data_path}")
    
    # Create simplified directory structure
    archives_dir = os.path.join(data_path, "archives")
    os.makedirs(archives_dir, exist_ok=True)
    
    # Create project directories under archives/
    projects = ["frontend", "backend", "shared"]
    sections = ["setup", "architecture", "errors", "fixes", "apis", "dependencies", "recommendations"]
    
    for project in projects:
        project_dir = os.path.join(archives_dir, project)
        os.makedirs(project_dir, exist_ok=True)
        
        for section in sections:
            section_dir = os.path.join(project_dir, section)
            os.makedirs(section_dir, exist_ok=True)
    
    # Copy custom-rules template to the root
    source_rules_path = os.path.join(repo_root, "custom-rules.md")
    target_rules_path = os.path.join(data_path, "custom-rules.md")
    
    if not os.path.exists(target_rules_path):
        if os.path.exists(source_rules_path):
            shutil.copy(source_rules_path, target_rules_path)
            print(f"✓ Custom rules template copied to {target_rules_path}")
        else:
            print(f"Warning: Custom rules template not found at {source_rules_path}")
    else:
        print(f"✓ Custom rules already exist at {target_rules_path}")
    
    # Create sample content if requested
    if create_examples:
        create_sample_content(data_path)
    
    return data_path


def create_wrapper_script():
    """
    Create the run_archives.sh wrapper script if it doesn't exist yet.
    This script ensures the correct Python interpreter is used.
    """
    wrapper_script_path = os.path.join(repo_root, "run_archives.sh")
    
    if os.path.exists(wrapper_script_path):
        print("✓ Wrapper script already exists")
        
        # Make sure it's executable
        if not os.access(wrapper_script_path, os.X_OK):
            os.chmod(wrapper_script_path, 0o755)
            print("✓ Made wrapper script executable")
        
        return
    
    print("Creating wrapper script (run_archives.sh)...")
    
    wrapper_content = textwrap.dedent("""#!/bin/bash
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
    # Set server URL to use the custom port
    if $PYTHON "$SCRIPT_DIR/ai_archives.py" generate $output_path --server-url "$SERVER_URL"; then
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
    
    # Run search
    $PYTHON "$SCRIPT_DIR/ai_archives.py" search "$1" --server-url "$SERVER_URL"
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
    
    # Run add
    if [ -z "$title" ]; then
        $PYTHON "$SCRIPT_DIR/ai_archives.py" add "$project" "$section" "$content" --server-url "$SERVER_URL"
    else
        $PYTHON "$SCRIPT_DIR/ai_archives.py" add "$project" "$section" "$content" "$title" --server-url "$SERVER_URL"
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
""")
    
    with open(wrapper_script_path, 'w') as f:
        f.write(wrapper_content)
    
    # Make the script executable
    os.chmod(wrapper_script_path, 0o755)
    
    print("✓ Created and made executable the wrapper script (run_archives.sh)")


def update_config(data_path):
    """
    Update the config.json file with the data path

    Args:
        data_path: Path to the data directory
    """
    config_path = os.path.join(repo_root, "archives", "core", "config.json")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Add data directory info to config
        if "settings" not in config:
            config["settings"] = {}
        
        # Use repo_root as the base data directory
        config["settings"]["data_directory"] = repo_root
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Updated config to use data directory: {repo_root}")


def create_sample_content(data_path, skip_prompt=False):
    """
    Create sample content in the archives

    Args:
        data_path: Path to the data directory
    """
    print_header("Creating Sample Content")
    
    # Set the data directory for the manager
    manager = get_archives_manager(data_repo_root=data_path)
    
    if prompt_yes_no("Would you like to create sample content in the archives?", default="yes"):
        # Create sample frontend setup entry
        frontend_content = textwrap.dedent("""
        # Sample Frontend Setup
        
        This is a sample entry for the frontend project setup.
        
        ## Getting Started
        
        1. Clone the repository
        2. Install dependencies: `npm install`
        3. Start the development server: `npm run dev`