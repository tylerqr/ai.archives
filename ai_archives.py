#!/usr/bin/env python3
"""
AI Archives Wrapper

A simple wrapper script that makes it easy for AI agents to interact with the Archives.
This eliminates environment activation and path issues by providing direct access to archives functions.
"""

import os
import sys
import subprocess
import argparse
from typing import List, Optional

# Default server URL (updated to port 5001 to avoid AirPlay conflicts on macOS)
DEFAULT_SERVER_URL = os.environ.get("ARCHIVES_SERVER_URL", "http://localhost:5001")

def run_command(args: List[str]) -> int:
    """Run a command and return the exit code"""
    try:
        return subprocess.call(args)
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1

def start_server(port: int = 5000) -> int:
    """Start the REST API server"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "server.py")
    
    if not os.path.exists(server_path):
        print(f"Error: Server script not found at {server_path}")
        return 1
    
    # Set environment variable for port
    env = os.environ.copy()
    env["PORT"] = str(port)
    
    print(f"Starting AI Archives server on port {port}...")
    
    # Start the server as a background process
    try:
        subprocess.Popen([sys.executable, server_path], env=env)
        print(f"Server started! Access at http://localhost:{port}")
        print("Use Ctrl+C to stop the server when you're done.")
        return 0
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1

def search_archives(query: str, project: Optional[str] = None, server_url: str = DEFAULT_SERVER_URL) -> int:
    """Search the archives"""
    from archives_client import ArchivesClient
    
    try:
        client = ArchivesClient(server_url)
        result = client.quick_search(query, project, format_type="text")
        print(result)
        return 0
    except Exception as e:
        print(f"Error searching archives: {e}")
        return 1

def add_to_archives(project: str, section: str, content: str, title: Optional[str] = None,
                   server_url: str = DEFAULT_SERVER_URL) -> int:
    """
    Add content to archives
    
    Args:
        project: Project name (e.g., 'frontend', 'backend', 'shared')
        section: Section name (e.g., 'setup', 'errors', 'fixes')
        content: Content to add as properly formatted markdown text.
                IMPORTANT FORMATTING GUIDELINES:
                - Use actual newlines, not escaped newlines (\\n)
                - Use proper markdown headers (# Title, ## Subtitle)
                - Use proper bullet points with spacing (- Item, * Item)
                - Format code using markdown code blocks (```language...```)
                - Ensure proper spacing between elements
                - DO NOT send raw strings with escaped characters
        title: Optional entry title
        server_url: URL of the archives server
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    from archives_client import ArchivesClient
    
    try:
        client = ArchivesClient(server_url)
        result = client.add(project, section, content, title)
        print(f"Successfully added to archives:")
        print(f"File: {result.get('file')}")
        return 0
    except Exception as e:
        print(f"Error adding to archives: {e}")
        return 1

def update_rule(name: str, content: str, server_url: str = DEFAULT_SERVER_URL) -> int:
    """Add or update a custom rule"""
    from archives_client import ArchivesClient
    
    try:
        client = ArchivesClient(server_url)
        result = client.add_rule(name, content)
        print(f"Successfully updated rule '{name}':")
        print(f"File: {result.get('file')}")
        return 0
    except Exception as e:
        print(f"Error updating rule: {e}")
        return 1

def get_rules(server_url: str = DEFAULT_SERVER_URL) -> int:
    """Get all custom rules"""
    from archives_client import ArchivesClient
    
    try:
        client = ArchivesClient(server_url)
        rules = client.get_rules()
        
        print(f"Found {rules.get('count', 0)} custom rules:")
        for i, rule in enumerate(rules.get('rules', []), 1):
            print(f"\n{i}. {rule.get('name', 'Unnamed Rule')}")
            print("-" * 40)
            print(f"Content preview: {rule.get('content', '')[:100]}...")
        
        return 0
    except Exception as e:
        print(f"Error getting rules: {e}")
        return 1

def generate_cursorrules(output_path: Optional[str] = None, server_url: str = DEFAULT_SERVER_URL) -> int:
    """Generate combined cursorrules file and optionally copy to project directory"""
    from archives_client import ArchivesClient
    import os
    
    try:
        client = ArchivesClient(server_url)
        result = client.generate_cursorrules(output_path)
        generated_file = result.get('file')
        print(f"Successfully generated cursorrules file:")
        print(f"File: {generated_file}")
        
        # Try to detect if we're being run from a project directory via symlink
        current_dir = os.getcwd()
        archives_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check if we're running from a symlinked ai.archives directory
        if os.path.exists(os.path.join(current_dir, 'ai.archives')) and \
           os.path.islink(os.path.join(current_dir, 'ai.archives')):
            project_dir = current_dir
            target_file = os.path.join(project_dir, '.cursorrules')
            
            # Ask user if they want to copy the file
            print("\nDetected project directory:", project_dir)
            response = input("Would you like to copy the .cursorrules file to your project? [Y/n] ").lower()
            
            if response in ['', 'y', 'yes']:
                try:
                    import shutil
                    shutil.copy2(generated_file, target_file)
                    print(f"\n✅ Successfully copied .cursorrules to your project:")
                    print(f"   {target_file}")
                    print("\nAI Archives integration is now complete!")
                except Exception as e:
                    print(f"\n❌ Error copying file to project: {e}")
                    print(f"\nTo manually copy the file, run:")
                    print(f"cp {generated_file} {target_file}")
            else:
                print("\nSkipped copying file to project.")
                print(f"\nTo manually copy the file later, run:")
                print(f"cp {generated_file} {target_file}")
        else:
            print("\nNote: Not running from a project directory with AI Archives symlink.")
            print("To complete the integration, copy the generated file to your project:")
            print(f"cp {generated_file} /path/to/your/project/.cursorrules")
        
        return 0
    except Exception as e:
        print(f"Error generating cursorrules: {e}")
        return 1

def list_projects(server_url: str = DEFAULT_SERVER_URL) -> int:
    """List all available projects"""
    from archives_client import ArchivesClient
    
    try:
        client = ArchivesClient(server_url)
        result = client.list_projects()
        
        print(f"Available projects ({result.get('count', 0)}):")
        for project in result.get('projects', []):
            print(f"- {project}")
        
        return 0
    except Exception as e:
        print(f"Error listing projects: {e}")
        return 1

def list_sections(project: str, server_url: str = DEFAULT_SERVER_URL) -> int:
    """List all sections for a project"""
    from archives_client import ArchivesClient
    
    try:
        client = ArchivesClient(server_url)
        result = client.list_sections(project)
        
        print(f"Sections for project '{project}' ({result.get('count', 0)}):")
        for section in result.get('sections', []):
            print(f"- {section}")
        
        return 0
    except Exception as e:
        print(f"Error listing sections: {e}")
        return 1

def copy_cursorrules(target_dir: str, server_url: str = DEFAULT_SERVER_URL) -> int:
    """Copy the generated cursorrules file to a target directory"""
    from archives_client import ArchivesClient
    import os
    import shutil
    
    try:
        # First ensure we have a generated cursorrules file
        client = ArchivesClient(server_url)
        result = client.generate_cursorrules()
        source_file = result.get('file')
        
        # Resolve target directory and file
        target_dir = os.path.abspath(target_dir)
        target_file = os.path.join(target_dir, '.cursorrules')
        
        # Copy the file
        shutil.copy2(source_file, target_file)
        print(f"\n✅ Successfully copied .cursorrules to:")
        print(f"   {target_file}")
        print("\nAI Archives integration is now complete!")
        return 0
    except Exception as e:
        print(f"Error copying cursorrules: {e}")
        return 1

def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Archives Wrapper")
    
    # Add server-url as a global argument
    parser.add_argument("--server-url", 
                        default=DEFAULT_SERVER_URL,
                        help=f"Server URL (default: {DEFAULT_SERVER_URL})")
    
    # Define subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the server")
    server_parser.add_argument("--port", type=int, default=5001, help="Port to run the server on")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search archives")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--project", "-p", help="Project to search in")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add to archives")
    add_parser.add_argument("project", help="Project name")
    add_parser.add_argument("section", help="Section name")
    add_parser.add_argument("content", help="Content to add")
    add_parser.add_argument("title", nargs="?", help="Entry title")
    
    # Rule commands
    rule_add_parser = subparsers.add_parser("rule-add", help="Add/update rule")
    rule_add_parser.add_argument("name", help="Rule name")
    rule_add_parser.add_argument("content", help="Rule content")
    
    rules_parser = subparsers.add_parser("rules", help="List rules")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate cursorrules file")
    generate_parser.add_argument("--output", "-o", help="Output file path")
    
    # Copy cursorrules command
    copy_parser = subparsers.add_parser("copy-cursorrules", help="Copy cursorrules file to target directory")
    copy_parser.add_argument("target_dir", help="Target directory to copy .cursorrules to")
    
    # List projects command
    subparsers.add_parser("projects", help="List all projects")
    
    # List sections command
    sections_parser = subparsers.add_parser("sections", help="List sections for a project")
    sections_parser.add_argument("project", help="Project name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Get server URL from args or environment variable
    server_url = args.server_url
    
    if args.command == "server":
        return start_server(args.port)
    elif args.command == "search":
        return search_archives(args.query, args.project, server_url)
    elif args.command == "add":
        return add_to_archives(args.project, args.section, args.content, args.title, server_url)
    elif args.command == "rule-add":
        return update_rule(args.name, args.content, server_url)
    elif args.command == "rules":
        return get_rules(server_url)
    elif args.command == "generate":
        return generate_cursorrules(args.output, server_url)
    elif args.command == "copy-cursorrules":
        return copy_cursorrules(args.target_dir, server_url)
    elif args.command == "projects":
        return list_projects(server_url)
    elif args.command == "sections":
        return list_sections(args.project, server_url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 