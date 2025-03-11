#!/usr/bin/env python3
"""
Check for custom rules in the AI archives.

This script checks for the presence of custom rules files (like custom-rules.md)
in the repository and makes them available to AI agents as a JSON response.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Try to import from core directly
try:
    from core.archives_manager import get_archives_manager
except ImportError:
    # Fall back to old import path for backward compatibility
    from archives.core.archives_manager import get_archives_manager

def main():
    # Try to use the archives manager first
    try:
        manager = get_archives_manager()
        custom_rules = manager.get_custom_rules()
        
        print(f"Number of custom rules: {len(custom_rules)}")
        for rule in custom_rules:
            print(f"- {rule['name']} ({rule['file']})")
        
        print(json.dumps(custom_rules))
    except Exception as e:
        print(f"Error using archives manager: {str(e)}")
        # Fall back to simple file check
        custom_rules = []
        
        # Check for custom-rules.md in script directory or one level up
        custom_rules_path = os.path.join(script_dir, "custom-rules.md")
        if os.path.exists(custom_rules_path):
            print(f"Found custom-rules.md at {custom_rules_path}")
            custom_rules.append({
                'name': 'custom-rules',
                'content': open(custom_rules_path, 'r').read(),
                'file': custom_rules_path
            })
        
        # Check for app_testing.md
        app_testing_path = os.path.join(script_dir, "app_testing.md")
        if os.path.exists(app_testing_path):
            custom_rules.append({
                'name': 'app_testing',
                'content': open(app_testing_path, 'r').read(),
                'file': app_testing_path
            })
        
        # Check for explicit_permission.md
        explicit_permission_path = os.path.join(script_dir, "explicit_permission.md")
        if os.path.exists(explicit_permission_path):
            custom_rules.append({
                'name': 'explicit_permission',
                'content': open(explicit_permission_path, 'r').read(),
                'file': explicit_permission_path
            })
        
        print(f"\nNumber of custom rules found via fallback: {len(custom_rules)}")
        for rule in custom_rules:
            print(f"- {rule['name']} ({rule['file']})")
        
        print(json.dumps(custom_rules))

if __name__ == "__main__":
    main() 