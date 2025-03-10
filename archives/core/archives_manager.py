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
        
        # Create or update the rule file
        rule_file = os.path.join(self.custom_rules_dir, f"{rule_name}.md")
        
        with open(rule_file, 'w') as f:
            f.write(rule_content)
        
        return rule_file
    
    def get_custom_rules(self) -> List[Dict[str, str]]:
        """
        Get all custom rules.
        
        Returns:
            List of dictionaries with rule name and content
        """
        if not os.path.exists(self.custom_rules_dir):
            return []
        
        rules = []
        rule_files = glob.glob(os.path.join(self.custom_rules_dir, "*.md"))
        
        for rule_file in rule_files:
            rule_name = os.path.splitext(os.path.basename(rule_file))[0]
            
            try:
                with open(rule_file, 'r') as f:
                    rule_content = f.read()
                
                rules.append({
                    "name": rule_name,
                    "content": rule_content,
                    "file": rule_file
                })
            except Exception as e:
                print(f"Error reading rule file {rule_file}: {str(e)}")
        
        return rules
    
    def generate_combined_cursorrules(self, output_path: Optional[str] = None) -> str:
        """
        Generate a combined cursorrules file with base rules and custom rules.
        
        Args:
            output_path: Optional path for the output file. If None, uses a temporary file.
            
        Returns:
            Path to the generated file
        """
        import tempfile
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
        
        # Combine base content with custom rules
        combined_content = base_content
        
        if custom_rules:
            combined_content += "\n\n# AI Archives - Custom Rules\n\n"
            
            for rule in custom_rules:
                combined_content += f"## {rule['name']}\n\n"
                combined_content += rule['content']
                combined_content += "\n\n"
        
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