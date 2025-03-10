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


def format_quick_search_markdown(results, query):
    """Format search results in markdown format optimized for AI agents"""
    if not results:
        return f"No archives found for query: '{query}'. The information you're looking for is not in the archives."
    
    output = f"# Archives Search Results for '{query}'\n\n"
    output += f"Found {len(results)} relevant entries in the archives:\n\n"
    
    for i, result in enumerate(results, 1):
        project = result['project']
        title = result['title']
        file = os.path.basename(result['file'])
        snippet = result['snippet'].strip()
        file_path = result['file']
        
        output += f"## {i}. {title}\n\n"
        output += f"**Project:** {project}  \n"
        output += f"**Location:** {file_path}  \n"
        
        # Add match information if it's a tokenized search result
        if 'score' in result:
            output += f"**Match Quality:** {result['score']} token matches  \n"
        
        output += f"\n### Content Preview:\n\n"
        output += f"{snippet}\n\n"
        output += "----\n\n"
    
    return output


def format_quick_search_text(results, query):
    """Format search results in plain text format optimized for AI agents"""
    if not results:
        return f"No archives found for query: '{query}'. The information you're looking for is not in the archives."
    
    output = f"ARCHIVES SEARCH RESULTS FOR: '{query}'\n"
    output += "=" * 80 + "\n\n"
    output += f"Found {len(results)} relevant entries in the archives:\n\n"
    
    for i, result in enumerate(results, 1):
        project = result['project']
        title = result['title']
        file = os.path.basename(result['file'])
        snippet = result['snippet'].strip()
        file_path = result['file']
        
        output += f"RESULT {i}: {title}\n"
        output += "-" * 80 + "\n"
        output += f"Project: {project}\n"
        output += f"Location: {file_path}\n\n"
        output += f"CONTENT PREVIEW:\n{snippet}\n\n"
    
    return output


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Archives CLI")
    
    # Global options
    parser.add_argument("--data-path", help="Path to the data directory")
    
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
    
    # Quick-search command (optimized for AI agents)
    quick_search_parser = subparsers.add_parser("quick-search", help="AI-optimized search for archives")
    quick_search_parser.add_argument("query", help="Search query")
    quick_search_parser.add_argument("--project", "-p", help="Project to search in (defaults to all)")
    quick_search_parser.add_argument("--format", choices=["markdown", "text"], default="markdown", 
                                    help="Output format (default: markdown)")
    
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
    
    # Get archives manager with data path if specified
    manager = get_archives_manager(data_path=args.data_path)
    
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
        result = manager.add_to_archives(args.project, args.section, content, args.title)
        print(f"Added content to {result}")
    
    elif args.command == "search":
        # Search archives
        results = manager.search_archives(args.query, args.project)
        print(format_results(results))
    
    elif args.command == "quick-search":
        # AI-optimized search across all projects (unless specific project specified)
        results = manager.search_archives(args.query, args.project)
        
        if args.format == "markdown":
            output = format_quick_search_markdown(results, args.query)
        else:
            output = format_quick_search_text(results, args.query)
        
        print(output)
    
    elif args.command == "list":
        # List archives
        projects = [args.project] if args.project else manager.config["settings"]["archive_structure"]["projects"]
        
        for project in projects:
            project_dir = os.path.join(manager.projects_dir, project)
            if not os.path.exists(project_dir):
                continue
            
            sections = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]
            
            print(f"\n{project.upper()} PROJECT:")
            
            for section in sections:
                section_dir = os.path.join(project_dir, section)
                files = [f for f in os.listdir(section_dir) if f.endswith('.md')]
                
                if files:
                    print(f"  {section}: {len(files)} file(s)")
                    for file in files:
                        file_path = os.path.join(section_dir, file)
                        with open(file_path, 'r') as f:
                            first_line = f.readline().strip()
                        
                        title = first_line if first_line.startswith('# ') else file
                        print(f"    - {title[2:] if title.startswith('# ') else title}")
    
    elif args.command == "rule" and args.rule_command == "add":
        # Get rule content from file or argument
        if args.file:
            with open(args.file, 'r') as f:
                content = f.read()
        elif args.content:
            content = args.content
        else:
            print("Error: Either --content or --file must be specified")
            return 1
        
        # Add rule
        result = manager.update_custom_rules(content, args.name)
        print(f"Added rule to {result}")
    
    elif args.command == "rule" and args.rule_command == "list":
        # List rules
        rules = manager.get_custom_rules()
        
        if not rules:
            print("No custom rules found.")
            return 0
        
        print(f"Found {len(rules)} custom rules:")
        
        for i, rule in enumerate(rules, 1):
            name = rule['name']
            file = os.path.basename(rule['file'])
            print(f"{i}. {name} (in {file})")
    
    elif args.command == "generate":
        # Generate combined cursorrules file
        output_path = args.output
        result = manager.generate_combined_cursorrules(output_path)
        print(f"Generated combined cursorrules file at {result}")
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 