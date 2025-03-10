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
                    subprocess.check_call(["git", "init"], cwd=data_repo_path)
                    print(f"Initialized Git repository at {data_repo_path}")
                except subprocess.SubprocessError:
                    print(f"Warning: Could not initialize Git repository at {data_repo_path}")
        
        # Create archive directory structure
        print("Creating archive directory structure...")
        archives_dir = os.path.join(data_repo_path, "archives")
        os.makedirs(archives_dir, exist_ok=True)
        
        projects_dir = os.path.join(archives_dir, "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        custom_rules_dir = os.path.join(archives_dir, "custom_rules")
        os.makedirs(custom_rules_dir, exist_ok=True)
        
        # Create script proxies directory
        scripts_dir = os.path.join(data_repo_path, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Create proxy scripts that point to the main repo
        create_proxy_scripts(data_repo_path, repo_root)
        
        # Default project structure
        for project in manager.config["settings"]["archive_structure"]["projects"]:
            project_dir = os.path.join(projects_dir, project)
            os.makedirs(project_dir, exist_ok=True)
            
            for section in manager.config["settings"]["archive_structure"]["sections"]:
                section_dir = os.path.join(project_dir, section)
                os.makedirs(section_dir, exist_ok=True)
        
        # Create a README.md file
        readme_path = os.path.join(data_repo_path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, 'w') as f:
                f.write(textwrap.dedent("""
                # AI Archives Data Repository
                
                This repository stores the actual archive content for the AI Archives system. It's separated from the system code to allow independent versioning and management of archive content.
                
                ## Repository Structure
                
                ```
                ai.archives-data/
                └── archives/
                    ├── custom_rules/   # Custom rules for AI agents
                    └── projects/       # Project-specific knowledge archives
                        ├── frontend/   # Frontend-specific archives
                        │   ├── setup/  # Setup guides
                        │   ├── errors/ # Common errors and solutions
                        │   └── ...     # Other frontend categories
                        ├── backend/    # Backend-specific archives
                        │   ├── apis/   # API documentation
                        │   ├── db/     # Database schema and queries
                        │   └── ...     # Other backend categories
                        └── shared/     # Shared knowledge
                            ├── architecture/ # System architecture
                            └── ...     # Other shared categories
                ```
                
                This repository is designed to be used with the [AI Archives system](https://github.com/tylerqr/ai.archives). It should be linked via symlinks as described in the integration guide.
                
                DO NOT DIRECTLY MODIFY FILES in this repository - all interactions should happen through the AI Archives system's CLI tools.
                """).strip())
        
        return data_repo_path
    
    return None


def create_proxy_scripts(data_repo_path, main_repo_path):
    """Create proxy scripts in the data repo that point to scripts in the main repo"""
    print("Creating proxy scripts in data repo...")
    
    scripts_dir = os.path.join(data_repo_path, "scripts")
    
    # Create the regenerate_cursorrules.py proxy script
    regenerate_script_path = os.path.join(scripts_dir, "regenerate_cursorrules.py")
    with open(regenerate_script_path, 'w') as f:
        f.write(textwrap.dedent(f"""#!/usr/bin/env python3
        \"\"\"
        Proxy script to regenerate the .cursorrules file
        
        This script finds the main AI Archives repository and calls the integrate_cursorrules.py script there.
        \"\"\"
        
        import os
        import sys
        import subprocess
        
        # The main repo is configured during setup
        MAIN_REPO_PATH = {repr(os.path.abspath(main_repo_path))}
        
        def main():
            # Check if the path exists
            if not os.path.exists(MAIN_REPO_PATH):
                print(f"Error: Main repository not found at {{MAIN_REPO_PATH}}")
                print("Please update the MAIN_REPO_PATH in this script to point to your main AI Archives repository.")
                return 1
            
            # The actual script we want to run
            target_script = os.path.join(MAIN_REPO_PATH, "scripts", "integrate_cursorrules.py")
            
            if not os.path.exists(target_script):
                print(f"Error: Script not found at {{target_script}}")
                return 1
            
            # Pass all arguments to the target script
            print(f"Running {{target_script}}...")
            result = subprocess.call([sys.executable, target_script] + sys.argv[1:])
            return result
        
        if __name__ == "__main__":
            sys.exit(main())
        """))
    
    # Make the script executable
    os.chmod(regenerate_script_path, 0o755)
    
    # Create the search_archives.py proxy script
    search_script_path = os.path.join(scripts_dir, "search_archives.py")
    with open(search_script_path, 'w') as f:
        f.write(textwrap.dedent(f"""#!/usr/bin/env python3
        \"\"\"
        Proxy script to search the archives
        
        This script finds the main AI Archives repository and calls the archives_cli.py script there.
        \"\"\"
        
        import os
        import sys
        import subprocess
        
        # The main repo is configured during setup
        MAIN_REPO_PATH = {repr(os.path.abspath(main_repo_path))}
        DATA_REPO_PATH = {repr(os.path.abspath(data_repo_path))}
        
        def main():
            # Check if the path exists
            if not os.path.exists(MAIN_REPO_PATH):
                print(f"Error: Main repository not found at {{MAIN_REPO_PATH}}")
                print("Please update the MAIN_REPO_PATH in this script to point to your main AI Archives repository.")
                return 1
            
            # The actual script we want to run
            target_script = os.path.join(MAIN_REPO_PATH, "scripts", "archives_cli.py")
            
            if not os.path.exists(target_script):
                print(f"Error: Script not found at {{target_script}}")
                return 1
            
            # Default to quick-search if no command is specified
            args = sys.argv[1:]
            if not args or args[0] not in ['search', 'quick-search', 'add', 'list', 'rule', 'generate']:
                # If the first arg is not a command, assume it's a search query
                if args:
                    args = ['quick-search'] + args
                else:
                    print("Usage: python search_archives.py [command] [options]")
                    print("Commands: search, quick-search, add, list, rule, generate")
                    print("For quick search: python search_archives.py \"your search query\"")
                    return 1
            
            # Add the data repo location
            args = ['--data-repo', DATA_REPO_PATH] + args
            
            # Pass arguments to the target script
            cmd = [sys.executable, target_script] + args
            print(f"Running: {{' '.join(cmd)}}")
            result = subprocess.call(cmd)
            return result
        
        if __name__ == "__main__":
            sys.exit(main())
        """))
    
    # Make the script executable
    os.chmod(search_script_path, 0o755)
    
    # Create a readme for the scripts directory
    readme_path = os.path.join(scripts_dir, "README.md")
    with open(readme_path, 'w') as f:
        f.write(textwrap.dedent(f"""
        # AI Archives Proxy Scripts
        
        These scripts provide convenient access to the AI Archives main repository scripts. They are configured to automatically find the main repository at:
        
        ```
        {os.path.abspath(main_repo_path)}
        ```
        
        If you've moved your main repository, please update the `MAIN_REPO_PATH` variable in each script.
        
        ## Available Scripts
        
        * `regenerate_cursorrules.py` - Regenerates the .cursorrules file with the latest custom rules
        * `search_archives.py` - Search the archives (simplifies access to archives_cli.py)
        
        ## Usage
        
        Run the scripts from this directory:
        
        ```bash
        # Regenerate the .cursorrules file
        python regenerate_cursorrules.py
        
        # Quick search the archives
        python search_archives.py "your search query"
        
        # Other archive operations 
        python search_archives.py add --project=frontend --section=styling --title="CSS Grid Guide" --content="..."
        ```
        """).strip())
    
    print(f"✓ Created proxy scripts in {scripts_dir}")
    
    return scripts_dir


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
        
        # Create symlink to the data repository if needed and requested
        if data_repo_path and prompt_yes_no(f"Create a symlink to the data repository in the {project_name} project?"):
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
        
        # Copy over the AI Archives System Integration Rules
        try:
            source_rules_path = os.path.join(manager.repo_root, "archives", "custom_rules", "custom-rules.md")
            if os.path.exists(source_rules_path):
                with open(source_rules_path, 'r') as f:
                    archives_rules_content = f.read()
                
                manager.update_custom_rules(
                    rule_content=archives_rules_content,
                    rule_name="ai_archives_integration"
                )
                print("✓ Added AI Archives System Integration Rules")
        except Exception as e:
            print(f"Warning: Could not copy AI Archives System Integration Rules: {e}")
    
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