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
# Regex for tokenization (alphanumeric and underscores)
TOKEN_PATTERN = re.compile(r'\w+')

def tokenize(text: str) -> List[str]:
    """
    Convert text into tokens by splitting on non-alphanumeric characters.
    
    Args:
        text: The text to tokenize
        
    Returns:
        List of tokens (lowercase)
    """
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]

def score_document(query_tokens: List[str], content: str) -> Tuple[int, List[int]]:
    """
    Score a document based on token matches.
    
    Args:
        query_tokens: List of tokens from the search query
        content: Document content to score
        
    Returns:
        Tuple of (score, list of match positions)
    """
    content_lower = content.lower()
    score = 0
    positions = []
    
    for token in query_tokens:
        # Check for exact token matches
        idx = 0
        while idx < len(content_lower):
            idx = content_lower.find(token, idx)
            if idx == -1:
                break
                
            # Verify it's a complete word (not part of another word)
            # Check before the token
            before_ok = idx == 0 or not content_lower[idx-1].isalnum()
            # Check after the token
            after_ok = idx + len(token) >= len(content_lower) or not content_lower[idx + len(token)].isalnum()
            
            if before_ok and after_ok:
                score += 1
                positions.append(idx)
                
            idx += 1
    
    return score, positions

def sanitize_content(content):
    """
    Sanitize and format content for the archives.
    
    This function:
    1. Removes ANSI color codes and error messages
    2. Handles escaped newlines and other escaped characters
    3. Formats the content for readability
    4. Fixes common issues with code examples
    
    Args:
        content: The content to sanitize
        
    Returns:
        Sanitized and formatted content
    """
    # First, process any escaped characters (convert them to their actual representation)
    # This fixes issues like "\n" appearing in the text instead of actual newlines
    try:
        # Try to detect if content has escaped characters (like \n) that need to be converted
        if '\\n' in content or '\\t' in content or '\\r' in content:
            # Use a safe eval approach to handle the string with escaped characters
            import ast
            content = ast.literal_eval(f'"""{content}"""')
    except (SyntaxError, ValueError):
        # If evaluation fails, keep the original content
        pass
    
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
    
    # Fix markdown formatting issues
    # Ensure proper spacing after headers
    sanitized = re.sub(r'(#+)([^#\s])', r'\1 \2', sanitized)
    
    # Fix lists without spaces after bullet points
    sanitized = re.sub(r'(\n\s*[-*])([^\s])', r'\1 \2', sanitized)
    
    # Ensure code blocks have newlines before and after them
    sanitized = re.sub(r'([^\n])```', r'\1\n```', sanitized)
    sanitized = re.sub(r'```([^\n])', r'```\n\1', sanitized)
    
    # Remove duplicate headers (sometimes an AI might repeat the title)
    lines = sanitized.split('\n')
    if len(lines) > 2 and lines[0].startswith('# ') and lines[-1].strip() == lines[0].strip():
        sanitized = '\n'.join(lines[:-1])
    
    return sanitized

class ArchivesManager:
    """
    Main class for managing the AI Archives system.
    """
    
    def __init__(self, data_path=None, github_token=None):
        """
        Initialize the ArchivesManager with the given data path.
        
        Args:
            data_path: Path to the data directory. If None, tries to find from config
            github_token: GitHub API token for integration features
        """
        # Get the repo root (where the project was installed)
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load config if it exists
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {'settings': DEFAULT_CONFIG}
        
        self.token = github_token or os.environ.get('GITHUB_TOKEN')
        
        # Setup data path
        if data_path:
            self.data_path = os.path.abspath(data_path)
        else:
            # Use config value if available
            self.data_path = self.config.get('settings', {}).get('data_directory', None)
            
            # If not set in config, use current directory
            if not self.data_path:
                self.data_path = os.path.dirname(self.repo_root)
        
        # Setup paths for archives
        self.archives_dir = os.path.join(self.repo_root, 'archives')
        
        # For backward compatibility, support both paths
        self.api_dir = self.repo_root
        
        # Setup paths for data repository - simplified structure
        # Projects are directly under the archives directory
        self.data_archives_dir = os.path.join(self.data_path, 'archives')
        
        # Create directories if they don't exist
        self._ensure_directories_exist()
        
    def _ensure_directories_exist(self):
        """Create required directories if they don't exist."""
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.data_archives_dir, exist_ok=True)
        
    def get_appropriate_archive_file(self, project: str, section: str) -> Tuple[str, bool]:
        """
        Get the appropriate archive file for a given project and section.
        Creates new files as needed.
        
        Args:
            project: Project name (e.g., 'frontend', 'backend', 'shared')
            section: Section name (e.g., 'setup', 'errors', 'fixes')
            
        Returns:
            Tuple of (file_path, is_new_file)
        """
        # Validate project and section
        valid_projects = self.config["settings"]["archive_structure"]["projects"]
        valid_sections = self.config["settings"]["archive_structure"]["sections"]
        
        if project not in valid_projects:
            print(f"Warning: Project '{project}' is not in the configured projects list: {valid_projects}")
            print(f"Creating directory for new project: {project}")
        
        if section not in valid_sections:
            print(f"Warning: Section '{section}' is not in the configured sections list: {valid_sections}")
            print(f"Creating directory for new section: {section}")
        
        # Create directories if they don't exist
        project_dir = os.path.join(self.data_archives_dir, project)
        os.makedirs(project_dir, exist_ok=True)
        
        section_dir = os.path.join(project_dir, section)
        os.makedirs(section_dir, exist_ok=True)
        
        # Try to find an existing file with content
        existing_files = glob.glob(os.path.join(section_dir, "*.md"))
        
        if existing_files:
            # Use the most recently modified file
            existing_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            return existing_files[0], False
        
        # Create a new file if none exists
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_file = os.path.join(section_dir, f"{project}_{section}_{timestamp}.md")
        
        # Create the file
        with open(new_file, 'w') as f:
            f.write("")
        
        return new_file, True
    
    def add_to_archives(self, project: str, section: str, content: str, title: Optional[str] = None) -> str:
        """
        Add content to the archives.
        
        Args:
            project: Project name (e.g., 'frontend', 'backend', 'shared')
            section: Section name (e.g., 'setup', 'errors', 'fixes')
            content: Content to add. Should be properly formatted markdown text.
                     - Use actual newlines, not escaped newlines (\\n)
                     - Use proper markdown headers (# Title, ## Subtitle)
                     - Use proper bullet points with spacing (- Item, * Item)
                     - Format code using markdown code blocks (```language...```)
            title: Optional title for the content. If not provided, a title will be 
                   generated based on project and section names.
            
        Returns:
            Path to the updated archive file
        """
        # Get the appropriate archive file
        archive_file, is_new_file = self.get_appropriate_archive_file(project, section)
        
        # Sanitize content
        sanitized_content = sanitize_content(content)
        
        # Format the content
        if is_new_file:
            if title:
                formatted_content = f"# {title}\n\n{sanitized_content}"
            else:
                title = f"{project.capitalize()} {section.capitalize()}"
                formatted_content = f"# {title}\n\n{sanitized_content}"
        else:
            # Read existing content
            with open(archive_file, 'r') as f:
                existing_content = f.read()
            
            # Add new content with a divider
            if title:
                formatted_content = f"{existing_content}\n\n---\n\n## {title}\n\n{sanitized_content}"
            else:
                formatted_content = f"{existing_content}\n\n---\n\n{sanitized_content}"
        
        # Write to the file
        with open(archive_file, 'w') as f:
            f.write(formatted_content)
        
        return archive_file
    
    def search_archives(self, query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the archives for a query.
        
        Args:
            query: Search query
            project: Optional project to limit the search to
            
        Returns:
            List of matching entries
        """
        results = []
        
        # First check if the exact query string matches (for backward compatibility)
        exact_results = self._exact_match_search(query, project)
        if exact_results:
            return exact_results
        
        # If no exact matches, try tokenized search
        query_tokens = tokenize(query)
        
        # Skip tokenized search if there are no valid tokens
        if not query_tokens:
            return []
            
        # Determine which projects to search
        if project:
            projects = [project]
        else:
            projects = self.config["settings"]["archive_structure"]["projects"]
        
        # Search each project
        for proj in projects:
            project_dir = os.path.join(self.data_archives_dir, proj)
            
            if not os.path.exists(project_dir):
                continue
            
            # Search all sections
            for section_dir in glob.glob(os.path.join(project_dir, "*")):
                if not os.path.isdir(section_dir):
                    continue
                
                section = os.path.basename(section_dir)
                
                # Search all files in the section
                for file_path in glob.glob(os.path.join(section_dir, "*.md")):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Score document based on token matches
                    score, positions = score_document(query_tokens, content)
                    
                    if score > 0:
                        # Extract the best snippet (we'll use the first match position)
                        if positions:
                            match_pos = positions[0]
                            start = max(0, match_pos - 100)
                            end = min(len(content), match_pos + 200)
                            snippet = content[start:end]
                        else:
                            # Fallback to beginning of document
                            snippet = content[:300]
                        
                        # Extract title from first line or filename
                        first_line = content.split('\n', 1)[0]
                        title = first_line.lstrip('#').strip() if first_line.startswith('#') else os.path.basename(file_path)
                        
                        results.append({
                            'project': proj,
                            'section': section,
                            'file': file_path,
                            'title': title,
                            'snippet': snippet,
                            'score': score,
                            'matched_tokens': len(set(token for token in query_tokens if token.lower() in content.lower()))
                        })
        
        # Sort results by score (highest first)
        results.sort(key=lambda x: (x['score'], x['matched_tokens']), reverse=True)
        return results
    
    def _exact_match_search(self, query: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform an exact string match search (original implementation).
        
        Args:
            query: Search query
            project: Optional project to limit the search to
            
        Returns:
            List of matching entries
        """
        results = []
        
        # Determine which projects to search
        if project:
            projects = [project]
        else:
            projects = self.config["settings"]["archive_structure"]["projects"]
        
        # Search each project
        for proj in projects:
            project_dir = os.path.join(self.data_archives_dir, proj)
            
            if not os.path.exists(project_dir):
                continue
            
            # Search all sections
            for section_dir in glob.glob(os.path.join(project_dir, "*")):
                if not os.path.isdir(section_dir):
                    continue
                
                section = os.path.basename(section_dir)
                
                # Search all files in the section
                for file_path in glob.glob(os.path.join(section_dir, "*.md")):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Simple search for exact match
                    if query.lower() in content.lower():
                        # Extract a snippet around the query
                        lower_content = content.lower()
                        query_pos = lower_content.find(query.lower())
                        start = max(0, query_pos - 100)
                        end = min(len(content), query_pos + len(query) + 100)
                        snippet = content[start:end]
                        
                        # Extract title from first line or filename
                        first_line = content.split('\n', 1)[0]
                        title = first_line.lstrip('#').strip() if first_line.startswith('#') else os.path.basename(file_path)
                        
                        results.append({
                            'project': proj,
                            'section': section,
                            'file': file_path,
                            'title': title,
                            'snippet': snippet
                        })
        
        return results
    
    def update_custom_rules(self, rule_content: str, rule_name: str) -> str:
        """
        Update or create a custom rule.
        
        Args:
            rule_content: Content of the rule
            rule_name: Name of the rule
            
        Returns:
            Path to the rule file
        """
        # Ensure rule name ends with .md
        if not rule_name.endswith('.md'):
            rule_name = f"{rule_name}.md"
        
        # Save to root directory
        rule_file = os.path.join(self.repo_root, rule_name)
        
        with open(rule_file, 'w') as f:
            f.write(rule_content)
        
        return rule_file
    
    def get_custom_rules(self) -> List[Dict[str, str]]:
        """
        Get all custom rules from the archives.
        
        Returns:
            List of dictionaries with 'name', 'file', and 'content' for each rule
        """
        rules = []
        rules_by_name = {}  # Track rules by name to handle duplicates
        
        # Priority 1: Check for custom rules in the repo root directory (highest priority)
        repo_root_custom_rules = os.path.join(self.repo_root, "*.md")
        for rule_file in glob.glob(repo_root_custom_rules):
            rule_name = os.path.splitext(os.path.basename(rule_file))[0]
            
            # Only consider .md files that are likely to be custom rules
            if rule_name.lower() in ['custom-rules', 'ai_archives_integration', 'archives_integration', 'explicit_permission']:
                with open(rule_file, 'r') as f:
                    content = f.read()
                
                rules_by_name[rule_name] = {
                    'name': rule_name,
                    'file': rule_file,
                    'content': content
                }
        
        # Priority 2: Check in data_path for custom rules (for backward compatibility)
        data_path_custom_rules = os.path.join(self.data_path, "*.md")
        for rule_file in glob.glob(data_path_custom_rules):
            rule_name = os.path.splitext(os.path.basename(rule_file))[0]
            
            # Skip if we already have this rule from repo root
            if rule_name in rules_by_name:
                continue
                
            with open(rule_file, 'r') as f:
                content = f.read()
            
            rules_by_name[rule_name] = {
                'name': rule_name,
                'file': rule_file,
                'content': content
            }
        
        # Priority 3: Check for custom rules in previous locations (backwards compatibility)
        # Legacy locations to check in order from highest to lowest priority:
        legacy_locations = [
            os.path.join(self.data_path, 'custom_rules'),  # Old data path location
            os.path.join(self.archives_dir, 'custom_rules')  # Old archives location
        ]
        
        for legacy_dir in legacy_locations:
            if os.path.exists(legacy_dir):
                for rule_file in glob.glob(os.path.join(legacy_dir, "*.md")):
                    rule_name = os.path.splitext(os.path.basename(rule_file))[0]
                    
                    # Skip if we already have this rule from another source
                    if rule_name in rules_by_name:
                        continue
                    
                    with open(rule_file, 'r') as f:
                        content = f.read()
                    
                    rules_by_name[rule_name] = {
                        'name': rule_name,
                        'file': rule_file,
                        'content': content
                    }
        
        # Convert dictionary to list
        return list(rules_by_name.values())
    
    def generate_combined_cursorrules(self, output_path: Optional[str] = None) -> str:
        """
        Generate a combined .cursorrules file with custom rules.
        
        Args:
            output_path: Optional path to write the file to. If None, uses the repository root.
            
        Returns:
            Path to the generated file
        """
        from .github_integration import get_github_integration
        
        # Get GitHub integration
        github = get_github_integration()
        
        # Fetch base cursorrules file
        base_repo = self.config["settings"]["cursorrules"]["base_repo"]
        base_branch = self.config["settings"]["cursorrules"]["base_branch"]
        base_file = self.config["settings"]["cursorrules"]["base_file"]
        
        print(f"Fetching base cursorrules from {base_repo}:{base_branch}/{base_file}...")
        
        base_content = github.fetch_base_cursorrules(
            repo=base_repo,
            branch=base_branch,
            file_path=base_file
        )
        
        if not base_content:
            print("Failed to fetch base cursorrules file. Using local template.")
            base_content = self._get_local_cursorrules_template()
        
        print(f"Successfully fetched base cursorrules ({len(base_content)} characters)")
        
        # Get custom rules
        custom_rules = self.get_custom_rules()
        
        # Merge with custom rules
        print(f"Merging with {len(custom_rules)} custom rules...")
        
        if custom_rules:
            # Create custom rules section
            combined_content = "\n\n# AI Archives - Custom Rules\n\n"
            
            # Find AI Archives integration rules first
            archives_rule = None
            other_rules = []
            
            for rule in custom_rules:
                rule_name_lower = rule['name'].lower()
                if rule_name_lower in ['ai_archives_integration', 'archives_integration', 'custom-rules']:
                    archives_rule = rule
                else:
                    other_rules.append(rule)
            
            # Add AI Archives integration rules first
            if archives_rule:
                combined_content += f"## {archives_rule['name']}\n\n"
                combined_content += archives_rule['content'] + "\n\n"
            
            # Add other rules
            for rule in other_rules:
                combined_content += f"## {rule['name']}\n\n"
                combined_content += rule['content'] + "\n\n"
            
            # Combine with base content
            if "# AI Archives - Custom Rules" not in base_content:
                merged_content = base_content + combined_content
            else:
                parts = base_content.split("# AI Archives - Custom Rules")
                merged_content = parts[0] + "# AI Archives - Custom Rules" + combined_content
        else:
            merged_content = base_content
        
        # Determine output path
        if not output_path:
            output_path = os.path.join(self.repo_root, '.cursorrules')
        
        # Write to file
        print(f"Writing combined cursorrules to {output_path}...")
        
        with open(output_path, 'w') as f:
            f.write(merged_content)
        
        print(f"Successfully wrote combined cursorrules file ({len(merged_content)} characters)")
        
        return output_path
    
    def _get_local_cursorrules_template(self) -> str:
        """
        Get a local template for the cursorrules file.
        
        Returns:
            Template content
        """
        return """
# Instructions

You are a powerful AI assistant working in Cursor. This is a .cursorrules file that defines your behavior when interacting with the user.

## Guidelines

* Always be helpful, accurate, and safe.
* Avoid making things up or providing false information.
* When writing code, ensure it's correct, readable, and efficient.
* Always run code to verify it works before returning it to the user.
"""


def get_archives_manager(repo_root: str = None, data_repo_root: str = None, data_path: str = None) -> ArchivesManager:
    """
    Get an instance of the ArchivesManager.
    This is the main entry point for using the archives system.
    
    Args:
        repo_root: Path to the repository root
        data_repo_root: Path to the data repository root (for backward compatibility)
        data_path: Path to the data directory
        
    Returns:
        An instance of ArchivesManager
    """
    # Handle data_repo_root parameter (for backward compatibility)
    if data_repo_root is not None and data_path is None:
        data_path = data_repo_root
    
    return ArchivesManager(data_path=data_path)

# Create a compatibility module to allow importing from archives.core.archives_manager
# This will be removed in a future version
import sys
import os

# Add a hook to handle imports from the old location
class ArchivesCoreCompatModule:
    def __init__(self):
        self.archives_manager = sys.modules[__name__]
        
    def __getattr__(self, name):
        return getattr(self.archives_manager, name)

# Create the module and add it to sys.modules for backward compatibility
sys.modules['archives.core.archives_manager'] = ArchivesCoreCompatModule()
sys.modules['archives.core'] = ArchivesCoreCompatModule()


if __name__ == "__main__":
    # Example usage
    manager = get_archives_manager()
    print(f"Repository root: {manager.repo_root}")
    print(f"Archives directory: {manager.archives_dir}") 