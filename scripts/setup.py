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
    print("=" * 80)


def prompt_yes_no(question, default="yes"):
    """
    Ask a yes/no question via input() and return the answer.
    
    Args:
        question: String presented to the user
        default: The default answer if the user just hits Enter
    
    Returns:
        True for "yes" or False for "no"
    """
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"Invalid default answer: '{default}'")
    
    while True:
        print(f"{question}{prompt}", end="")
        choice = input().lower()
        if choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")


def check_prerequisites():
    """Check if the prerequisites are installed"""
    print_header("Checking Prerequisites")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    
    print("✓ Python version is sufficient")
    
    # Check if git is installed
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        print(f"Git version: {result.stdout.strip()}")
        print("✓ Git is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Git is not installed.")
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
    
    # Create the wrapper script if it doesn't exist
    create_wrapper_script()
    
    # Update the config file to point to the data directory
    update_config(data_path)
    
    # Create sample content if requested
    if create_examples:
        create_sample_content(data_path)
    
    return data_path


def create_wrapper_script():
    """Create the wrapper script for easier access to AI archives functionality"""
    print_header("Creating Wrapper Script")
    
    wrapper_path = os.path.join(repo_root, "run_archives.sh")
    
    if os.path.exists(wrapper_path):
        print(f"Wrapper script already exists at {wrapper_path}")
        return
    
    wrapper_content = """#!/bin/bash
# AI Archives Wrapper Script
# This script provides a simple interface to the AI Archives system
# It handles server management and environment setup automatically

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default server URL
SERVER_URL="http://localhost:5001"

# Function to check if the server is running
check_server() {
    curl -s "$SERVER_URL/ping" > /dev/null
    if [ $? -eq 0 ]; then
        echo "Server is running on port 5001."
        return 0
    else
        echo "Server is not running on port 5001. Starting it..."
        # Start the server in the background
        nohup python "$SCRIPT_DIR/server.py" --port 5001 > /dev/null 2>&1 &
        
        # Wait for the server to start
        for i in {1..10}; do
            sleep 1
            curl -s "$SERVER_URL/ping" > /dev/null
            if [ $? -eq 0 ]; then
                echo "Server is running on port 5001."
                return 0
            fi
        done
        
        echo "Error: Failed to start the server. Try running manually: python $SCRIPT_DIR/server.py"
        return 1
    fi
}

# Function to generate cursorrules
generate_cursorrules() {
    check_server
    if [ $? -eq 0 ]; then
        echo "Generating cursorrules file..."
        curl -s -X POST "$SERVER_URL/generate-cursorrules" > /dev/null
        if [ $? -eq 0 ]; then
            echo "Successfully generated cursorrules file."
            return 0
        else
            echo "Failed to generate cursorrules file. Trying direct method..."
        fi
    fi
    
    # Fallback to using Python script directly
    python "$SCRIPT_DIR/scripts/rest_integrate_cursorrules.py"
    return $?
}

# Function to search archives
search_archives() {
    check_server
    if [ $? -eq 0 ]; then
        project_param=""
        if [ -n "$2" ]; then
            project_param="&project=$2"
        fi
        curl -s "$SERVER_URL/search?query=$1$project_param" | python -m json.tool
        return $?
    fi
    return 1
}

# Function to add to archives
add_to_archives() {
    if [ $# -lt 4 ]; then
        echo "Usage: $0 add PROJECT SECTION TITLE CONTENT"
        return 1
    fi
    
    project="$1"
    section="$2"
    title="$3"
    content="$4"
    
    check_server
    if [ $? -eq 0 ]; then
        curl -s -X POST "$SERVER_URL/add" \
            -H "Content-Type: application/json" \
            -d "{\"project\": \"$project\", \"section\": \"$section\", \"title\": \"$title\", \"content\": \"$content\"}"
        return $?
    fi
    return 1
}

# Main command handler
case "$1" in
    generate)
        generate_cursorrules
        ;;
    search)
        if [ -z "$2" ]; then
            echo "Usage: $0 search QUERY [PROJECT]"
            exit 1
        fi
        search_archives "$2" "$3"
        ;;
    add)
        if [ $# -lt 5 ]; then
            echo "Usage: $0 add PROJECT SECTION TITLE CONTENT"
            exit 1
        fi
        add_to_archives "$2" "$3" "$4" "$5"
        ;;
    server)
        echo "Starting AI Archives server..."
        python "$SCRIPT_DIR/server.py" --port 5001
        ;;
    *)
        echo "Usage: $0 {generate|search|add|server}"
        echo ""
        echo "Commands:"
        echo "  generate            Generate a new .cursorrules file"
        echo "  search QUERY        Search the archives"
        echo "  add PROJECT SECTION TITLE CONTENT"
        echo "                      Add content to the archives"
        echo "  server              Start the AI Archives server"
        exit 1
        ;;
esac

exit 0
"""
    
    with open(wrapper_path, "w") as f:
        f.write(wrapper_content)
    
    # Make the script executable
    os.chmod(wrapper_path, 0o755)
    
    print(f"✓ Created wrapper script at {wrapper_path}")
    print("  You can now use ./run_archives.sh to interact with the archives")


def update_config(data_path):
    """
    Update the configuration to use the specified data directory

    Args:
        data_path: Path to the data directory
    """
    print_header("Updating Configuration")
    
    # Load the current config
    config_path = os.path.join(repo_root, "core", "config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}
    
    # Ensure settings exists
    if "settings" not in config:
        config["settings"] = {}
    
    # Use repo_root as the base data directory
    config["settings"]["data_directory"] = data_path
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Updated config to use data directory: {data_path}")


def create_sample_content(data_path, skip_prompt=False):
    """
    Create sample content in the archives

    Args:
        data_path: Path to the data directory
        skip_prompt: Whether to skip prompting the user
    """
    print_header("Creating Sample Content")
    
    # Set the data directory for the manager
    manager = get_archives_manager(data_repo_root=data_path)
    
    if skip_prompt or prompt_yes_no("Would you like to create sample content in the archives?", default="yes"):
        # Create sample frontend setup entry
        frontend_content = textwrap.dedent("""
        # Sample Frontend Setup
        
        This is a sample entry for the frontend project setup.
        
        ## Getting Started
        
        1. Clone the repository
        2. Install dependencies: `npm install`
        3. Start the development server: `npm run dev`
        """)

        # Create sample backend setup entry
        backend_content = textwrap.dedent("""
        # Sample Backend Setup
        
        This is a sample entry for the backend project setup.
        
        ## Getting Started
        
        1. Clone the repository
        2. Install dependencies: `pip install -r requirements.txt`
        3. Start the development server: `python app.py`
        """)

        # Create sample shared setup entry
        shared_content = textwrap.dedent("""
        # Sample Shared Setup
        
        This is a sample entry for the shared project setup.
        
        ## Getting Started
        
        1. Clone the repository
        2. Install dependencies: `pip install -r requirements.txt`
        3. Start the development server: `python app.py`
        """)

        # Add the sample content to the archives
        manager.add_to_archives("frontend", "setup", frontend_content, "Frontend Setup")
        manager.add_to_archives("backend", "setup", backend_content, "Backend Setup")
        manager.add_to_archives("shared", "setup", shared_content, "Shared Setup")
        
        print("✓ Created sample content in the archives")
    else:
        print("Skipping sample content creation")


def main():
    """Main entry point for the setup script"""
    parser = argparse.ArgumentParser(description="Set up the AI Archives system")
    
    # Setup options
    parser.add_argument("--install", action="store_true", help="Perform a full installation")
    parser.add_argument("--data-path", help="Path to store archives data")
    parser.add_argument("--no-examples", action="store_true", help="Skip creating example archives")
    parser.add_argument("--link", metavar="PROJECT_PATH", help="Link archives to an existing project")
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_prerequisites():
        print("Please install the required prerequisites and try again.")
        return 1
    
    # Perform installation if requested
    if args.install:
        print_header("Installing AI Archives System")
        
        # Set up the data directory
        data_path = setup_data_directory(
            data_path=args.data_path,
            create_examples=not args.no_examples
        )
        
        print("\n✓ AI Archives system installed successfully!")
        print(f"Data directory: {data_path}")
        print("\nYou can now use the archives with:")
        print("  ./run_archives.sh search \"your search term\"")
        print("  ./run_archives.sh add frontend setup \"Title\" \"Content\"")
        print("  ./run_archives.sh generate")
        
        return 0
    
    # Link to existing project if requested
    if args.link:
        project_path = os.path.abspath(args.link)
        if not os.path.exists(project_path):
            print(f"Error: Project path {project_path} does not exist.")
            return 1
        
        # Add warning about correct setup
        print_header("⚠️ CORRECT SETUP VERIFICATION")
        print("Verifying that you're following the correct setup process:")
        print("1. The AI Archives repository should be installed OUTSIDE any existing Git project")
        print("2. You should create a SYMBOLIC LINK from your project to the AI Archives")
        print("3. You should NOT clone the AI Archives inside your project directory")
        print("")
        
        # Check if we're linking from within a git repository to outside
        if os.path.exists(os.path.join(project_path, ".git")):
            # This is good - project_path is a git repo
            if os.path.commonpath([project_path, repo_root]) == project_path:
                print("⚠️ WARNING: It appears the AI Archives is installed INSIDE your project directory.")
                print("This is NOT the recommended setup and may cause Git conflicts.")
                print("The correct setup is to install AI Archives OUTSIDE your project and create a symlink.")
                if not prompt_yes_no("Continue anyway?", default="no"):
                    print("Setup aborted. Please reinstall AI Archives in a separate location.")
                    return 1
        
        # Create a symbolic link to the AI Archives
        sym_link_path = os.path.join(project_path, "ai.archives")
        if os.path.exists(sym_link_path):
            print(f"Warning: {sym_link_path} already exists. Skipping link creation.")
        else:
            os.symlink(repo_root, sym_link_path)
            print(f"✓ Created symbolic link from {project_path} to AI Archives")
        
        # Create a .cursorrules file in the project
        cursorrules_path = os.path.join(project_path, ".cursorrules")
        if os.path.exists(cursorrules_path):
            print(f"Warning: {cursorrules_path} already exists. Skipping file creation.")
        else:
            # Generate a .cursorrules file
            manager = get_archives_manager(data_repo_root=args.data_path)
            cursorrules_content = manager.generate_combined_cursorrules()
            
            with open(cursorrules_path, "w") as f:
                f.write(cursorrules_content)
            
            print(f"✓ Created .cursorrules file in {project_path}")
        
        print("\n✓ Project linked to AI Archives successfully!")
        print("\nYou can now use the archives with:")
        print("  ./ai.archives/run_archives.sh search \"your search term\"")
        
        return 0
    
    # If no specific action requested, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())