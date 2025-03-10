#!/usr/bin/env python3
"""
Migrate Custom Rules to Single File

This script migrates existing custom rule files to a single file approach,
combining all rules into reko-rules.md.
"""

import os
import sys
import glob
from pathlib import Path

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

from archives.core.archives_manager import sanitize_content

def migrate_rules_to_single_file(data_repo_root=None):
    """
    Migrate all existing rule files to a single reko-rules.md file.
    
    Args:
        data_repo_root: Path to the data repository root
    
    Returns:
        Path to the new single rules file
    """
    # Determine the data repo root
    if not data_repo_root:
        # Default to the reko repository
        data_repo_root = os.path.join(repo_root, '..', 'ai.archives.reko')
    
    data_repo_root = os.path.abspath(data_repo_root)
    custom_rules_dir = os.path.join(data_repo_root, 'archives', 'custom_rules')
    
    # Ensure the directory exists
    os.makedirs(custom_rules_dir, exist_ok=True)
    
    # Path to the new single rules file
    single_file_path = os.path.join(custom_rules_dir, 'reko-rules.md')
    
    # Check if the single file already exists and read its content
    existing_content = ""
    if os.path.exists(single_file_path):
        with open(single_file_path, 'r') as f:
            existing_content = f.read()
    
    # Get all markdown files except the README and the single file itself
    rule_files = [f for f in glob.glob(os.path.join(custom_rules_dir, '*.md')) 
                 if os.path.basename(f) != 'README.md' and os.path.basename(f) != 'reko-rules.md']
    
    # If no rule files found and no existing content, create a default empty file
    if not rule_files and not existing_content:
        with open(single_file_path, 'w') as f:
            f.write("# Reko Custom Rules\n\nAdd your custom rules here.")
        print(f"Created empty rules file at {single_file_path}")
        return single_file_path
    
    # Process each rule file
    combined_content = existing_content if existing_content else ""
    
    for rule_file in rule_files:
        rule_name = os.path.splitext(os.path.basename(rule_file))[0]
        
        try:
            with open(rule_file, 'r') as f:
                rule_content = f.read()
            
            # Skip if this rule is already in the combined content
            if f"## {rule_name}" in combined_content:
                print(f"Rule '{rule_name}' already exists in the combined file, skipping...")
                continue
            
            # Clean the content
            rule_content = sanitize_content(rule_content)
            
            # Add the rule to the combined content
            if combined_content and not combined_content.endswith("\n\n"):
                combined_content += "\n\n"
            
            combined_content += f"## {rule_name}\n\n{rule_content}\n\n"
            
            print(f"Added rule '{rule_name}' to combined file")
            
            # Optionally, rename the original file as a backup
            backup_file = rule_file + ".bak"
            os.rename(rule_file, backup_file)
            print(f"Moved original file to {backup_file}")
            
        except Exception as e:
            print(f"Error processing rule file {rule_file}: {str(e)}")
    
    # Write the combined content to the single file
    with open(single_file_path, 'w') as f:
        f.write(combined_content)
    
    print(f"Successfully migrated all rules to {single_file_path}")
    return single_file_path

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate custom rules to a single file")
    parser.add_argument("--data-repo", help="Path to the data repository")
    
    args = parser.parse_args()
    
    migrate_rules_to_single_file(args.data_repo)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 