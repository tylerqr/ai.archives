#!/usr/bin/env python3
"""
AI Archives CLI

Command-line interface for interacting with the AI Archives system.
"""

import os
import sys
import argparse
import textwrap
import re
import json
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


def format_history_logs(logs):
    """Format history logs for display"""
    if not logs:
        return "No matching logs found."
    
    output = f"Found {len(logs)} history logs:\n\n"
    
    for i, log in enumerate(logs, 1):
        timestamp = log['timestamp']
        action = log['action']
        file = os.path.basename(log['file'])
        
        # Extract decision explanation if available
        decision_explanation = ""
        match = re.search(r'## Decision Explanation\s+\n(.*?)(?=\n## |$)', log['content'], re.DOTALL)
        if match:
            decision_explanation = match.group(1).strip()
            decision_explanation = textwrap.fill(decision_explanation, width=80)
            decision_explanation = textwrap.indent(decision_explanation, '    ')
        
        output += f"{i}. [{timestamp}] {action} (in {file})\n"
        if decision_explanation:
            output += f"Decision: {decision_explanation}\n"
        output += "\n"
    
    return output


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Archives CLI")
    
    # Global options
    parser.add_argument("--data-repo", help="Path to the data repository")
    
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

    # History commands
    history_parser = subparsers.add_parser("history", help="Manage history logs")
    history_subparsers = history_parser.add_subparsers(dest="history_command", help="History commands")
    
    # List history logs
    list_history_parser = history_subparsers.add_parser("list", help="List history logs")
    list_history_parser.add_argument("--action", "-a", help="Filter by action type")
    list_history_parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum number of logs to show")
    
    # Search history logs
    search_history_parser = history_subparsers.add_parser("search", help="Search through history logs")
    search_history_parser.add_argument("query", help="Search query")
    search_history_parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum number of logs to show")
    
    # View history log
    view_history_parser = history_subparsers.add_parser("view", help="View a specific history log")
    view_history_parser.add_argument("log_file", help="Log file name or path")
    
    # Toggle history logging
    toggle_history_parser = history_subparsers.add_parser("toggle", help="Enable or disable history logging")
    toggle_history_parser.add_argument("--enable", action="store_true", help="Enable history logging")
    toggle_history_parser.add_argument("--disable", action="store_true", help="Disable history logging")
    
    # Cleanup history logs
    cleanup_history_parser = history_subparsers.add_parser("cleanup", help="Remove old history logs")
    cleanup_history_parser.add_argument("--days", "-d", type=int, help="Override retention period (days)")
    cleanup_history_parser.add_argument("--force", "-f", action="store_true", help="Force cleanup without confirmation")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get archives manager with data repository if specified
    manager = get_archives_manager(data_repo_root=args.data_repo)
    
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
    
    elif args.command == "history" and args.history_command == "list":
        # List history logs
        logs = manager.get_history_logs(args.action, args.limit)
        print(format_history_logs(logs))
        
    elif args.command == "history" and args.history_command == "search":
        # Search history logs
        logs = manager.search_history_logs(args.query, args.limit)
        print(format_history_logs(logs))
        
    elif args.command == "history" and args.history_command == "view":
        # Get the log file path
        log_file = args.log_file
        
        # If it's just a filename, construct the full path
        if not os.path.dirname(log_file):
            log_file = os.path.join(manager.history_log_dir, log_file)
            
        # If it still doesn't have an extension, add .md
        if not os.path.splitext(log_file)[1]:
            log_file += ".md"
            
        # Check if the file exists
        if not os.path.exists(log_file):
            print(f"Error: Log file {log_file} not found")
            return 1
            
        # Read and display the content
        with open(log_file, 'r') as f:
            print(f.read())
            
    elif args.command == "history" and args.history_command == "toggle":
        # Get current config
        config_path = os.path.join(manager.repo_root, 'archives', 'core', 'config.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        # Update history logging setting
        if args.enable and args.disable:
            print("Error: Cannot specify both --enable and --disable")
            return 1
            
        if args.enable:
            if not 'history_logging' in config['settings']:
                config['settings']['history_logging'] = {}
            config['settings']['history_logging']['enabled'] = True
            print("History logging enabled")
        elif args.disable:
            if not 'history_logging' in config['settings']:
                config['settings']['history_logging'] = {}
            config['settings']['history_logging']['enabled'] = False
            print("History logging disabled")
        else:
            # Just display current status
            enabled = config['settings'].get('history_logging', {}).get('enabled', True)
            print(f"History logging is currently {'enabled' if enabled else 'disabled'}")
            return 0
            
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    elif args.command == "history" and args.history_command == "cleanup":
        # Get confirmation if not forced
        days = args.days
        force = args.force
        
        # Perform cleanup
        removed_count = manager.cleanup_history_logs(days, force)
        print(f"Cleanup complete. Removed {removed_count} history logs.")
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 