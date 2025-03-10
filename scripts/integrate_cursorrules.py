#!/usr/bin/env python3
"""
Integrate AI Archives with Devin.cursorrules

This script handles the integration of the AI archives with the Devin.cursorrules system,
fetching updates from the source repository and merging with custom rules.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

from archives.core.archives_manager import get_archives_manager
from archives.core.github_integration import get_github_integration


def fetch_base_cursorrules(config, github):
    """
    Fetch the base cursorrules file from the source repository.
    
    Args:
        config: Configuration dictionary
        github: GitHubIntegration instance
        
    Returns:
        Content of the cursorrules file
    """
    base_repo = config["settings"]["cursorrules"]["base_repo"]
    base_branch = config["settings"]["cursorrules"]["base_branch"]
    base_file = config["settings"]["cursorrules"]["base_file"]
    
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
    
    Args:
        base_content: Content of the base cursorrules file
        custom_rules: List of custom rule dictionaries
        
    Returns:
        Merged content
    """
    print(f"Merging with {len(custom_rules)} custom rules...")
    
    # Create the custom rules section
    custom_rules_content = "# AI Archives - Custom Rules\n\n"
    
    # Add each custom rule
    for rule in custom_rules:
        custom_rules_content += f"## {rule['name']}\n\n"
        custom_rules_content += rule['content'] + "\n\n"
    
    # Combine custom rules (at the top) with base content
    merged_content = custom_rules_content + "\n" + base_content
    
    return merged_content


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
    
    args = parser.parse_args()
    
    # Get archives manager and GitHub integration
    manager = get_archives_manager()
    github = get_github_integration(args.token)
    
    # Get config
    config = manager.config
    
    # Set default output path if not provided
    output_path = args.output
    if not output_path:
        output_path = os.path.join(manager.repo_root, '.cursorrules')
    
    # Fetch base cursorrules
    base_content = fetch_base_cursorrules(config, github)
    
    # Get custom rules
    custom_rules = manager.get_custom_rules()
    
    # Merge with custom rules
    merged_content = merge_with_custom_rules(base_content, custom_rules)
    
    # Write combined file
    combined_path = write_combined_file(merged_content, output_path)
    
    # Copy to target project if specified
    if args.copy_to:
        copy_to_project(combined_path, args.copy_to)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 