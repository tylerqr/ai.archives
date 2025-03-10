#!/usr/bin/env python3
"""
AI Archives System Setup Script

This script helps users set up the AI archives system in their projects.
It creates the necessary directory structure, initializes the archives,
and can link the system to external projects for cross-project knowledge sharing.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
import json
import subprocess
import textwrap

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


def setup_ai_archives(data_repo=None, target_dir=None):
    """Set up the AI archives system"""
    print_header("Setting up AI Archives")
    
    manager = get_archives_manager()

    # Handle data repository setup
    if data_repo:
        data_repo_path = os.path.abspath(data_repo)
        print(f"Setting up AI Archives data repository at {data_repo_path}")
        
        # Create data repo directory if it doesn't exist
        os.makedirs(data_repo_path, exist_ok=True)
        
        # Check if it's a git repository, if not initialize it
        git_dir = os.path.join(data_repo_path, ".git")
        if not os.path.exists(git_dir):
            if prompt_yes_no(f"Directory {data_repo_path} is not a Git repository. Initialize it?"):
                try:
                    subprocess.run(["git", "init"], cwd=data_repo_path, check=True)
                    print(f"✓ Initialized Git repository at {data_repo_path}")
                except subprocess.SubprocessError as e:
                    print(f"Error initializing Git repository: {str(e)}")
        
        # Create archives directory structure in data repo
        archives_dst = os.path.join(data_repo_path, "archives")
        if not os.path.exists(archives_dst):
            os.makedirs(archives_dst, exist_ok=True)
            
            # Create project directories
            projects_dir = os.path.join(archives_dst, "projects")
            os.makedirs(projects_dir, exist_ok=True)
            
            for project_type in ["frontend", "backend", "shared"]:
                os.makedirs(os.path.join(projects_dir, project_type), exist_ok=True)
            
            # Create custom rules directory
            custom_rules_dir = os.path.join(archives_dst, "custom_rules")
            os.makedirs(custom_rules_dir, exist_ok=True)
            
            print(f"✓ Created archives directory structure in {data_repo_path}")
        
        # Update config to point to the data repository
        config_path = os.path.join(manager.repo_root, 'archives', 'core', 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Add data repository information to config
            if 'data_repository' not in config['settings']:
                config['settings']['data_repository'] = {}
            
            config['settings']['data_repository']['path'] = data_repo_path
            config['settings']['data_repository']['name'] = os.path.basename(data_repo_path)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✓ Updated configuration to use data repository: {data_repo_path}")
        
        # Generate a default .cursorrules file in the data repository
        cursorrules_path = os.path.join(data_repo_path, ".cursorrules")
        if not os.path.exists(cursorrules_path):
            try:
                # Try to generate from source
                manager.generate_combined_cursorrules(cursorrules_path)
                print(f"✓ Generated .cursorrules file at {cursorrules_path}")
            except Exception as e:
                print(f"Warning: Could not generate .cursorrules file: {str(e)}")
                print("You will need to generate the .cursorrules file manually later.")
    
    # Handle target directory setup (for backward compatibility)
    elif target_dir:
        target_path = os.path.abspath(target_dir)
        print(f"Setting up AI Archives in {target_path}")
        
        # Create target directory if it doesn't exist
        os.makedirs(target_path, exist_ok=True)
        
        # Copy archives directory structure to target
        archives_src = os.path.join(manager.repo_root, "archives")
        archives_dst = os.path.join(target_path, "archives")
        
        if os.path.exists(archives_dst):
            if not prompt_yes_no(f"Archives directory already exists at {archives_dst}. Overwrite?", default="no"):
                print("Setup aborted.")
                return False
            shutil.rmtree(archives_dst)
        
        # Copy archives
        shutil.copytree(archives_src, archives_dst)
        
        # Copy scripts
        scripts_src = os.path.join(manager.repo_root, "scripts")
        scripts_dst = os.path.join(target_path, "scripts")
        
        if os.path.exists(scripts_dst):
            if not prompt_yes_no(f"Scripts directory already exists at {scripts_dst}. Overwrite?", default="no"):
                print("Continuing without overwriting scripts.")
            else:
                shutil.rmtree(scripts_dst)
                shutil.copytree(scripts_src, scripts_dst)
        else:
            shutil.copytree(scripts_src, scripts_dst)
        
        # Copy requirements.txt
        requirements_src = os.path.join(manager.repo_root, "requirements.txt")
        requirements_dst = os.path.join(target_path, "requirements.txt")
        
        if os.path.exists(requirements_dst):
            if prompt_yes_no(f"requirements.txt already exists at {requirements_dst}. Overwrite?", default="no"):
                shutil.copy2(requirements_src, requirements_dst)
        else:
            shutil.copy2(requirements_src, requirements_dst)
        
        # Generate a default .cursorrules file
        cursorrules_path = os.path.join(target_path, ".cursorrules")
        if not os.path.exists(cursorrules_path):
            try:
                # Try to generate from source
                manager.generate_combined_cursorrules(cursorrules_path)
            except Exception as e:
                print(f"Warning: Could not generate .cursorrules file: {str(e)}")
                print("You will need to generate the .cursorrules file manually later.")
        
        print("\n✓ AI Archives system files copied successfully.")
    else:
        # Just validate the existing structure
        archives_dir = os.path.join(manager.repo_root, "archives")
        if not os.path.exists(archives_dir):
            print("Error: Archives directory not found.")
            return False
        
        # Check for required subdirectories
        required_dirs = ["core", "api", "examples"]
        for dir_name in required_dirs:
            dir_path = os.path.join(archives_dir, dir_name)
            if not os.path.exists(dir_path):
                print(f"Creating missing directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
        
        print("\n✓ AI Archives directory structure verified/created.")
    
    return True


def setup_cross_project_links(projects, data_repo=None):
    """Set up cross-project links"""
    print_header("Setting up Cross-Project Links")
    
    if not projects:
        print("No projects specified for linking.")
        return True
    
    manager = get_archives_manager()
    
    # Determine data repo path
    data_repo_path = None
    if data_repo:
        data_repo_path = os.path.abspath(data_repo)
    else:
        # Try to get from config
        config_path = os.path.join(manager.repo_root, 'archives', 'core', 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if 'data_repository' in config.get('settings', {}):
                data_repo_path = config['settings']['data_repository'].get('path')
    
    for project_name, project_path in projects:
        if not os.path.exists(project_path):
            print(f"Warning: Project path does not exist: {project_path}")
            continue
        
        print(f"Linking {project_name} project at {project_path}")
        
        # Create symlink to the data repository if needed
        if data_repo_path:
            print(f"Creating a symlink to the data repository in the {project_name} project.")
            data_repo_name = os.path.basename(data_repo_path)
            symlink_path = os.path.join(project_path, data_repo_name)
            
            # Remove existing symlink if it exists
            if os.path.exists(symlink_path):
                if os.path.islink(symlink_path):
                    os.unlink(symlink_path)
                else:
                    print(f"Warning: {symlink_path} exists but is not a symlink. Skipping.")
                    continue
            
            # Create symlink
            try:
                os.symlink(data_repo_path, symlink_path, target_is_directory=True)
                print(f"✓ Created symlink to data repository at {symlink_path}")
            except OSError as e:
                print(f"Error creating symlink: {str(e)}")
                continue
        else:
            print("Warning: No data repository path found. Skipping symlink creation.")
        
        # Copy cursorrules file if requested
        if prompt_yes_no(f"Copy the combined .cursorrules file to the {project_name} project?"):
            try:
                # Use cursorrules from data repo if available
                if data_repo_path and os.path.exists(os.path.join(data_repo_path, ".cursorrules")):
                    source_path = os.path.join(data_repo_path, ".cursorrules")
                else:
                    # Generate and copy cursorrules file
                    source_path = manager.generate_combined_cursorrules()
                
                target_path = os.path.join(project_path, ".cursorrules")
                
                with open(source_path, 'r') as f:
                    content = f.read()
                
                with open(target_path, 'w') as f:
                    f.write(content)
                
                print(f"✓ Copied .cursorrules to {target_path}")
            except Exception as e:
                print(f"Error copying .cursorrules file: {str(e)}")
    
    return True


def create_sample_content(data_repo=None):
    """Create sample content in the archives"""
    print_header("Creating Sample Content")
    
    manager = get_archives_manager()
    
    # Determine the archives directory
    archives_dir = None
    if data_repo:
        archives_dir = os.path.join(os.path.abspath(data_repo), "archives")
    else:
        archives_dir = os.path.join(manager.repo_root, "archives")
    
    if not os.path.exists(archives_dir):
        print(f"Error: Archives directory not found at {archives_dir}")
        return False
    
    if prompt_yes_no("Would you like to create sample content in the archives?", default="no"):
        # Create sample frontend setup entry
        frontend_content = textwrap.dedent("""
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
        
        # Create sample backend API entry
        backend_content = textwrap.dedent("""
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
        
        # Create sample custom rule
        rule_content = textwrap.dedent("""
        # Custom Rule for Code Style
        
        This rule defines the code style conventions for our projects.
        
        ## Formatting
        
        - Use 2 spaces for indentation
        - Use single quotes for string literals
        - Use semicolons at the end of statements
        - Maximum line length: 100 characters
        
        ## Naming Conventions
        
        - Use camelCase for variables and functions
        - Use PascalCase for classes and components
        - Use UPPER_SNAKE_CASE for constants
        """).strip()
        
        manager.update_custom_rules(
            rule_content=rule_content,
            rule_name="code_style"
        )
        print("✓ Created sample custom rule")
    
    return True


def display_next_steps():
    """Display next steps for the user"""
    print_header("Next Steps")
    
    print("""
Here are the next steps to complete your AI Archives setup:

1. Add project-specific knowledge to your archives:
   ```
   python scripts/archives_cli.py add --project=frontend --section=setup --title="Project Setup" --content="Your knowledge here"
   ```

2. Add custom rules:
   ```
   python scripts/archives_cli.py rule add --name=code_style --content="Your rule here"
   ```

3. Generate a combined cursorrules file:
   ```
   python scripts/integrate_cursorrules.py
   ```

4. Start using the archives in your projects!
""")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Archives Setup Script")
    parser.add_argument("--target", help="Target directory for copying archives")
    parser.add_argument("--data-repo", help="Path to the data repository (recommended)")
    parser.add_argument("--link", nargs=2, action="append", metavar=("project_name", "project_path"),
                        help="Link an external project (can be used multiple times)")
    
    args = parser.parse_args()
    
    if not check_prerequisites():
        sys.exit(1)
    
    # Check if both target and data-repo are specified
    if args.target and args.data_repo:
        print("Error: You cannot specify both --target and --data-repo. Choose one approach.")
        sys.exit(1)
    
    projects = args.link or []
    
    # Setup the AI archives
    if not setup_ai_archives(data_repo=args.data_repo, target_dir=args.target):
        sys.exit(1)
    
    # Setup cross-project links
    if projects:
        if not setup_cross_project_links(projects, data_repo=args.data_repo):
            sys.exit(1)
    
    # Create sample content
    create_sample_content(data_repo=args.data_repo)
    
    # Display next steps
    display_next_steps()
    
    print("\nAI Archives setup completed successfully!")
    

if __name__ == "__main__":
    main() 