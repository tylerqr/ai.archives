# AI Archives Integration Guide

This guide explains how to integrate the AI Archives system with your existing projects to enable long-lived memory and knowledge sharing for AI agents.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [Integrating with Frontend Projects](#integrating-with-frontend-projects)
- [Integrating with Backend Projects](#integrating-with-backend-projects)
- [Cross-Project Knowledge Sharing](#cross-project-knowledge-sharing)
- [Custom Rules](#custom-rules)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following:

- Git installed and configured
- Python 3.8 or higher
- Access to the repositories you want to integrate with
- Basic understanding of command-line operations

## Repository Structure

The AI Archives system uses a two-repository structure:

1. **Main Repository** (`ai.archives`): Contains the core system code, scripts, and utilities
2. **Data Repository** (`ai.archives.{your-project-name}`): Stores your project-specific archives, knowledge, and custom rules

This separation keeps the system code clean and allows you to keep your project knowledge private while still benefiting from system updates.

```
ai.archives/               # Main system repository
├── archives/
│   ├── core/              # Core system files and utilities
│   ├── api/               # API documentation
│   └── examples/          # Example configurations and templates
├── scripts/               # Utility scripts for managing the archives
├── INTEGRATION_GUIDE.md   # Detailed integration instructions
└── requirements.txt       # Python dependencies

ai.archives.{project}/    # Your data repository (created separately)
├── archives/
│   ├── projects/          # Project-specific knowledge
│   │   ├── frontend/      # Frontend project knowledge
│   │   ├── backend/       # Backend project knowledge
│   │   └── shared/        # Shared knowledge across projects
│   └── custom_rules/      # Custom cursorrules that survive updates
└── .cursorrules           # Generated custom cursorrules file
```

## Installation

1. Clone the main AI Archives repository:

```bash
git clone https://github.com/tylerqr/ai.archives.git
cd ai.archives
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your data repository:

```bash
# Navigate to a location outside your project directories
cd /path/to/storage/location

# Create a data repository with a custom name (recommended format: ai.archives.{your-project-name})
# For example, if your project is called "myapp":
mkdir ai.archives.myapp
cd ai.archives.myapp
git init
```

This repository will store your project-specific archives. It should be created outside of your existing project directories to avoid cluttering them.

## Basic Setup

The AI Archives system provides a setup script to help you configure both repositories:

```bash
cd /path/to/ai.archives
python scripts/setup.py --data-repo /path/to/storage/location/ai.archives.myapp
```

This script will:
1. Check prerequisites
2. Configure the data repository
3. Create the necessary directory structure
4. Generate an initial .cursorrules file

For more advanced setup options:

```bash
python scripts/setup.py --help
```

## Integrating with Frontend Projects

### Method 1: Symlink (Recommended)

Create symlinks to both repositories in your frontend project:

```bash
python scripts/setup.py --data-repo /path/to/ai.archives.myapp --link frontend /path/to/frontend/project
```

This will:
1. Create a symlink to the AI Archives in your project
2. Create a symlink to your data repository
3. (Optional) Copy the .cursorrules file to your project

### Method 2: Direct File Access

If symlinks are not an option, you can directly access the files:

```bash
# Set environment variables to point to the repositories
export AI_ARCHIVES_MAIN=/path/to/ai.archives
export AI_ARCHIVES_DATA=/path/to/ai.archives.myapp

# Run commands directly
$AI_ARCHIVES_MAIN/scripts/archives_cli.py --data-repo=$AI_ARCHIVES_DATA add --project=frontend --section=setup --title="Project Setup" --content="Your knowledge here"
```

### Frontend-Specific Archives

After integrating with your frontend project, you can start adding project-specific knowledge:

```bash
# Add frontend setup documentation
python scripts/archives_cli.py add --project=frontend --section=setup --title="Project Setup" --file=setup.md

# Add frontend architecture documentation
python scripts/archives_cli.py add --project=frontend --section=architecture --title="Architecture" --file=architecture.md
```

## Integrating with Backend Projects

The integration process for backend projects is similar to frontend projects:

### Method 1: Symlink (Recommended)

```bash
python scripts/setup.py --data-repo /path/to/ai.archives.myapp --link backend /path/to/backend/project
```

### Method 2: Direct File Access

```bash
# Set environment variables to point to the repositories
export AI_ARCHIVES_MAIN=/path/to/ai.archives
export AI_ARCHIVES_DATA=/path/to/ai.archives.myapp

# Run commands directly
$AI_ARCHIVES_MAIN/scripts/archives_cli.py --data-repo=$AI_ARCHIVES_DATA add --project=backend --section=apis --title="API Documentation" --content="Your API documentation here"
```

### Backend-Specific Archives

After integrating with your backend project, you can start adding project-specific knowledge:

```bash
# Add backend API documentation
python scripts/archives_cli.py add --project=backend --section=apis --title="API Documentation" --file=api-docs.md

# Add backend database schema documentation
python scripts/archives_cli.py add --project=backend --section=architecture --title="Database Schema" --file=schema.md
```

## Cross-Project Knowledge Sharing

The AI Archives system enables knowledge sharing between frontend and backend projects through the shared archives.

### Adding Shared Knowledge

```bash
# Add shared architecture documentation
python scripts/archives_cli.py add --project=shared --section=architecture --title="System Architecture" --file=system-architecture.md

# Add shared authentication flow documentation
python scripts/archives_cli.py add --project=shared --section=setup --title="Authentication Flow" --file=auth-flow.md
```

### Accessing Shared Knowledge

In both frontend and backend projects, AI agents can access the shared knowledge:

```bash
# Search for authentication-related information
python scripts/archives_cli.py search "authentication"
```

## Custom Rules

Custom rules allow you to define project-specific rules for AI agents to follow.

### Adding Custom Rules

Create a new custom rule:

```bash
# Add a custom rule from a file
python scripts/archives_cli.py rule add --name=code_style --file=code-style-rules.md

# Or add a custom rule inline
python scripts/archives_cli.py rule add --name=git_workflow --content="# Git Workflow
1. Create feature branch from develop
2. Submit PR for review
3. Squash and merge to develop"
```

### Listing Custom Rules

```bash
python scripts/archives_cli.py rule list
```

### Generating Combined Cursorrules

After adding custom rules, generate a combined cursorrules file:

```bash
python scripts/integrate_cursorrules.py
```

This will fetch the base cursorrules file from the source repository and merge it with your custom rules.

## Maintenance

### Updating Archives

Regularly update the archives with new knowledge:

```bash
# After fixing a bug or implementing a feature
python scripts/archives_cli.py add --project=frontend --section=fixes --title="Fixed Layout Bug"
```

### Updating the AI Archives System

To update the main system repository:

```bash
cd /path/to/ai.archives
git pull
```

Your data repository remains untouched, preserving your knowledge while allowing you to benefit from system improvements.

### File Size Management

The AI Archives system automatically manages file sizes:
- When an archive file exceeds 500 lines (configurable), a new file is created
- You don't need to worry about managing file sizes manually

## Troubleshooting

### Common Issues

1. **Repository Path Issues**: If you're getting errors about not finding the data repository, make sure the path is correctly set in the configuration:
   ```bash
   # Check your data repository configuration
   cat /path/to/ai.archives/archives/core/config.json
   ```

2. **Import Errors**: Make sure you're running scripts from the correct directory
   ```bash
   cd /path/to/ai.archives
   python scripts/archives_cli.py ...
   ```

3. **GitHub API Errors**: Ensure your GitHub token is set and has the required permissions if using GitHub functionality
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

4. **File Not Found Errors**: Check paths and directory structure
   ```bash
   # Verify directory structure
   python scripts/setup.py
   ```

5. **Permission Errors**: Ensure you have write permissions to the target directories
   ```bash
   # Check if you can write to the directory
   touch /path/to/target/directory/test.txt
   rm /path/to/target/directory/test.txt
   ```

### Getting Help

If you encounter any issues not covered here, please create an issue in the [GitHub repository](https://github.com/tylerqr/ai.archives/issues). 