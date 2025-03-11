#!/usr/bin/env python3
"""
AI Archives API Module

This module provides a simple API for integrating the AI Archives with other projects.
It handles the common operations like searching, adding to archives, etc.
"""

import os
import sys
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Try to import from core directly
try:
    from core.archives_manager import get_archives_manager
    from core.github_integration import get_github_integration
except ImportError:
    # Fall back to old import path for backward compatibility
    from archives.core.archives_manager import get_archives_manager
    from archives.core.github_integration import get_github_integration


class ArchivesAPI:
    """
    API class for interacting with the AI Archives system.
    """
    
    def __init__(self, repo_root: Optional[str] = None, github_token: Optional[str] = None):
        """
        Initialize the ArchivesAPI with repository root and GitHub token.
        
        Args:
            repo_root: Path to the repository root. If None, tries to determine automatically.
            github_token: GitHub API token. If None, tries to get from environment.
        """
        self.manager = get_archives_manager(repo_root)
        self.github = get_github_integration(github_token)
    
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
        return self.manager.add_to_archives(project, section, content, title)
    
    def search_archives(self, query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the archives for a specific query.
        
        Args:
            query: The search query
            project: Optional project to limit the search to
            
        Returns:
            List of matching entries with file path and snippet
        """
        return self.manager.search_archives(query, project)
    
    def update_custom_rule(self, rule_content: str, rule_name: str) -> str:
        """
        Add or update a custom rule.
        
        Args:
            rule_content: The content of the rule
            rule_name: The name of the rule file (without extension)
            
        Returns:
            Path to the rule file
        """
        return self.manager.update_custom_rules(rule_content, rule_name)
    
    def get_custom_rules(self) -> List[Dict[str, str]]:
        """
        Get all custom rules.
        
        Returns:
            List of rule dictionaries with name and content
        """
        return self.manager.get_custom_rules()
    
    def generate_combined_cursorrules(self, output_path: Optional[str] = None) -> str:
        """
        Generate a combined cursorrules file from the base file and custom rules.
        
        Args:
            output_path: Optional path for the output file. If None, uses .cursorrules in repo root.
            
        Returns:
            Path to the generated file
        """
        # Fetch base cursorrules content
        config = self.manager.config
        base_repo = config["settings"]["cursorrules"]["base_repo"]
        base_branch = config["settings"]["cursorrules"]["base_branch"]
        base_file = config["settings"]["cursorrules"]["base_file"]
        
        base_content = self.github.fetch_base_cursorrules(
            repo=base_repo,
            branch=base_branch,
            file_path=base_file
        )
        
        if not base_content:
            raise Exception("Failed to fetch base cursorrules file")
        
        # Get custom rules - ONLY from custom-rules.md
        custom_rules_path = os.path.join(self.manager.repo_root, 'custom-rules.md')
        if os.path.exists(custom_rules_path):
            with open(custom_rules_path, 'r') as f:
                custom_rules_content = f.read()
        else:
            custom_rules_content = ""
        
        # Start with the custom rules section
        merged_content = "# AI Archives - Custom Rules\n\n"
        
        # Add custom rules content directly
        merged_content += custom_rules_content + "\n\n"
        
        # Add a note about the scratchpad.md file
        merged_content += "# IMPORTANT: AI Scratchpad Location\n\n"
        merged_content += "When working with this project, all planning, progress tracking, and lessons learned should be written to:\n\n"
        merged_content += "```\n./ai.archives/scratchpad.md\n```\n\n"
        merged_content += "DO NOT modify this .cursorrules file directly. Instead, use the scratchpad.md file for all dynamic content.\n\n"
        
        # Add separator between custom rules and base content
        merged_content += "# Base CursorRules\n\n"
        
        # Modify base content to use separate files instead of editing .cursorrules
        modified_base_content = base_content
        
        # Replace references to editing .cursorrules with scratchpad.md
        modified_base_content = modified_base_content.replace(
            "the current state of `Multi-Agent Scratchpad` section in the `.cursorrules` file", 
            "the current state of the `scratchpad.md` file in the ai.archives directory"
        )
        
        modified_base_content = modified_base_content.replace(
            "You then need to actually do the changes to the file.", 
            "You then need to actually do the changes to the `scratchpad.md` file."
        )
        
        modified_base_content = modified_base_content.replace(
            "also make incremental writes or modifications to the `Multi-Agent Scratchpad` section in the `.cursorrules` file", 
            "also make incremental writes or modifications to the `scratchpad.md` file"
        )
        
        modified_base_content = modified_base_content.replace(
            "The `Multi-Agent Scratchpad` section in the `.cursorrules` file", 
            "The `scratchpad.md` file"
        )
        
        # Replace references to the Lessons section
        modified_base_content = modified_base_content.replace(
            "you should take note in the `Lessons` section in the `.cursorrules` file", 
            "you should take note in the `Lessons` section of the `scratchpad.md` file in the ai.archives directory"
        )
        
        # Add base content with modifications
        merged_content += modified_base_content
        
        # Set default output path if not provided
        if output_path is None:
            output_path = os.path.join(self.manager.repo_root, '.cursorrules')
        
        # Write combined file
        with open(output_path, 'w') as f:
            f.write(merged_content)
        
        # Create a combined scratchpad.md file if it doesn't exist
        scratchpad_path = os.path.join(self.manager.repo_root, 'scratchpad.md')
        if not os.path.exists(scratchpad_path):
            with open(scratchpad_path, 'w') as f:
                f.write("# Multi-Agent Scratchpad\n\n")
                f.write("## Background and Motivation\n\n")
                f.write("(Planner writes: User/business requirements, macro objectives, why this problem needs to be solved)\n\n")
                f.write("## Key Challenges and Analysis\n\n")
                f.write("(Planner: Records of technical barriers, resource constraints, potential risks)\n\n")
                f.write("## Verifiable Success Criteria\n\n")
                f.write("(Planner: List measurable or verifiable goals to be achieved)\n\n")
                f.write("## High-level Task Breakdown\n\n")
                f.write("(Planner: List subtasks by phase, or break down into modules)\n\n")
                f.write("## Current Status / Progress Tracking\n\n")
                f.write("(Executor: Update completion status after each subtask. If needed, use bullet points or tables to show Done/In progress/Blocked status)\n\n")
                f.write("## Next Steps and Action Items\n\n")
                f.write("(Planner: Specific arrangements for the Executor)\n\n")
                f.write("## Executor's Feedback or Assistance Requests\n\n")
                f.write("(Executor: Write here when encountering blockers, questions, or need for more information during execution)\n\n")
                f.write("# Lessons\n\n")
                f.write("## User Specified Lessons\n\n")
                f.write("- Add lessons here\n\n")
                f.write("## Cursor learned\n\n")
                f.write("- Add lessons here\n")
        
        # Remove the separate lessons.md file if it exists
        lessons_path = os.path.join(self.manager.repo_root, 'lessons.md')
        if os.path.exists(lessons_path):
            try:
                os.remove(lessons_path)
            except:
                pass
        
        return output_path
    
    def copy_cursorrules_to_project(self, target_project_path: str) -> Optional[str]:
        """
        Copy the combined cursorrules file to a target project.
        
        Args:
            target_project_path: Path to the target project
            
        Returns:
            Path to the copied file or None if failed
        """
        # Generate combined cursorrules
        combined_path = self.generate_combined_cursorrules()
        
        if not os.path.exists(target_project_path):
            raise ValueError(f"Target project path does not exist: {target_project_path}")
        
        target_file = os.path.join(target_project_path, '.cursorrules')
        
        # Copy file
        with open(combined_path, 'r') as f:
            content = f.read()
        
        with open(target_file, 'w') as f:
            f.write(content)
        
        return target_file


# Create a single global instance
_api_instance = None

def get_archives_api(repo_root: Optional[str] = None, github_token: Optional[str] = None) -> ArchivesAPI:
    """
    Get the global ArchivesAPI instance.
    
    Args:
        repo_root: Path to the repository root. If None, tries to determine automatically.
        github_token: GitHub API token. If None, tries to get from environment.
        
    Returns:
        ArchivesAPI instance
    """
    global _api_instance
    if _api_instance is None:
        _api_instance = ArchivesAPI(repo_root, github_token)
    return _api_instance


if __name__ == "__main__":
    # Example usage
    api = get_archives_api()
    
    # Add to archives
    file_path = api.add_to_archives(
        project="shared", 
        section="setup", 
        content="Example content for the AI archives system",
        title="Setting up the AI Archives System"
    )
    print(f"Added to archives: {file_path}")
    
    # Search archives
    results = api.search_archives("setup")
    print(f"Found {len(results)} results in archives") 