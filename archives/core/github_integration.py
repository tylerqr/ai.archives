#!/usr/bin/env python3
"""
GitHub Integration for AI Archives

This module handles GitHub operations such as fetching the base cursorrules file,
pushing updates to the archives, and other GitHub-related functionality.
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any, List
from base64 import b64decode
from urllib.parse import urljoin


class GitHubIntegration:
    """
    Class for handling GitHub integration with the AI Archives system.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub integration with an optional token.
        
        Args:
            token: GitHub API token. If None, tries to get from environment.
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            print("Warning: No GitHub token provided. Some features may be limited.")
        
        self.api_base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def fetch_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """
        Fetch file content from a GitHub repository.
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            path: Path to the file in the repository
            ref: Branch, tag, or commit SHA
            
        Returns:
            File content as string, or None if not found
        """
        url = f"{self.api_base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching file: {response.status_code} {response.reason}")
            print(response.text)
            return None
        
        data = response.json()
        if "content" in data:
            # Content is base64 encoded
            return b64decode(data["content"]).decode('utf-8')
        
        return None
    
    def fetch_base_cursorrules(self, repo: str, branch: str, file_path: str) -> Optional[str]:
        """
        Fetch the base cursorrules file from the specified repository.
        
        Args:
            repo: Repository name in format "owner/repo"
            branch: Branch name
            file_path: Path to the cursorrules file
            
        Returns:
            Content of the cursorrules file, or None if not found
        """
        owner, repo_name = repo.split('/')
        return self.fetch_file_content(owner, repo_name, file_path, branch)
    
    def create_or_update_file(self, owner: str, repo: str, path: str, 
                             content: str, message: str, branch: str = "main",
                             sha: Optional[str] = None) -> Dict[str, Any]:
        """
        Create or update a file in a GitHub repository.
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            path: Path to the file in the repository
            content: New content for the file
            message: Commit message
            branch: Branch name
            sha: SHA of the file (required for updating existing files)
            
        Returns:
            Response data from GitHub API
        """
        if not self.token:
            raise ValueError("GitHub token is required for this operation")
        
        url = f"{self.api_base_url}/repos/{owner}/{repo}/contents/{path}"
        
        # If we don't have the SHA but need to update, fetch it first
        if not sha and self.file_exists(owner, repo, path, branch):
            file_data = self.get_file_data(owner, repo, path, branch)
            if file_data:
                sha = file_data.get("sha")
        
        # Prepare request data
        data = {
            "message": message,
            "content": content.encode('utf-8').hex(),
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
        
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code not in (200, 201):
            print(f"Error creating/updating file: {response.status_code} {response.reason}")
            print(response.text)
            return {}
        
        return response.json()
    
    def file_exists(self, owner: str, repo: str, path: str, ref: str = "main") -> bool:
        """
        Check if a file exists in a GitHub repository.
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            path: Path to the file in the repository
            ref: Branch, tag, or commit SHA
            
        Returns:
            True if the file exists, False otherwise
        """
        url = f"{self.api_base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        return response.status_code == 200
    
    def get_file_data(self, owner: str, repo: str, path: str, ref: str = "main") -> Dict[str, Any]:
        """
        Get metadata about a file in a GitHub repository.
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            path: Path to the file in the repository
            ref: Branch, tag, or commit SHA
            
        Returns:
            File metadata as a dictionary
        """
        url = f"{self.api_base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            return {}
        
        return response.json()
    
    def create_pull_request(self, owner: str, repo: str, title: str, body: str,
                           head: str, base: str = "main") -> Dict[str, Any]:
        """
        Create a pull request in a GitHub repository.
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            title: PR title
            body: PR description
            head: Name of the branch where changes are implemented
            base: Name of the branch where changes should be pulled into
            
        Returns:
            Response data from GitHub API
        """
        if not self.token:
            raise ValueError("GitHub token is required for this operation")
        
        url = f"{self.api_base_url}/repos/{owner}/{repo}/pulls"
        
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code != 201:
            print(f"Error creating pull request: {response.status_code} {response.reason}")
            print(response.text)
            return {}
        
        return response.json()


# Helper function to get an instance of the GitHub integration
def get_github_integration(token: Optional[str] = None) -> GitHubIntegration:
    """
    Get an instance of the GitHubIntegration.
    
    Args:
        token: Optional GitHub API token
        
    Returns:
        GitHubIntegration instance
    """
    return GitHubIntegration(token)


if __name__ == "__main__":
    # Example usage
    token = os.environ.get('GITHUB_TOKEN')
    github = get_github_integration(token)
    
    # Example: fetch the cursorrules file from the devin.cursorrules repo
    content = github.fetch_base_cursorrules(
        repo="grapeot/devin.cursorrules",
        branch="multi-agent",
        file_path=".cursorrules"
    )
    
    if content:
        print("Successfully fetched cursorrules file")
        print(f"Length: {len(content)} characters")
    else:
        print("Failed to fetch cursorrules file") 