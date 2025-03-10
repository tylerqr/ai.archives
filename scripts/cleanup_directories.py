#!/usr/bin/env python3
"""
Cleanup Script for AI Archives Directory Structure

This script helps users migrate from the old approach (symlinks to both repos)
to the new recommended approach (symlink only to the data repo).
"""

import os
import sys
import argparse
import shutil
from pathlib import Path

def cleanup_project_directory(project_path):
    """
    Clean up a project directory by removing symlinks to the main AI archives repo
    and leaving only symlinks to the data repo.
    
    Args:
        project_path: Path to the project directory
    
    Returns:
        True if successful, False otherwise
    """
    print(f"Cleaning up project directory: {project_path}")
    
    # Check if the project directory exists
    if not os.path.exists(project_path):
        print(f"Error: Project directory does not exist: {project_path}")
        return False
    
    # Look for ai.archives symlink
    ai_archives_symlink = os.path.join(project_path, "ai.archives")
    if os.path.exists(ai_archives_symlink) and os.path.islink(ai_archives_symlink):
        print(f"Removing symlink to main AI archives repo: {ai_archives_symlink}")
        try:
            os.unlink(ai_archives_symlink)
            print("✓ Symlink removed successfully")
        except OSError as e:
            print(f"Error removing symlink: {str(e)}")
            return False
    else:
        print("No symlink to main AI archives repo found")
    
    # Check for data repo symlink (we want to keep this one)
    data_repo_symlinks = [f for f in os.listdir(project_path) 
                         if f.startswith("ai.archives.") and 
                         os.path.islink(os.path.join(project_path, f))]
    
    if data_repo_symlinks:
        print(f"Found data repo symlinks (keeping these): {data_repo_symlinks}")
    else:
        print("No data repo symlinks found")
    
    print(f"Project directory cleanup completed: {project_path}")
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Clean up AI Archives directory structure")
    parser.add_argument("--project", "-p", required=True, help="Path to the project directory to clean up")
    
    args = parser.parse_args()
    
    success = cleanup_project_directory(args.project)
    
    if success:
        print("\nDirectory cleanup completed successfully.")
        print("\nRecommended next steps:")
        print("1. Regenerate the .cursorrules file:")
        print("   python scripts/integrate_cursorrules.py")
        print("2. Copy the updated .cursorrules file to your project:")
        print(f"   cp <data_repo_path>/.cursorrules {args.project}/")
    else:
        print("\nDirectory cleanup failed.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 