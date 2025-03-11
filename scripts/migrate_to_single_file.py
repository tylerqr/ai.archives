#!/usr/bin/env python3
"""
Migrate multiple rule files to a single comprehensive rules file

This script finds all rule files and combines them into a single comprehensive
rules file for easier management and reference.
"""

import os
import sys
import glob
import argparse
from pathlib import Path

def migrate_rules_to_single_file(data_repo_root=None):
    """
    Migrate multiple rule files to a single comprehensive file
    
    Args:
        data_repo_root: Path to the data repository root. If None, tries to auto-detect
        
    Returns:
        Path to the generated file
    """
    print("Migrating rules to a single file...")
    
    # If no data_repo_root is specified, use the current directory
    if data_repo_root is None:
        data_repo_root = os.getcwd()
    
    # Convert to absolute path
    data_repo_root = os.path.abspath(data_repo_root)
    print(f"Using data repository root: {data_repo_root}")
    
    # Create a single rule file in the root directory
    single_file_path = os.path.join(data_repo_root, 'reko-rules.md')
    
    # Find all rule files in various locations
    rule_files = []
    
    # Check for rules in the root directory
    root_rule_files = [f for f in glob.glob(os.path.join(data_repo_root, "*.md"))
                      if os.path.basename(f).lower() not in ['readme.md', 'contributing.md']]
    rule_files.extend(root_rule_files)
    
    # Check old locations for backward compatibility
    legacy_locations = [
        os.path.join(data_repo_root, 'custom_rules'),
        os.path.join(data_repo_root, 'archives', 'custom_rules')
    ]
    
    for legacy_dir in legacy_locations:
        if os.path.exists(legacy_dir):
            legacy_rule_files = [f for f in glob.glob(os.path.join(legacy_dir, "*.md"))]
            rule_files.extend(legacy_rule_files)
    
    if not rule_files:
        print("No rule files found to migrate.")
        return None
    
    print(f"Found {len(rule_files)} rule files to migrate:")
    for rule_file in rule_files:
        print(f"  - {rule_file}")
    
    # Combine all files into one
    combined_content = "# Comprehensive AI Archives Rules\n\n"
    
    for rule_file in rule_files:
        rule_name = os.path.splitext(os.path.basename(rule_file))[0]
        try:
            with open(rule_file, 'r') as f:
                content = f.read()
                
            # Add rule content with header
            combined_content += f"## {rule_name}\n\n"
            combined_content += content
            combined_content += "\n\n"
        except Exception as e:
            print(f"Error reading {rule_file}: {e}")
    
    # Write the combined file
    with open(single_file_path, 'w') as f:
        f.write(combined_content)
    
    print(f"Successfully migrated rules to: {single_file_path}")
    
    return single_file_path

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='Migrate multiple rule files to a single comprehensive file')
    parser.add_argument('--data-path', help='Path to the data repository root')
    
    args = parser.parse_args()
    
    migrate_rules_to_single_file(args.data_path)

if __name__ == "__main__":
    main() 