#!/usr/bin/env python3
"""
Integrate AI Archives with Devin.cursorrules

This script handles the integration of the AI archives with the Devin.cursorrules system,
fetching updates from the source repository and merging with custom rules.
"""

import os
import sys
import argparse
import re
from pathlib import Path

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

from archives.core.archives_manager import get_archives_manager
from archives.core.github_integration import get_github_integration

# Regular expression to match ANSI color codes
ANSI_COLOR_PATTERN = re.compile(r'\x1B\[\d+(;\d+)*(;*[mK])')
# Improved regex for error messages
ERROR_MESSAGE_PATTERN = re.compile(r'(\[31m|\[1m|\[22m|\[39m|Usage Error[^\n]*)')
# Regex to fix yarn commands
YARN_COMMAND_PATTERN = re.compile(r'\$ +yarn +run +\[.*?\] +your-script')


def sanitize_content(content):
    """
    Remove ANSI color codes and error messages from the content.
    
    Args:
        content: The content to sanitize
        
    Returns:
        Sanitized content
    """
    # Remove ANSI color codes
    sanitized = ANSI_COLOR_PATTERN.sub('', content)
    
    # Remove error messages
    sanitized = ERROR_MESSAGE_PATTERN.sub('', sanitized)
    
    # Fix yarn commands
    sanitized = YARN_COMMAND_PATTERN.sub('`yarn ios`', sanitized)
    sanitized = sanitized.replace('`yarn ios` ... to build and run on Android simulator or device', '`yarn android` to build and run on Android simulator or device')
    
    # Fix common issues with code command examples
    sanitized = sanitized.replace("<scriptName> ...", "your-script ...")
    
    # Fix multiple consecutive newlines that might appear after removing content
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
    
    return sanitized


def fetch_base_cursorrules(config, github):
    """
    Fetch the base cursorrules file from GitHub.
    
    Args:
        config: Configuration dictionary
        github: GitHub integration instance
        
    Returns:
        Content of the base cursorrules file
    """
    base_repo = config["settings"]["cursorrules"]["base_repo"]
    base_branch = config["settings"]["cursorrules"]["base_branch"]
    base_file = config["settings"]["cursorrules"]["base_file"]
    
    # Check if the base_repo is a full URL or just owner/repo
    if base_repo.startswith("http"):
        print(f"Fetching base cursorrules from {base_repo}:{base_branch}/{base_file}...")
        # For URLs, use requests directly
        import requests
        url = f"{base_repo.rstrip('/')}/{base_file}"
        if base_branch:
            # If it's a GitHub URL, adjust for the branch
            if "github.com" in base_repo:
                url = f"{base_repo.rstrip('/')}/raw/{base_branch}/{base_file}"
            else:
                # For other Git hosts, this might need adjustment
                url = f"{base_repo.rstrip('/')}/{base_branch}/{base_file}"
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch base cursorrules file: {response.status_code}")
            sys.exit(1)
        
        content = response.text
    else:
        # Use the GitHub API for owner/repo format
        print(f"Fetching base cursorrules from {base_repo}:{base_branch}/{base_file}...")
        content = github.fetch_base_cursorrules(
            repo=base_repo,
            branch=base_branch,
            file_path=base_file
        )
    
    if not content:
        print("Failed to fetch base cursorrules file.")
        sys.exit(1)
    
    print(f"Successfully fetched base cursorrules ({len(content)} characters)")
    return content


def merge_with_custom_rules(base_content, custom_rules):
    """
    Merge the base cursorrules content with custom rules.
    
    Places custom rules at the top followed by the base content.
    
    Args:
        base_content: Base cursorrules content
        custom_rules: List of custom rules
        
    Returns:
        Merged content
    """
    # Start with an empty combined content
    combined_content = ""
    
    # First, add a reference to the archive system
    combined_content += "# AI Archives System Reference\n\n"
    combined_content += "When asked to interact with the AI Archives system (search archives, add to archives, update rules):\n"
    combined_content += "1. Refer to the usage instructions file at `archives/custom_rules/how-to-use-archive-system.md`\n"
    combined_content += "2. Follow the appropriate protocol for searching, updating, or managing archives\n"
    combined_content += "3. Use the archives CLI commands as documented in the instructions\n\n"
    
    # Then add the custom rules
    if custom_rules:
        print(f"Merging with {len(custom_rules)} custom rules...")
        combined_content += "# AI Archives - Custom Rules\n\n"
        
        for rule in custom_rules:
            combined_content += f"## {rule['name']}\n\n"
            combined_content += rule['content']
            combined_content += "\n\n"
    
    # Add the base content last
    combined_content += base_content
    
    return combined_content


def write_combined_file(content, output_path):
    """
    Write the combined cursorrules file.
    
    Args:
        content: Combined content to write
        output_path: Path to write the file to
        
    Returns:
        Path to the written file
    """
    print(f"Writing combined cursorrules to {output_path}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully wrote combined cursorrules file ({len(content)} characters)")
    return output_path


def copy_to_project(combined_path, target_project_path):
    """
    Copy the combined cursorrules file to a target project.
    
    Args:
        combined_path: Path to the combined cursorrules file
        target_project_path: Path to the target project
        
    Returns:
        Path to the copied file
    """
    if not os.path.exists(target_project_path):
        print(f"Error: Target project path does not exist: {target_project_path}")
        return None
    
    target_file = os.path.join(target_project_path, '.cursorrules')
    
    print(f"Copying combined cursorrules to {target_file}...")
    
    with open(combined_path, 'r') as f:
        content = f.read()
    
    with open(target_file, 'w') as f:
        f.write(content)
    
    print(f"Successfully copied cursorrules to target project")
    return target_file


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Integrate AI Archives with Devin.cursorrules")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--token", "-t", help="GitHub API token")
    parser.add_argument("--copy-to", "-c", help="Copy the combined file to a target project")
    parser.add_argument("--data-repo", "-d", help="Path to the data repository")
    
    args = parser.parse_args()
    
    # Get archives manager and GitHub integration
    manager = get_archives_manager(data_repo_root=args.data_repo)
    github = get_github_integration(args.token)
    
    # Get config
    config = manager.config
    
    # Set default output path if not provided
    output_path = args.output
    if not output_path:
        # Default to data repository if available, otherwise use main repo
        if hasattr(manager, 'data_repo_root') and manager.data_repo_root != manager.repo_root:
            output_path = os.path.join(manager.data_repo_root, '.cursorrules')
        else:
            output_path = os.path.join(manager.repo_root, '.cursorrules')
    
    # Fetch base cursorrules
    base_content = fetch_base_cursorrules(config, github)
    
    # Get custom rules
    custom_rules = manager.get_custom_rules()
    
    # Merge with custom rules (placing them at the top)
    merged_content = merge_with_custom_rules(base_content, custom_rules)
    
    # Write combined file
    print(f"Writing combined cursorrules to {output_path}...")
    write_combined_file(merged_content, output_path)
    
    # Copy to target project if requested
    if args.copy_to:
        copy_to_project(output_path, args.copy_to)
    
    print(f"Successfully wrote combined cursorrules file ({len(merged_content)} characters)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 