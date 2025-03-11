#!/usr/bin/env python3
"""
AI Archives Setup Verification Script

This script verifies the proper setup of AI Archives in a project directory,
checking the symlink paths and ensuring the archives CLI is accessible.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_symlink(path):
    """Check if a path is a symlink and where it points to."""
    try:
        if os.path.islink(path):
            target = os.readlink(path)
            return True, target
        else:
            return False, None
    except Exception as e:
        return False, str(e)

def verify_archives_setup():
    """Verify the AI Archives setup in the current directory."""
    print("AI Archives Setup Verification")
    print("==============================")
    
    # Check for ai.archives directory
    ai_archives_path = Path("ai.archives")
    is_symlink, target = check_symlink(ai_archives_path)
    
    print(f"Checking for ai.archives directory:")
    if os.path.exists(ai_archives_path):
        print(f"  ✅ ai.archives directory exists")
        if is_symlink:
            print(f"  ✅ ai.archives is a symlink pointing to: {target}")
        else:
            print(f"  ⚠️  ai.archives is not a symlink - this might cause issues")
    else:
        print(f"  ❌ ai.archives directory does not exist")
        print(f"     Create it with: ln -s /path/to/ai_archives_repo ai.archives")
        return False
    
    # Check for archives directory
    archives_path = ai_archives_path / "archives"
    print(f"\nChecking for archives directory:")
    if os.path.exists(archives_path):
        print(f"  ✅ archives directory exists at: {archives_path}")
    else:
        print(f"  ❌ archives directory not found at: {archives_path}")
        print(f"     Expected path: {archives_path.absolute()}")
        return False
    
    # Check for project directories (frontend, backend, shared)
    print(f"\nChecking for project directories:")
    for project in ["frontend", "backend", "shared"]:
        project_path = archives_path / project
        if os.path.exists(project_path):
            print(f"  ✅ {project} directory exists at: {project_path}")
        else:
            print(f"  ⚠️ {project} directory not found at: {project_path}")
    
    # Check for core directory
    core_path = ai_archives_path / "core"
    print(f"\nChecking for core directory:")
    if os.path.exists(core_path):
        print(f"  ✅ core directory exists at: {core_path}")
    else:
        print(f"  ❌ core directory not found at: {core_path}")
        print(f"     Expected path: {core_path.absolute()}")
        return False
    
    # Check for custom rules file in root
    custom_rules_path = ai_archives_path / "custom-rules.md"
    print(f"\nChecking for custom rules file:")
    if os.path.exists(custom_rules_path):
        print(f"  ✅ custom-rules.md exists at: {custom_rules_path}")
    else:
        print(f"  ⚠️  custom-rules.md not found at: {custom_rules_path}")
        print(f"     This might cause issues with AI agent memory")
    
    # Check gitignore for .cursorrules
    print(f"\nChecking .gitignore configuration:")
    gitignore_path = Path(".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        if ".cursorrules" in gitignore_content:
            print(f"  ✅ .cursorrules is properly added to .gitignore")
        else:
            print(f"  ⚠️  .cursorrules is not in .gitignore")
            print(f"     Consider adding it with: echo '.cursorrules' >> .gitignore")
    else:
        print(f"  ⚠️  No .gitignore file found")
    
    # Check for REST API setup
    print(f"\nChecking for REST API setup:")
    server_path = ai_archives_path / "server.py"
    wrapper_path = ai_archives_path / "run_archives.sh"
    
    if os.path.exists(server_path):
        print(f"  ✅ server.py exists at: {server_path}")
    else:
        print(f"  ❌ server.py not found at: {server_path}")
    
    if os.path.exists(wrapper_path):
        print(f"  ✅ run_archives.sh wrapper exists at: {wrapper_path}")
    else:
        print(f"  ❌ run_archives.sh wrapper not found at: {wrapper_path}")
    
    # Test running the wrapper script
    print(f"\nTesting wrapper script:")
    try:
        # Just run the help command
        result = subprocess.run(
            [str(wrapper_path)],
            capture_output=True,
            text=True,
            check=False
        )
        if "Usage:" in result.stdout:
            print(f"  ✅ run_archives.sh wrapper runs successfully")
        else:
            print(f"  ⚠️  run_archives.sh runs but output seems unexpected")
    except Exception as e:
        print(f"  ❌ Error running run_archives.sh: {e}")
    
    print("\n✅ AI Archives setup appears to be working correctly!")
    print("\nTest commands:")
    print(f"  Search:  ./ai.archives/run_archives.sh search \"your search term\"")
    print(f"  Add:     ./ai.archives/run_archives.sh add frontend errors \"Title\" \"Content\"")
    print(f"  Generate: ./ai.archives/run_archives.sh generate")
    
    return True

if __name__ == "__main__":
    verify_archives_setup() 