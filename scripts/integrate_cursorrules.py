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
    
    if not custom_rules:
        return base_content
    
    # Create the custom rules section header
    custom_rules_content = "\n\n# AI Archives - Custom Rules\n\n"
    
    # First, check if we have the AI Archives integration rules
    archives_rules = None
    other_rules = []
    
    for rule in custom_rules:
        if rule['name'].lower() in ['ai_archives_integration', 'archives_integration', 'custom-rules']:
            archives_rules = rule
        else:
            other_rules.append(rule)
    
    # Add the AI Archives integration rules first if they exist
    if archives_rules:
        custom_rules_content += f"## {archives_rules['name']}\n\n"
        custom_rules_content += archives_rules['content'] + "\n\n"
    
    # Add each remaining custom rule
    for rule in other_rules:
        custom_rules_content += f"## {rule['name']}\n\n"
        custom_rules_content += rule['content'] + "\n\n"
    
    # Check if the base content already contains a custom rules section
    if "# AI Archives - Custom Rules" not in base_content:
        # Combine base content with custom rules (at the end)
        merged_content = base_content + custom_rules_content
    else:
        # Replace the existing custom rules section
        parts = base_content.split("# AI Archives - Custom Rules")
        merged_content = parts[0] + "# AI Archives - Custom Rules" + custom_rules_content
    
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
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully wrote combined cursorrules file ({len(content)} characters)")
    return output_path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Integrate AI Archives with Devin.cursorrules")
    
    parser.add_argument("--output", "-o", help="Path to write the combined cursorrules file")
    parser.add_argument("--data-path", "-d", help="Path to the data directory")
    
    args = parser.parse_args()
    
    # Get archives manager and GitHub integration
    manager = get_archives_manager(data_path=args.data_path)
    github = get_github_integration()
    
    # Fetch base cursorrules
    base_content = fetch_base_cursorrules(manager.config, github)
    
    # Get custom rules
    custom_rules = manager.get_custom_rules()
    
    # Merge with custom rules
    merged_content = merge_with_custom_rules(base_content, custom_rules)
    
    # Determine output path
    output_path = args.output
    if not output_path:
        # Default to current directory .cursorrules
        output_path = os.path.join(os.getcwd(), ".cursorrules")
    
    # Write combined file
    write_combined_file(merged_content, output_path)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 