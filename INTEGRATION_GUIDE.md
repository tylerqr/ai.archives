# AI Archives Integration Guide

This guide explains how to integrate the AI Archives system with your existing projects to enable long-lived memory and knowledge sharing for AI agents.

## Table of Contents

- [Prerequisites](#prerequisites)
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

## Installation

1. Clone the AI Archives repository:

```bash
git clone https://github.com/tylerqr/ai.archives.git
cd ai.archives
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up GitHub access:

```bash
# Set GitHub token for API access (recommended)
export GITHUB_TOKEN=your_github_token
```

## Basic Setup

The AI Archives system provides a setup script to help you get started:

```bash
python scripts/setup.py
```

This script will check prerequisites, validate the directory structure, and guide you through the setup process.

For more advanced setup options:

```bash
python scripts/setup.py --help
```

## Integrating with Frontend Projects

### Method 1: Symlink (Recommended)

Create a symlink to the AI Archives system in your frontend project:

```bash
python scripts/setup.py --link frontend /path/to/frontend/project
```

This will:
1. Create a symlink to the AI Archives in your project
2. (Optional) Copy the .cursorrules file to your project

### Method 2: Copy

Copy the AI Archives system to your frontend project:

```bash
python scripts/setup.py --target /path/to/frontend/project
```

This will copy all necessary files to your frontend project directory.

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
python scripts/setup.py --link backend /path/to/backend/project
```

### Method 2: Copy

```bash
python scripts/setup.py --target /path/to/backend/project
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

### Updating Base Cursorrules

Update the base cursorrules file from the source repository:

```bash
python scripts/integrate_cursorrules.py
```

### File Size Management

The AI Archives system automatically manages file sizes:
- When an archive file exceeds 500 lines (configurable), a new file is created
- You don't need to worry about managing file sizes manually

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running scripts from the correct directory
   ```bash
   cd /path/to/ai.archives
   python scripts/archives_cli.py ...
   ```

2. **GitHub API Errors**: Ensure your GitHub token is set and has the required permissions
   ```bash
   export GITHUB_TOKEN=your_github_token
   ```

3. **File Not Found Errors**: Check paths and directory structure
   ```bash
   # Verify directory structure
   python scripts/setup.py
   ```

4. **Permission Errors**: Ensure you have write permissions to the target directories
   ```bash
   # Check if you can write to the directory
   touch /path/to/target/directory/test.txt
   rm /path/to/target/directory/test.txt
   ```

### Getting Help

If you encounter any issues not covered here, please create an issue in the [GitHub repository](https://github.com/tylerqr/ai.archives/issues). 