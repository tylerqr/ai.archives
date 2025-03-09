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
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the ArchivesManager with the repository root path.
        
        Args:
            repo_root: Path to the repository root. If None, tries to determine automatically.
        """
        # Find repo root if not provided
        if repo_root is None:
            self.repo_root = self._find_repo_root()
        else:
            self.repo_root = repo_root
            
        # Load configuration
        self.config_path = os.path.join(self.repo_root, 'archives', 'core', 'config.json')
        self.config = self._load_config()
        
        # Setup paths
        self.archives_dir = os.path.join(self.repo_root, 'archives')
        self.projects_dir = os.path.join(self.archives_dir, 'projects')
        self.custom_rules_dir = os.path.join(self.archives_dir, 'custom_rules')
        self.api_dir = os.path.join(self.archives_dir, 'api')
        
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
            Tuple of (file_path, is_new)
        """
        # Validate project and section
        valid_projects = self.config["settings"]["archive_structure"]["projects"]
        valid_sections = self.config["settings"]["archive_structure"]["sections"]
        
        if project not in valid_projects:
            raise ValueError(f"Invalid project: {project}. Valid projects are: {valid_projects}")
        
        if section not in valid_sections:
            raise ValueError(f"Invalid section: {section}. Valid sections are: {valid_sections}")
        
        # Find all existing files for this project/section
        project_dir = os.path.join(self.projects_dir, project)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir, exist_ok=True)
        
        # Pattern: section_name_YYYY-MM-DD.md
        pattern = f"{section}_*.md"
        matching_files = sorted(glob.glob(os.path.join(project_dir, pattern)))
        
        max_lines = self.config["settings"]["max_file_lines"]
        
        if not matching_files:
            # No files exist yet, create a new one
            today = datetime.now().strftime("%Y-%m-%d")
            new_file = os.path.join(project_dir, f"{section}_{today}.md")
            return new_file, True
        
        # Check the most recent file
        latest_file = matching_files[-1]
        
        # Count lines in the file
        with open(latest_file, 'r') as f:
            line_count = sum(1 for _ in f)
        
        if line_count >= max_lines:
            # File is too big, create a new one
            today = datetime.now().strftime("%Y-%m-%d")
            new_file = os.path.join(project_dir, f"{section}_{today}.md")
            return new_file, True
        
        # Use the existing file
        return latest_file, False
        
    def add_to_archives(self, project: str, section: str, content: str, title: Optional[str] = None) -> str:
        """
        Add new content to the appropriate archive file.
        
        Args:
            project: The project name (e.g., 'frontend', 'backend')
            section: The section name (e.g., 'setup', 'errors')
            content: The content to add
            title: Optional title for the entry
            
        Returns:
            Path to the updated file
        """
        file_path, is_new = self.get_appropriate_archive_file(project, section)
        
        # Format the entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_new:
            # Create a new file with header
            entry = f"# {project.capitalize()} Project - {section.capitalize()} Archives\n\n"
            entry += f"## {title or f'Entry on {timestamp}'}\n\n"
            entry += f"*Added on: {timestamp}*\n\n"
            entry += content + "\n\n---\n\n"
        else:
            # Append to existing file
            entry = f"## {title or f'Entry on {timestamp}'}\n\n"
            entry += f"*Added on: {timestamp}*\n\n"
            entry += content + "\n\n---\n\n"
        
        # Write to file
        mode = 'w' if is_new else 'a'
        with open(file_path, mode) as f:
            f.write(entry)
        
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
        Add or update a custom rule.
        
        Args:
            rule_content: The content of the rule
            rule_name: The name of the rule file (without extension)
            
        Returns:
            Path to the rule file
        """
        if not os.path.exists(self.custom_rules_dir):
            os.makedirs(self.custom_rules_dir, exist_ok=True)
        
        rule_path = os.path.join(self.custom_rules_dir, f"{rule_name}.md")
        
        with open(rule_path, 'w') as f:
            f.write(rule_content)
        
        return rule_path
    
    def get_custom_rules(self) -> List[Dict[str, str]]:
        """
        Get all custom rules.
        
        Returns:
            List of rule dictionaries with name and content
        """
        rules = []
        
        if not os.path.exists(self.custom_rules_dir):
            return rules
        
        for file_path in glob.glob(os.path.join(self.custom_rules_dir, "*.md")):
            rule_name = os.path.basename(file_path).replace(".md", "")
            with open(file_path, 'r') as f:
                content = f.read()
            
            rules.append({
                "name": rule_name,
                "content": content,
                "file_path": file_path
            })
        
        return rules
    
    def generate_combined_cursorrules(self, output_path: Optional[str] = None) -> str:
        """
        Generate a combined cursorrules file from the base file and custom rules.
        
        Args:
            output_path: Optional path for the output file. If None, uses .cursorrules in repo root.
            
        Returns:
            Path to the generated file
        """
        if output_path is None:
            output_path = os.path.join(self.repo_root, '.cursorrules')
        
        # Get the base cursorrules content
        base_repo = self.config["settings"]["cursorrules"]["base_repo"]
        base_branch = self.config["settings"]["cursorrules"]["base_branch"]
        base_file = self.config["settings"]["cursorrules"]["base_file"]
        
        # This part would normally fetch from GitHub, but for now, we'll use a placeholder
        # In a real implementation, you'd use git/GitHub API to fetch the base file
        base_content = "# Base CursorRules\n\n[Base content would be fetched from GitHub]\n\n"
        
        # Get custom rules
        custom_rules = self.get_custom_rules()
        custom_content = "# Custom Rules\n\n"
        
        for rule in custom_rules:
            custom_content += f"## {rule['name']}\n\n"
            custom_content += rule['content'] + "\n\n"
        
        # Combine the content
        combined_content = base_content + "\n\n" + custom_content
        
        # Write to the output file
        with open(output_path, 'w') as f:
            f.write(combined_content)
        
        return output_path


# Helper function to get an instance of the manager
def get_archives_manager() -> ArchivesManager:
    """
    Get an instance of the ArchivesManager.
    
    Returns:
        ArchivesManager instance
    """
    return ArchivesManager()


if __name__ == "__main__":
    # Example usage
    manager = get_archives_manager()
    print(f"Repository root: {manager.repo_root}")
    print(f"Archives directory: {manager.archives_dir}") 