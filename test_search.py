#!/usr/bin/env python3
"""
Test script to verify search functionality with the new directory structure.
"""

import os
import sys
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
    """Test search functionality"""
    print("Testing search functionality with new structure...")
    
    # Get archives manager
    manager = get_archives_manager()
    
    # Print paths for debugging
    print(f"Repository root: {manager.repo_root}")
    print(f"Data path: {manager.data_path}")
    print(f"Projects directory: {manager.projects_dir}")
    print(f"Data archives directory: {manager.data_archives_dir}")
    
    # Test search
    query = "setup"
    print(f"\nSearching for: {query}")
    results = manager.search_archives(query)
    
    if results:
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title', 'Untitled')} (Project: {result.get('project', 'unknown')}, Section: {result.get('section', 'unknown')})")
            if 'score' in result:
                print(f"   Score: {result['score']}, Matched Tokens: {result.get('matched_tokens', 0)}")
            print(f"   File: {os.path.basename(result.get('file', 'unknown'))}")
            snippet = result.get('snippet', '')
            if snippet:
                print(f"   Snippet: {snippet[:100]}...")
    else:
        print("No results found.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 