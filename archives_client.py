#!/usr/bin/env python3
"""
AI Archives Client Library

A simple client library for AI agents to interact with the AI Archives REST API.
This eliminates the need for complex Python environment setup and command-line calls.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Union

class ArchivesClient:
    """Client for the AI Archives REST API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the client with the API base URL
        
        Args:
            base_url: Base URL of the Archives REST API
        """
        self.base_url = base_url.rstrip('/')
    
    def ping(self) -> Dict[str, Any]:
        """Check if the server is running"""
        response = requests.get(f"{self.base_url}/ping")
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, project: Optional[str] = None) -> Dict[str, Any]:
        """
        Search the archives
        
        Args:
            query: Search query
            project: Optional project to search in
            
        Returns:
            Search results as a dictionary
        """
        params = {'query': query}
        if project:
            params['project'] = project
            
        response = requests.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return response.json()
    
    def quick_search(self, query: str, project: Optional[str] = None, format_type: str = "json") -> Union[Dict[str, Any], str]:
        """
        Optimized search for AI agents
        
        Args:
            query: Search query
            project: Optional project to search in
            format_type: Response format ('json' or 'text')
            
        Returns:
            Search results as dictionary or formatted text string
        """
        params = {'query': query, 'format': format_type}
        if project:
            params['project'] = project
            
        response = requests.get(f"{self.base_url}/quick-search", params=params)
        response.raise_for_status()
        
        if format_type == 'text':
            return response.text
        else:
            return response.json()
    
    def add(self, project: str, section: str, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Add content to archives
        
        Args:
            project: Project name (e.g., 'frontend', 'backend', 'shared')
            section: Section name (e.g., 'setup', 'errors', 'fixes')
            content: Content to add as properly formatted markdown text.
                    IMPORTANT FORMATTING GUIDELINES:
                    - Use actual newlines, not escaped newlines (\\n)
                    - Use proper markdown headers (# Title, ## Subtitle)
                    - Use proper bullet points with spacing (- Item, * Item)
                    - Format code using markdown code blocks (```language...```)
                    - Ensure proper spacing between elements
                    - DO NOT send raw strings with escaped characters
            title: Optional entry title
            
        Returns:
            Result as a dictionary
        """
        data = {
            'project': project,
            'section': section,
            'content': content
        }
        
        if title:
            data['title'] = title
            
        response = requests.post(f"{self.base_url}/add", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_rules(self) -> Dict[str, Any]:
        """
        Get all custom rules
        
        Returns:
            Rules as a dictionary
        """
        response = requests.get(f"{self.base_url}/rules")
        response.raise_for_status()
        return response.json()
    
    def add_rule(self, name: str, content: str) -> Dict[str, Any]:
        """
        Add or update a custom rule
        
        Args:
            name: Rule name
            content: Rule content
            
        Returns:
            Result as a dictionary
        """
        data = {'name': name, 'content': content}
        response = requests.post(f"{self.base_url}/rules", json=data)
        response.raise_for_status()
        return response.json()
    
    def generate_cursorrules(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate combined cursorrules file
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Result as a dictionary
        """
        data = {}
        if output_path:
            data['output_path'] = output_path
            
        response = requests.post(f"{self.base_url}/generate-cursorrules", json=data)
        response.raise_for_status()
        return response.json()
    
    def list_projects(self) -> Dict[str, Any]:
        """
        List all available projects
        
        Returns:
            Projects as a dictionary
        """
        response = requests.get(f"{self.base_url}/list-projects")
        response.raise_for_status()
        return response.json()
    
    def list_sections(self, project: str) -> Dict[str, Any]:
        """
        List all sections for a project
        
        Args:
            project: Project name
            
        Returns:
            Sections as a dictionary
        """
        params = {'project': project}
        response = requests.get(f"{self.base_url}/list-sections", params=params)
        response.raise_for_status()
        return response.json()


# Simple usage example
if __name__ == "__main__":
    import sys
    
    # Create client
    client = ArchivesClient()
    
    # Simple demo of functionality
    if len(sys.argv) < 2:
        print("Usage: python archives_client.py <command> [args...]")
        print("\nAvailable commands:")
        print("  search <query> [project]       - Search archives")
        print("  add <project> <section> <content> [title] - Add to archives")
        print("  rules                           - List all rules")
        print("  add-rule <name> <content>       - Add/update a rule")
        print("  generate                        - Generate cursorrules file")
        print("  projects                        - List all projects")
        print("  sections <project>              - List sections for a project")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "search":
            if len(sys.argv) < 3:
                print("Error: Missing query argument")
                sys.exit(1)
                
            query = sys.argv[2]
            project = sys.argv[3] if len(sys.argv) > 3 else None
            
            # Use text format for cleaner output in terminal
            result = client.quick_search(query, project, format_type="text")
            print(result)
            
        elif command == "add":
            if len(sys.argv) < 5:
                print("Error: Missing arguments. Usage: add <project> <section> <content> [title]")
                sys.exit(1)
                
            project = sys.argv[2]
            section = sys.argv[3]
            content = sys.argv[4]
            title = sys.argv[5] if len(sys.argv) > 5 else None
            
            result = client.add(project, section, content, title)
            print(json.dumps(result, indent=2))
            
        elif command == "rules":
            result = client.get_rules()
            print(json.dumps(result, indent=2))
            
        elif command == "add-rule":
            if len(sys.argv) < 4:
                print("Error: Missing arguments. Usage: add-rule <name> <content>")
                sys.exit(1)
                
            name = sys.argv[2]
            content = sys.argv[3]
            
            result = client.add_rule(name, content)
            print(json.dumps(result, indent=2))
            
        elif command == "generate":
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            result = client.generate_cursorrules(output_path)
            print(json.dumps(result, indent=2))
            
        elif command == "projects":
            result = client.list_projects()
            print(json.dumps(result, indent=2))
            
        elif command == "sections":
            if len(sys.argv) < 3:
                print("Error: Missing project argument")
                sys.exit(1)
                
            project = sys.argv[2]
            result = client.list_sections(project)
            print(json.dumps(result, indent=2))
            
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1) 