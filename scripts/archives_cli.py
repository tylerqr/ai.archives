#!/usr/bin/env python3
"""
AI Archives CLI

Command-line interface for interacting with the AI Archives system.
"""

import os
import sys
import argparse
import textwrap
from pathlib import Path

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

from archives.core.archives_manager import get_archives_manager


def format_results(results):
    """Format search results for display"""
    if not results:
        return "No matching results found."
    
    output = f"Found {len(results)} matching entries:\n\n"
    
    for i, result in enumerate(results, 1):
        project = result['project']
        title = result['title']
        file = os.path.basename(result['file'])
        snippet = result['snippet'].strip()
        
        # Wrap and indent the snippet for better readability
        wrapped_snippet = textwrap.indent(
            textwrap.fill(snippet, width=80), 
            '    '
        )
        
        output += f"{i}. [{project}] {title} (in {file})\n{wrapped_snippet}\n\n"
    
    return output


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Archives CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add content to archives")
    add_parser.add_argument("--project", "-p", required=True, help="Project name")
    add_parser.add_argument("--section", "-s", required=True, help="Section name")
    add_parser.add_argument("--title", "-t", help="Entry title")
    add_parser.add_argument("--content", "-c", help="Content to add")
    add_parser.add_argument("--file", "-f", help="File containing content to add")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search archives")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--project", "-p", help="Project to search in")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available archives")
    list_parser.add_argument("--project", "-p", help="Project to list")
    
    # Rule commands
    rule_parser = subparsers.add_parser("rule", help="Manage custom rules")
    rule_subparsers = rule_parser.add_subparsers(dest="rule_command", help="Rule commands")
    
    # Add rule
    add_rule_parser = rule_subparsers.add_parser("add", help="Add custom rule")
    add_rule_parser.add_argument("--name", "-n", required=True, help="Rule name")
    add_rule_parser.add_argument("--content", "-c", help="Rule content")
    add_rule_parser.add_argument("--file", "-f", help="File containing rule content")
    
    # List rules
    list_rule_parser = rule_subparsers.add_parser("list", help="List custom rules")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate combined cursorrules file")
    generate_parser.add_argument("--output", "-o", help="Output file path")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get archives manager
    manager = get_archives_manager()
    
    if args.command == "add":
        # Get content from file or argument
        if args.file:
            with open(args.file, 'r') as f:
                content = f.read()
        elif args.content:
            content = args.content
        else:
            print("Error: Either --content or --file must be specified")
            return 1
        
        # Add to archives
        file_path = manager.add_to_archives(
            project=args.project,
            section=args.section,
            content=content,
            title=args.title
        )
        print(f"Content added to {file_path}")
    
    elif args.command == "search":
        results = manager.search_archives(
            query=args.query,
            project=args.project
        )
        print(format_results(results))
    
    elif args.command == "list":
        projects_dir = manager.projects_dir
        if args.project:
            project_dir = os.path.join(projects_dir, args.project)
            if not os.path.exists(project_dir):
                print(f"Project '{args.project}' not found")
                return 1
            
            print(f"Archives for project '{args.project}':")
            for file_path in sorted(Path(project_dir).glob("*.md")):
                print(f"  {file_path.name}")
        else:
            print("Available projects:")
            for project in sorted(os.listdir(projects_dir)):
                if os.path.isdir(os.path.join(projects_dir, project)):
                    print(f"  {project}")
    
    elif args.command == "rule":
        if args.rule_command == "add":
            # Get content from file or argument
            if args.file:
                with open(args.file, 'r') as f:
                    content = f.read()
            elif args.content:
                content = args.content
            else:
                print("Error: Either --content or --file must be specified")
                return 1
            
            # Add rule
            file_path = manager.update_custom_rules(
                rule_content=content,
                rule_name=args.name
            )
            print(f"Rule added to {file_path}")
        
        elif args.rule_command == "list":
            rules = manager.get_custom_rules()
            if not rules:
                print("No custom rules found")
            else:
                print("Custom rules:")
                for rule in rules:
                    print(f"  {rule['name']} ({rule['file_path']})")
        
        else:
            print("Error: Missing rule command")
            return 1
    
    elif args.command == "generate":
        output_path = manager.generate_combined_cursorrules(
            output_path=args.output
        )
        print(f"Combined cursorrules file generated at {output_path}")
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 