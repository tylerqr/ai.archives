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
    
    # Check if running from the AI archives repository
    try:
        manager = get_archives_manager()
        print(f"AI Archives repository found at: {manager.repo_root}")
        print("✓ Repository structure OK")
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True


def setup_ai_archives(target_dir=None):
    """Set up the AI archives system"""
    print_header("Setting up AI Archives")
    
    manager = get_archives_manager()
    
    if target_dir:
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
        required_dirs = ["core", "projects", "custom_rules", "api"]
        for dir_name in required_dirs:
            dir_path = os.path.join(archives_dir, dir_name)
            if not os.path.exists(dir_path):
                print(f"Creating missing directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
        
        # Check for required project directories
        projects_dir = os.path.join(archives_dir, "projects")
        project_dirs = ["frontend", "backend", "shared"]
        for dir_name in project_dirs:
            dir_path = os.path.join(projects_dir, dir_name)
            if not os.path.exists(dir_path):
                print(f"Creating missing project directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
        
        print("\n✓ AI Archives directory structure verified/created.")
    
    return True


def setup_cross_project_links(projects):
    """Set up cross-project links"""
    print_header("Setting up Cross-Project Links")
    
    if not projects:
        print("No projects specified for linking.")
        return True
    
    manager = get_archives_manager()
    
    for project_name, project_path in projects:
        if not os.path.exists(project_path):
            print(f"Warning: Project path does not exist: {project_path}")
            continue
        
        print(f"Linking {project_name} project at {project_path}")
        
        # Create symlink to the AI archives if requested
        if prompt_yes_no(f"Create a symlink to the AI archives in the {project_name} project?"):
            symlink_path = os.path.join(project_path, "ai.archives")
            
            # Remove existing symlink if it exists
            if os.path.exists(symlink_path):
                if os.path.islink(symlink_path):
                    os.unlink(symlink_path)
                else:
                    print(f"Warning: {symlink_path} exists but is not a symlink. Skipping.")
                    continue
            
            # Create symlink
            try:
                os.symlink(manager.repo_root, symlink_path, target_is_directory=True)
                print(f"✓ Created symlink at {symlink_path}")
            except OSError as e:
                print(f"Error creating symlink: {str(e)}")
                continue
        
        # Copy cursorrules file if requested
        if prompt_yes_no(f"Copy the combined .cursorrules file to the {project_name} project?"):
            try:
                # Generate and copy cursorrules file
                combined_path = manager.generate_combined_cursorrules()
                target_path = os.path.join(project_path, ".cursorrules")
                
                with open(combined_path, 'r') as f:
                    content = f.read()
                
                with open(target_path, 'w') as f:
                    f.write(content)
                
                print(f"✓ Copied .cursorrules to {target_path}")
            except Exception as e:
                print(f"Error copying .cursorrules file: {str(e)}")
    
    return True


def create_sample_content():
    """Create sample content in the archives"""
    print_header("Creating Sample Content")
    
    manager = get_archives_manager()
    
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
    
    next_steps = textwrap.dedent("""
    The AI Archives system has been set up successfully. Here are the next steps:
    
    1. Update the archives with project-specific knowledge:
       python scripts/archives_cli.py add --project=frontend --section=setup
    
    2. Search the archives for relevant information:
       python scripts/archives_cli.py search "authentication"
    
    3. Add custom rules for your projects:
       python scripts/archives_cli.py rule add --name=my_rule
    
    4. Generate an updated .cursorrules file with your custom rules:
       python scripts/integrate_cursorrules.py
    
    For more information, consult the README.md file in the AI Archives repository.
    """).strip()
    
    print(next_steps)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Set up the AI Archives system")
    parser.add_argument("--target", "-t", help="Target directory for setup (if different from current repo)")
    parser.add_argument("--link", "-l", action="append", nargs=2, metavar=("NAME", "PATH"),
                        help="Link a project to the AI archives (can be specified multiple times)")
    parser.add_argument("--skip-prereq", action="store_true", help="Skip prerequisites check")
    parser.add_argument("--skip-samples", action="store_true", help="Skip creating sample content")
    
    args = parser.parse_args()
    
    print_header("AI Archives Setup")
    print("This script will set up the AI Archives system for your projects.")
    
    # Check prerequisites
    if not args.skip_prereq and not check_prerequisites():
        print("\nPrerequisites check failed. Please address the issues and try again.")
        return 1
    
    # Set up AI archives
    if not setup_ai_archives(args.target):
        print("\nSetup failed. Please address the issues and try again.")
        return 1
    
    # Set up cross-project links
    if args.link and not setup_cross_project_links(args.link):
        print("\nCross-project link setup failed. Continuing with setup.")
    
    # Create sample content
    if not args.skip_samples and not create_sample_content():
        print("\nSample content creation failed. Continuing with setup.")
    
    # Display next steps
    display_next_steps()
    
    print("\n✓ AI Archives setup completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 