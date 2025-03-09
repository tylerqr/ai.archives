#!/usr/bin/env python3
"""
Demo script to generate a combined .cursorrules file for demonstration.

This script simulates the functionality of integrate_cursorrules.py but uses
a local mock base file instead of fetching from GitHub.
"""

import os
import sys
import glob
from pathlib import Path

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)


def read_file(file_path):
    """Read a file and return its contents."""
    with open(file_path, 'r') as f:
        return f.read()


def get_custom_rules(custom_rules_dir):
    """Get all custom rules from the directory."""
    rules = []
    
    if not os.path.exists(custom_rules_dir):
        print(f"Warning: Custom rules directory not found: {custom_rules_dir}")
        return rules
    
    for file_path in glob.glob(os.path.join(custom_rules_dir, "*.md")):
        rule_name = os.path.basename(file_path).replace(".md", "")
        content = read_file(file_path)
        
        rules.append({
            "name": rule_name,
            "content": content,
            "file_path": file_path
        })
    
    return rules


def merge_with_custom_rules(base_content, custom_rules):
    """Merge the base cursorrules content with custom rules."""
    print(f"Merging with {len(custom_rules)} custom rules...")
    
    # Add a section for custom rules if it doesn't exist
    if "# AI Archives - Custom Rules" not in base_content:
        merged_content = base_content + "\n\n# AI Archives - Custom Rules\n\n"
    else:
        # Split at the custom rules section to preserve the base content
        parts = base_content.split("# AI Archives - Custom Rules")
        merged_content = parts[0] + "# AI Archives - Custom Rules\n\n"
    
    # Add each custom rule
    for rule in custom_rules:
        print(f"  Adding rule: {rule['name']}")
        merged_content += f"## {rule['name']}\n\n"
        merged_content += rule['content'] + "\n\n"
    
    return merged_content


def write_combined_file(content, output_path):
    """Write the combined cursorrules file."""
    print(f"Writing combined cursorrules to {output_path}...")
    
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully wrote combined cursorrules file ({len(content)} characters)")
    return output_path


def main():
    """Main function."""
    # Set paths
    mock_base_file = os.path.join(script_dir, "mockdata", "base_cursorrules.txt")
    custom_rules_dir = os.path.join(repo_root, "archives", "custom_rules")
    output_path = os.path.join(repo_root, ".cursorrules")
    
    # Check if mock base file exists
    if not os.path.exists(mock_base_file):
        print(f"Error: Mock base file not found: {mock_base_file}")
        return 1
    
    # Read mock base content
    print(f"Reading mock base content from {mock_base_file}...")
    base_content = read_file(mock_base_file)
    
    # Get custom rules
    custom_rules = get_custom_rules(custom_rules_dir)
    
    # Merge with custom rules
    merged_content = merge_with_custom_rules(base_content, custom_rules)
    
    # Write combined file
    combined_path = write_combined_file(merged_content, output_path)
    
    print("\nDone! The combined .cursorrules file has been generated.")
    print(f"You can view it at: {combined_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 