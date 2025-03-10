#!/usr/bin/env python3
"""
AI Archives Manager

This module provides core functionality for managing the AI archives system.
It handles reading, writing, and searching archives, as well as maintaining
custom rules and integrating with the base cursorrules file.
"""

import os
import json
import re
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import tempfile
import shutil

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

class ArchivesManager:
    """
    Main class for managing the AI Archives system.
    """
    
    def __init__(self, repo_root: str = None, data_repo_root: str = None):
        """
        Initialize the ArchivesManager with the repository root path.
        
        Args:
            repo_root: Path to the main repository root. If None, tries to determine automatically.
            data_repo_root: Path to the data repository root. If None, tries to determine from config.
        """
        # Find repo root if not provided
        if repo_root is None:
            self.repo_root = self._find_repo_root()
        else:
            self.repo_root = repo_root
            
        # Load configuration
        self.config_path = os.path.join(self.repo_root, 'archives', 'core', 'config.json')
        self.config = self._load_config()
        
        # Set up data repository path
        if data_repo_root is not None:
            self.data_repo_root = data_repo_root
        elif 'data_repository' in self.config.get('settings', {}) and 'path' in self.config['settings']['data_repository']:
            self.data_repo_root = self.config['settings']['data_repository']['path']
        else:
            # If no data repo specified, use the main repo as data repo for backward compatibility
            self.data_repo_root = self.repo_root
        
        # Setup paths for main repository
        self.archives_dir = os.path.join(self.repo_root, 'archives')
        self.core_dir = os.path.join(self.archives_dir, 'core')
        self.api_dir = os.path.join(self.archives_dir, 'api')
        self.examples_dir = os.path.join(self.archives_dir, 'examples')
        
        # Setup paths for data repository
        self.data_archives_dir = os.path.join(self.data_repo_root, 'archives')
        self.projects_dir = os.path.join(self.data_archives_dir, 'projects')
        self.custom_rules_dir = os.path.join(self.data_archives_dir, 'custom_rules')
        
    def _find_repo_root(self) -> str:
        """
        Find the repository root by looking for the .git directory.
        
        Returns:
            Path to the repository root.
        """
        current_dir = os.getcwd()
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, '.git')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        # If we can't find a .git directory, use the current directory
        return os.getcwd()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration file.
        
        Returns:
            Configuration dictionary.
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default config if file doesn't exist
            return {
                "version": "1.0.0",
                "settings": {
                    "max_file_lines": 500,
                    "default_format": "markdown",
                    "archive_structure": {
                        "projects": ["frontend", "backend", "shared"],
                        "sections": ["setup", "architecture", "errors", "fixes", "apis", "dependencies", "recommendations"]
                    },
                    "cursorrules": {
                        "base_repo": "https://github.com/grapeot/devin.cursorrules",
                        "base_branch": "multi-agent",
                        "base_file": ".cursorrules",
                        "custom_rules_dir": "archives/custom_rules"
                    }
                }
            }
    
    def get_appropriate_archive_file(self, project: str, section: str) -> Tuple[str, bool]:
        """
        Get the appropriate archive file for a given project and section.
        If the file is over the line limit, a new file will be created.
        
        Args:
            project: The project name (e.g., 'frontend', 'backend')
            section: The section name (e.g., 'setup', 'errors')
            
        Returns:
            Tuple of (file_path, is_new_file)
        """
        # Create project and section directories if they don't exist
        project_dir = os.path.join(self.projects_dir, project)
        os.makedirs(project_dir, exist_ok=True)
        
        section_dir = os.path.join(project_dir, section)
        os.makedirs(section_dir, exist_ok=True)
        
        # Get all existing archive files for this section
        archive_files = sorted(glob.glob(os.path.join(section_dir, "*.md")))
        
        if not archive_files:
            # No existing files, create the first one
            new_file = os.path.join(section_dir, f"{section}_001.md")
            return new_file, True
        
        # Check the latest file to see if it's over the line limit
        latest_file = archive_files[-1]
        
        # Get max file lines from config
        max_lines = self.config.get('settings', {}).get('max_file_lines', 500)
        
        try:
            with open(latest_file, 'r') as f:
                line_count = sum(1 for _ in f)
            
            if line_count >= max_lines:
                # Create a new file
                file_number = int(os.path.basename(latest_file).split('_')[1].split('.')[0])
                new_file = os.path.join(section_dir, f"{section}_{file_number+1:03d}.md")
                return new_file, True
            else:
                # Use the existing file
                return latest_file, False
        except Exception as e:
            # If there's an error, create a new file to be safe
            new_file = os.path.join(section_dir, f"{section}_001.md")
            return new_file, True

    def add_to_archives(self, project: str, section: str, content: str, title: Optional[str] = None) -> str:
        """
        Add content to the archives.
        
        Args:
            project: The project name (e.g., 'frontend', 'backend')
            section: The section name (e.g., 'setup', 'errors')
            content: The content to add
            title: Optional title for the entry
            
        Returns:
            Path to the file the content was added to
        """
        # Ensure the data archives directory exists
        os.makedirs(self.data_archives_dir, exist_ok=True)
        
        # Get the appropriate file to add to
        file_path, is_new_file = self.get_appropriate_archive_file(project, section)
        
        # Format the content with timestamp and title
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not title:
            title = f"{section.capitalize()} update"
        
        formatted_content = f"# {title}\n\n"
        formatted_content += f"*Date: {timestamp}*\n\n"
        formatted_content += content
        formatted_content += "\n\n---\n\n"
        
        # Add to the file
        mode = 'w' if is_new_file else 'a'
        with open(file_path, mode) as f:
            f.write(formatted_content)
        
        return file_path
    
    def search_archives(self, query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the archives for a specific query.
        
        Args:
            query: The search query
            project: Optional project to limit the search to
            
        Returns:
            List of matching entries with file path and snippet
        """
        results = []
        
        # Determine which projects to search
        if project:
            projects = [project]
        else:
            projects = self.config["settings"]["archive_structure"]["projects"]
        
        # Search through all the archives
        for proj in projects:
            project_dir = os.path.join(self.projects_dir, proj)
            if not os.path.exists(project_dir):
                continue
                
            for file_path in glob.glob(os.path.join(project_dir, "*.md")):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Simple search (could be enhanced with more sophisticated search algorithms)
                if re.search(query, content, re.IGNORECASE):
                    # Extract the matching section(s)
                    sections = re.split(r'##\s+', content)
                    for section in sections[1:]:  # Skip the first split (file header)
                        if re.search(query, section, re.IGNORECASE):
                            title = section.split('\n')[0].strip()
                            snippet = section[:500] + "..." if len(section) > 500 else section
                            results.append({
                                "file": file_path,
                                "project": proj,
                                "title": title,
                                "snippet": snippet
                            })
        
        return results
    
    def update_custom_rules(self, rule_content: str, rule_name: str) -> str:
        """
        Update or create a custom rule.
        
        Args:
            rule_content: The content of the rule
            rule_name: The name of the rule
            
        Returns:
            Path to the rule file
        """
        # Ensure the data archives and custom rules directories exist
        os.makedirs(self.data_archives_dir, exist_ok=True)
        os.makedirs(self.custom_rules_dir, exist_ok=True)
        
        # Sanitize the rule content to remove ANSI color codes and error messages
        sanitized_content = sanitize_content(rule_content)
        
        # The single rules file
        rules_file = os.path.join(self.custom_rules_dir, "reko-rules.md")
        
        # Check if the file exists and read its content
        existing_content = ""
        if os.path.exists(rules_file):
            with open(rules_file, 'r') as f:
                existing_content = f.read()
        
        # Check if the rule already exists in the file
        rule_section_pattern = re.compile(f"## {re.escape(rule_name)}(.*?)(?:## |$)", re.DOTALL)
        match = rule_section_pattern.search(existing_content)
        
        if match:
            # Update existing rule
            new_content = rule_section_pattern.sub(f"## {rule_name}\n\n{sanitized_content}\n\n", existing_content)
        else:
            # Add new rule
            if existing_content and not existing_content.endswith("\n\n"):
                existing_content += "\n\n"
            new_content = existing_content + f"## {rule_name}\n\n{sanitized_content}\n\n"
        
        # Write the updated content back to the file
        with open(rules_file, 'w') as f:
            f.write(new_content)
        
        return rules_file
    
    def get_custom_rules(self) -> List[Dict[str, str]]:
        """
        Get all custom rules from the single rules file.
        
        Returns:
            List of dictionaries with rule name and content
        """
        rules_file = os.path.join(self.custom_rules_dir, "reko-rules.md")
        
        if not os.path.exists(rules_file):
            return []
        
        rules = []
        
        try:
            with open(rules_file, 'r') as f:
                content = f.read()
            
            # Split the content by section headers (## Rule Name)
            rule_sections = re.split(r'(?=## )', content)
            
            for section in rule_sections:
                if not section.strip():
                    continue
                
                # Get the rule name and content
                match = re.match(r'## (.*?)\n(.*)', section, re.DOTALL)
                if match:
                    rule_name = match.group(1).strip()
                    rule_content = match.group(2).strip()
                    
                    rules.append({
                        "name": rule_name,
                        "content": rule_content,
                        "file": rules_file
                    })
                else:
                    # Handle content without a proper header
                    rules.append({
                        "name": "general",
                        "content": section.strip(),
                        "file": rules_file
                    })
            
        except Exception as e:
            print(f"Error reading rules file {rules_file}: {str(e)}")
        
        return rules
    
    def generate_combined_cursorrules(self, output_path: Optional[str] = None) -> str:
        """
        Generate a combined cursorrules file with base rules and custom rules.
        
        Places custom rules at the top followed by the base content.
        
        Args:
            output_path: Optional path for the output file. If None, uses a file in the data repo.
            
        Returns:
            Path to the generated file
        """
        import requests
        
        # Get base cursorrules file from GitHub
        base_repo = self.config.get('settings', {}).get('cursorrules', {}).get('base_repo')
        base_branch = self.config.get('settings', {}).get('cursorrules', {}).get('base_branch')
        base_file = self.config.get('settings', {}).get('cursorrules', {}).get('base_file')
        
        if not base_repo or not base_branch or not base_file:
            raise ValueError("Missing base repository information in config")
        
        # Fetch base cursorrules content
        base_url = f"https://raw.githubusercontent.com/{base_repo}/{base_branch}/{base_file}"
        response = requests.get(base_url)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch base cursorrules file: {response.status_code}")
        
        base_content = response.text
        
        # Get custom rules
        custom_rules = self.get_custom_rules()
        
        # Check if archive system usage instructions file exists
        usage_file_path = os.path.join(self.repo_root, 'archives', 'custom_rules', 'how-to-use-archive-system.md')
        has_usage_instructions = os.path.exists(usage_file_path)
        
        # Initialize combined content
        combined_content = ""
        
        # Add reference to archive system usage instructions
        combined_content += "# AI Archives System Reference\n\n"
        combined_content += "When asked to interact with the AI Archives system (search archives, add to archives, update rules):\n"
        
        if has_usage_instructions:
            combined_content += "1. Refer to the usage instructions file at `archives/custom_rules/how-to-use-archive-system.md`\n"
            combined_content += "2. Follow the appropriate protocol for searching, updating, or managing archives\n"
            combined_content += "3. Use the archives CLI commands as documented in the instructions\n"
        else:
            combined_content += "Please note that the AI Archives system is installed but usage instructions are not available.\n"
            combined_content += "You can use `python scripts/archives_cli.py` for basic operations.\n"
        
        combined_content += "\n"
        
        # Add custom rules after the instructions
        if custom_rules:
            combined_content += "# AI Archives - Custom Rules\n\n"
            
            # Since all rules are now in a single file, we just add them with their section headers
            for rule in custom_rules:
                combined_content += f"## {rule['name']}\n\n"
                combined_content += rule['content']
                combined_content += "\n\n"
        
        # Add the base content last
        combined_content += base_content
        
        # Write to output file
        if output_path:
            output_file = output_path
        else:
            # If no output path specified, use a file in the data repo
            output_file = os.path.join(self.data_repo_root, ".cursorrules")
        
        with open(output_file, 'w') as f:
            f.write(combined_content)
        
        return output_file


def get_archives_manager(repo_root: str = None, data_repo_root: str = None) -> ArchivesManager:
    """
    Get an instance of the ArchivesManager.
    
    Args:
        repo_root: Optional path to the repository root
        data_repo_root: Optional path to the data repository root
        
    Returns:
        ArchivesManager instance
    """
    return ArchivesManager(repo_root=repo_root, data_repo_root=data_repo_root)


if __name__ == "__main__":
    # Example usage
    manager = get_archives_manager()
    print(f"Repository root: {manager.repo_root}")
    print(f"Archives directory: {manager.archives_dir}") 