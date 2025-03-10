#!/usr/bin/env python3
"""
Custom Cursorrules Generation Script

This script is a simplified version of integrate_cursorrules.py that directly generates
a custom .cursorrules file with our desired format.
"""

import os
import sys
import requests
from pathlib import Path

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

# Define paths
data_repo_root = os.path.abspath(os.path.join(repo_root, '..', 'ai.archives.reko'))
usage_file_path = os.path.join(repo_root, 'archives', 'custom_rules', 'how-to-use-archive-system.md')
custom_rules_path = os.path.join(data_repo_root, 'archives', 'custom_rules', 'reko-rules.md')
output_path = os.path.join(data_repo_root, '.cursorrules')

print(f"Repo root: {repo_root}")
print(f"Data repo root: {data_repo_root}")
print(f"Usage file path: {usage_file_path}")
print(f"Custom rules path: {custom_rules_path}")
print(f"Output path: {output_path}")

# Fetch base cursorrules from GitHub
base_repo = "grapeot/devin.cursorrules"
base_branch = "multi-agent"
base_file = ".cursorrules"
base_url = f"https://raw.githubusercontent.com/{base_repo}/{base_branch}/{base_file}"

print(f"Fetching base cursorrules from {base_url}...")
response = requests.get(base_url)

if response.status_code != 200:
    print(f"Failed to fetch base cursorrules file: {response.status_code}")
    sys.exit(1)

base_content = response.text
print(f"Successfully fetched base cursorrules ({len(base_content)} characters)")

# Read usage instructions
usage_instructions = ""
if os.path.exists(usage_file_path):
    try:
        with open(usage_file_path, 'r') as f:
            usage_instructions = f.read()
        print(f"Successfully read usage instructions ({len(usage_instructions)} characters)")
    except Exception as e:
        print(f"Error reading usage instructions: {str(e)}")
else:
    print(f"Usage instructions file not found at {usage_file_path}")

# Read custom rules
custom_rules = []
if os.path.exists(custom_rules_path):
    try:
        with open(custom_rules_path, 'r') as f:
            content = f.read()
        
        # Split the content by section headers (## Rule Name)
        rule_sections = [s for s in content.split('## ') if s.strip()]
        
        for section in rule_sections:
            lines = section.strip().split('\n', 1)
            if len(lines) >= 2:
                rule_name = lines[0].strip()
                rule_content = lines[1].strip()
                custom_rules.append({
                    'name': rule_name,
                    'content': rule_content
                })
        
        print(f"Successfully read {len(custom_rules)} custom rules")
    except Exception as e:
        print(f"Error reading custom rules: {str(e)}")
else:
    print(f"Custom rules file not found at {custom_rules_path}")

# Generate combined content
combined_content = ""

# Add reference to archive system usage instructions
print("Adding AI Archives System Reference")
combined_content += "# AI Archives System Reference\n\n"
combined_content += "When asked to interact with the AI Archives system (search archives, add to archives, update rules):\n"

if usage_instructions:
    combined_content += "1. Refer to the usage instructions file at `archives/custom_rules/how-to-use-archive-system.md`\n"
    combined_content += "2. Follow the appropriate protocol for searching, updating, or managing archives\n"
    combined_content += "3. Use the archives CLI commands as documented in the instructions\n"
else:
    combined_content += "Please note that the AI Archives system is installed but usage instructions are not available.\n"
    combined_content += "You can use `python scripts/archives_cli.py` for basic operations.\n"

combined_content += "\n"

# Add custom rules
if custom_rules:
    print("Adding custom rules")
    combined_content += "# AI Archives - Custom Rules\n\n"
    
    for rule in custom_rules:
        combined_content += f"## {rule['name']}\n\n"
        combined_content += rule['content']
        combined_content += "\n\n"

# Add base content last
print("Adding base content")
combined_content += base_content

# Write to output file
print(f"Writing combined content ({len(combined_content)} chars) to {output_path}")
with open(output_path, 'w') as f:
    f.write(combined_content)

print(f"Successfully wrote combined cursorrules file to {output_path}")

# Optionally copy to lc-app
lc_app_path = "/Users/tylerruff/lc-app/.cursorrules"
print(f"Copying to lc-app at {lc_app_path}")
try:
    with open(output_path, 'r') as src:
        content = src.read()
    
    with open(lc_app_path, 'w') as dest:
        dest.write(content)
    
    print(f"Successfully copied to {lc_app_path}")
except Exception as e:
    print(f"Error copying to lc-app: {str(e)}") 