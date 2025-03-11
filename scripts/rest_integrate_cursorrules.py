#!/usr/bin/env python3
"""
Integrate AI Archives with Devin.cursorrules using REST API

This script handles the integration of the AI archives with the Devin.cursorrules system,
fetching updates from the source repository and merging with custom rules.
It uses the REST API through ai_archives.py instead of direct file operations.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Get the repository root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)

def check_server_status():
    """Check if the server is running, start it if not using the wrapper script"""
    try:
        wrapper_script = os.path.join(repo_root, "run_archives.sh")
        
        # Check if server is running using the wrapper script
        result = subprocess.run(
            [wrapper_script, "server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # The wrapper script will start the server if it's not running
        print(result.stdout)
        
        return True
    except Exception as e:
        print(f"Error checking server status: {e}")
        return False

def generate_cursorrules(output_path=None):
    """Generate the combined cursorrules file using the wrapper script"""
    wrapper_script = os.path.join(repo_root, "run_archives.sh")
    
    cmd = [wrapper_script, "generate"]
    if output_path:
        cmd.append(output_path)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error generating cursorrules: {e}")
        print(e.stdout)
        print(e.stderr)
        return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Integrate AI Archives with Devin.cursorrules using REST API")
    
    parser.add_argument("--output", "-o", help="Path to write the combined cursorrules file")
    parser.add_argument("--skip-server", "-s", action="store_true", help="Skip server status check")
    
    args = parser.parse_args()
    
    # Check server status unless skipped
    if not args.skip_server:
        check_server_status()
    
    # Generate cursorrules
    return generate_cursorrules(args.output)

if __name__ == "__main__":
    sys.exit(main()) 