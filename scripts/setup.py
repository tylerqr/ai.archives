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

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

try:
    from archives.core.archives_manager import get_archives_manager
except ImportError:
    print("Error: Could not import archives module. Make sure you're running this script from the correct directory.")
    sys.exit(1)


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
        data_path: Path to the data directory. If None, uses ./data/
        create_examples: Whether to create example archives

    Returns:
        Path to the data directory
    """
    print_header("Setting up AI Archives Data Directory")
    
    # Use default data directory if not specified
    if data_path is None:
        data_path = os.path.join(repo_root, "data")
    
    data_path = os.path.abspath(data_path)
    print(f"Setting up data directory at: {data_path}")
    
    # Create data directory structure
    os.makedirs(data_path, exist_ok=True)
    
    archives_dir = os.path.join(data_path, "archives")
    os.makedirs(archives_dir, exist_ok=True)
    
    projects_dir = os.path.join(archives_dir, "projects")
    os.makedirs(projects_dir, exist_ok=True)
    
    custom_rules_dir = os.path.join(archives_dir, "custom_rules")
    os.makedirs(custom_rules_dir, exist_ok=True)
    
    # Create default project directories
    manager = get_archives_manager()
    for project in manager.config["settings"]["archive_structure"]["projects"]:
        project_dir = os.path.join(projects_dir, project)
        os.makedirs(project_dir, exist_ok=True)
        
        for section in manager.config["settings"]["archive_structure"]["sections"]:
            section_dir = os.path.join(project_dir, section)
            os.makedirs(section_dir, exist_ok=True)
    
    # Copy the default custom rules to the data directory
    source_rules_path = os.path.join(repo_root, "archives", "custom_rules", "custom-rules.md")
    target_rules_path = os.path.join(custom_rules_dir, "custom-rules.md")
    
    if os.path.exists(source_rules_path) and not os.path.exists(target_rules_path):
        shutil.copy2(source_rules_path, target_rules_path)
        print("✓ Copied default custom rules to data directory")
    
    # Update the config file to point to the data directory
    update_config(data_path)
    
    # Create example archives if requested
    if create_examples:
        create_sample_content(data_path)
    
    return data_path


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
        
        config["settings"]["data_directory"] = data_path
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Updated config to use data directory: {data_path}")


def create_sample_content(data_path):
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
        
        ## Project Structure
        
        The frontend project follows a standard React structure with components organized by feature.
        """).strip()
        
        manager.add_to_archives(
            project="frontend",
            section="setup",
            content=frontend_content,
            title="Sample Frontend Setup"
        )
        print("✓ Created sample frontend setup entry")
        
        # Create sample NativeWind documentation
        nativewind_content = textwrap.dedent("""
        # NativeWind Usage Guide
        
        NativeWind is a styling solution for React Native that brings Tailwind CSS to React Native.
        
        ## Installation
        
        1. Install NativeWind:
        ```bash
        npm install nativewind
        npm install --dev tailwindcss@3.3.2
        ```
        
        2. Initialize Tailwind CSS:
        ```bash
        npx tailwindcss init
        ```
        
        3. Configure `tailwind.config.js`:
        ```js
        module.exports = {
          content: ["./App.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
          theme: {
            extend: {},
          },
          plugins: [],
        }
        ```
        
        4. Configure your `babel.config.js` to include NativeWind:
        ```js
        module.exports = {
          presets: ['babel-preset-expo'],
          plugins: ["nativewind/babel"],
        }
        ```
        
        ## Usage
        
        Apply Tailwind classes using the `className` prop:
        
        ```jsx
        import { View, Text } from 'react-native';
        
        export function MyComponent() {
          return (
            <View className="flex-1 items-center justify-center bg-white">
              <Text className="text-blue-600 font-bold text-xl">Hello from NativeWind</Text>
            </View>
          );
        }
        ```
        
        ## Troubleshooting
        
        ### Common Issues
        
        1. Styles not being applied:
           - Make sure you've properly configured your babel.config.js
           - Clear Metro bundler cache: `npx react-native start --reset-cache`
        
        2. TypeScript errors:
           - Add the types in your `app.d.ts` file:
           ```ts
           /// <reference types="nativewind/types" />
           ```
        
        ### Performance Considerations
        
        - Use `className` for dynamic styles that change based on state
        - For completely static styles, consider using StyleSheet for better performance
        """).strip()
        
        manager.add_to_archives(
            project="frontend",
            section="styling",
            content=nativewind_content,
            title="NativeWind Usage Guide"
        )
        print("✓ Created sample NativeWind documentation")
        
        # Create sample backend API entry
        backend_content = textwrap.dedent("""
        # Sample API Documentation
        
        This is a sample entry for the backend API documentation.
        
        ## Authentication API
        
        ### POST /api/auth/login
        
        Authenticates a user and returns a JWT token.
        
        **Request:**
        ```json
        {
          "email": "user@example.com",
          "password": "password"
        }
        ```
        
        **Response:**
        ```json
        {
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "user": {
            "id": "123",
            "email": "user@example.com",
            "name": "John Doe"
          }
        }
        ```
        """).strip()
        
        manager.add_to_archives(
            project="backend",
            section="apis",
            content=backend_content,
            title="Sample API Documentation"
        )
        print("✓ Created sample backend API entry")
    
    return True


def link_to_project(project_path):
    """
    Link the archives to an existing project directory

    Args:
        project_path: Path to the project directory
    """
    print_header(f"Linking Archives to Project: {project_path}")
    
    # Create a .cursorrules file in the project directory
    cursorrules_path = os.path.join(project_path, ".cursorrules")
    
    # Generate cursorrules file
    manager = get_archives_manager()
    output_path = manager.generate_combined_cursorrules(cursorrules_path)
    
    print(f"✓ Generated .cursorrules file at {output_path}")


def display_next_steps(data_path):
    """Display next steps instructions"""
    print_header("Next Steps")
    
    print(textwrap.dedent(f"""
    Here are the next steps to complete your AI Archives setup:
    
    1. Add content to your archives:
       ```
       python scripts/archives_cli.py add --project=frontend --section=setup --title="Project Setup" --content="..."
       ```
       
    2. Search your archives:
       ```
       python scripts/archives_cli.py quick-search "your search query"
       ```
       
    3. Update custom rules:
       ```
       python scripts/archives_cli.py rule add --name=my_rule --content="..."
       ```
       
    4. Regenerate .cursorrules file (after changing custom rules):
       ```
       python scripts/integrate_cursorrules.py
       ```
       
    Your archives are stored in: {data_path}
    
    For more information, please see the README.md and INTEGRATION_GUIDE.md files.
    """))


def install_archives_system(install_path, data_path=None, link_path=None):
    """
    Install the AI Archives system by cloning the repository

    Args:
        install_path: Path where to install the system
        data_path: Path for the data directory (defaults to install_path/data)
        link_path: Path to link the archives to (optional)
    """
    print_header("Installing AI Archives System")
    
    install_path = os.path.abspath(install_path)
    os.makedirs(install_path, exist_ok=True)
    
    # Check if we're already in the repo
    current_repo = repo_root
    target_repo = os.path.join(install_path, "ai.archives")
    
    # If we're installing to a new location, clone the repo
    if current_repo != target_repo:
        if os.path.exists(target_repo):
            print(f"Repository already exists at {target_repo}")
            if not prompt_yes_no(f"Would you like to use the existing repository?", default="yes"):
                print("Installation aborted.")
                return False
        else:
            # Clone the repository
            try:
                print(f"Cloning AI Archives repository to {target_repo}...")
                subprocess.check_call(
                    ["git", "clone", "https://github.com/tylerqr/ai.archives.git", target_repo],
                    cwd=install_path
                )
                print(f"✓ Cloned repository to {target_repo}")
            except subprocess.SubprocessError as e:
                print(f"Error cloning repository: {e}")
                return False
        
        # Set up the data directory
        if data_path is None:
            data_path = os.path.join(target_repo, "data")
        
        # Run setup script in the cloned repository
        subprocess.check_call(
            [sys.executable, "scripts/setup.py", "--data-path", data_path],
            cwd=target_repo
        )
        
        # Link to project if specified
        if link_path:
            subprocess.check_call(
                [sys.executable, "scripts/setup.py", "--link", link_path],
                cwd=target_repo
            )
    else:
        # We're already in the repo, just set up the data directory
        setup_data_directory(data_path)
        
        # Link to project if specified
        if link_path:
            link_to_project(link_path)
    
    return True


def get_project_root_suggestion():
    """
    Suggest a location for installing the AI Archives system,
    avoiding nested git repositories.
    """
    # Try to find the current git repo root
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Suggest a sibling directory to the current git repo
        parent_dir = os.path.dirname(git_root)
        suggestion = os.path.join(parent_dir, "ai.archives")
        
        return suggestion, git_root
    except (subprocess.SubprocessError, FileNotFoundError):
        # If not in a git repo, suggest the current directory
        current_dir = os.path.abspath(os.getcwd())
        suggestion = os.path.join(current_dir, "ai.archives")
        
        return suggestion, None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Archives Setup Script")
    
    # Main operation modes
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install", "-i", action="store_true", help="Install the AI Archives system")
    group.add_argument("--setup-data", "-d", action="store_true", help="Set up the data directory")
    group.add_argument("--link", "-l", metavar="PROJECT_PATH", help="Link archives to an existing project")
    
    # Options
    parser.add_argument("--install-path", metavar="PATH", help="Path where to install the system")
    parser.add_argument("--data-path", metavar="PATH", help="Path for the data directory")
    parser.add_argument("--no-examples", action="store_true", help="Don't create example archives")
    
    args = parser.parse_args()
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Default mode is to set up the data directory if none specified
    if not args.install and not args.setup_data and not args.link:
        args.setup_data = True
    
    # If installing, determine the install path
    if args.install:
        if not args.install_path:
            suggestion, git_root = get_project_root_suggestion()
            
            if git_root:
                print(f"\nAvoid installing inside your existing Git repository: {git_root}")
                print(f"Suggested installation location: {suggestion}")
            
            install_path = input(f"\nWhere would you like to install AI Archives? [{suggestion}]: ")
            if not install_path:
                install_path = suggestion
        else:
            install_path = args.install_path
        
        # Install the system
        install_archives_system(
            install_path=install_path,
            data_path=args.data_path,
            link_path=args.link
        )
    
    # Set up the data directory
    elif args.setup_data:
        setup_data_directory(
            data_path=args.data_path,
            create_examples=not args.no_examples
        )
    
    # Link to an existing project
    elif args.link:
        link_to_project(args.link)
    
    print("\nAI Archives setup completed successfully!")
    
    # Display next steps
    data_path = args.data_path or os.path.join(repo_root, "data")
    display_next_steps(data_path)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 