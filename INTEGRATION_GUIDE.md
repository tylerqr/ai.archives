# AI Archives Integration Guide

This guide explains how to integrate the AI Archives system with your existing projects to enable long-lived memory and knowledge sharing for AI agents.

## Table of Contents

- [Prerequisites](#prerequisites)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Project Integration](#project-integration)
- [Data Management](#data-management)
- [Custom Rules](#custom-rules)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing the AI Archives system, ensure you have:

- Python 3.8 or higher
- Git
- A proper location **outside** of your existing projects to install the system

## System Architecture

The AI Archives system uses a single-repository architecture with a configurable data path:

1. **Main Repository** (`ai.archives`): Contains the core system code, scripts, and utilities
2. **Archives Directory** (`archives/` by default): Stores your project-specific archives, knowledge, and custom rules

The archives directory contains your knowledge and custom rules, allowing you to:
- Maintain your knowledge outside of version control if desired
- Update the system without affecting your archives
- Preserve your archives during system updates

### Directory Structure

```
ai.archives/                # Main system repository
├── archives/               # Archives storage
│   ├── projects/           # Project-specific content
│   ├── custom_rules/       # User custom rules
│   └── archives/           # Archive data
├── scripts/                # System scripts
│   ├── archives_cli.py     # Command-line interface
│   └── integrate_cursorrules.py # Rule integration tool
├── archives_api.py         # External API for integration
├── custom-rules.md         # Default custom rules template
└── .cursorrules            # Generated cursorrules file
```

## Installation

### ⚠️ IMPORTANT: Repository Placement

When setting up the AI Archives system, repository placement is CRITICAL to avoid Git conflicts and corruption of existing projects. Follow these strict guidelines:

1. **NEVER install the AI Archives inside an existing project directory**
2. **ALWAYS use a completely separate location for the AI Archives**

Example of CORRECT installation:
```
/Users/username/
├── projects/                  # User's regular projects folder
│   └── my-project/            # User's existing project
│       └── ...
└── ai-systems/               # Separate location for AI tools
    └── ai.archives/          # AI Archives repository (INSTALL HERE)
```

Example of INCORRECT installation (DO NOT DO THIS):
```
/Users/username/projects/my-project/  # User's existing project
├── .git/                             # User's project git repo
├── ai.archives/                      # ⛔ WRONG! Don't install inside existing project
└── ...
```

### Installation Steps

#### ATTENTION AI AGENTS:

When a user asks you to set up the AI Archives system:

1. Ask the user where they want to store the AI Archives repository
2. Recommend a location OUTSIDE of any existing project directories
3. DO NOT place the archives inside the user's current working project

#### Standard Installation

1. Clone the main AI Archives repository to a location OUTSIDE of any existing project directories:

```bash
# Create a directory for AI tools if it doesn't exist
mkdir -p ~/ai-systems
cd ~/ai-systems

# Clone the repository
git clone https://github.com/tylerqr/ai.archives.git
cd ai.archives

# Run the setup script
python scripts/setup.py --install
```

The setup script will ask you where you want to store your archives data. The default location is `./data/` within the repository. You can specify a different location with the `--data-path` option.

## Project Integration

### Linking to Existing Projects

To integrate the AI Archives with your existing projects:

```bash
# Navigate to the AI Archives repository
cd ~/ai-systems/ai.archives

# Link to your project
python scripts/setup.py --link /path/to/your/project
```

This will:
1. Generate a .cursorrules file in your project
2. Configure the file to use the AI Archives system

### Usage from Linked Projects

Once linked, you can use the archives from your project:

```bash
# Add content to the archives
python /path/to/ai.archives/scripts/archives_cli.py add --project=frontend --section=setup --title="Project Setup" --content="Your knowledge here"

# Search the archives
python /path/to/ai.archives/scripts/archives_cli.py quick-search "your search query"
```

## Data Management

### Frontend-Specific Archives

Store frontend knowledge in the `frontend` project:

```bash
# Example: Adding frontend setup information
python scripts/archives_cli.py add --project=frontend --section=setup --title="Project Setup" --file=setup.md

# Example: Adding architecture documentation
python scripts/archives_cli.py add --project=frontend --section=architecture --title="Architecture" --file=architecture.md
```

### Backend-Specific Archives

Store backend knowledge in the `backend` project:

```bash
# Example: Adding API documentation
python scripts/archives_cli.py add --project=backend --section=apis --title="API Documentation" --file=api-docs.md

# Example: Adding database schema
python scripts/archives_cli.py add --project=backend --section=architecture --title="Database Schema" --file=schema.md
```

### Shared Knowledge

Store shared knowledge in the `shared` project:

```bash
# Example: Adding system architecture
python scripts/archives_cli.py add --project=shared --section=architecture --title="System Architecture" --file=system-architecture.md

# Example: Adding authentication flow
python scripts/archives_cli.py add --project=shared --section=setup --title="Authentication Flow" --file=auth-flow.md
```

### Searching Archives

To search for information across all projects:

```bash
# Search for "authentication"
python scripts/archives_cli.py quick-search "authentication"
```

#### Intelligent Tokenized Search

The AI Archives system uses an intelligent tokenized search algorithm that breaks your query into individual words and finds documents containing those words. This means:

- Multi-word queries like "react native styling" will find documents containing those words, even if the exact phrase doesn't appear
- Results are ranked by the number of token matches, with the most relevant results first
- Search results show a "Match Quality" score indicating how many token matches were found
- Exact phrase matches are still prioritized for backward compatibility

For best results:
- Include specific keywords in your search queries
- Use multiple relevant terms to narrow down results
- Check the Match Quality score to understand why a result was returned

```bash
# Examples of effective tokenized searches
python scripts/archives_cli.py quick-search "babel config styling"
python scripts/archives_cli.py quick-search "styling issues react native"
```

## Custom Rules

Custom rules allow you to define AI agent behavior specifically for your project. They are stored in the data directory and merged into the cursorrules file.

### Adding Custom Rules

```bash
# Add a rule for code style
python scripts/archives_cli.py rule add --name=code_style --file=code-style-rules.md

# Add a rule for Git workflow
python scripts/archives_cli.py rule add --name=git_workflow --content="# Git Workflow
- Use feature branches for all new features
- Create pull requests for code review
- Squash commits when merging"
```

### Listing Custom Rules

```bash
python scripts/archives_cli.py rule list
```

### Regenerating .cursorrules

After adding or updating custom rules, regenerate the .cursorrules file:

```bash
python scripts/integrate_cursorrules.py
```

## Advanced Configuration

### Customizing Data Location

You can customize where your archives data is stored by specifying the `--data-path` option:

```bash
# During installation
python scripts/setup.py --install --data-path /path/to/your/data

# After installation
python scripts/setup.py --setup-data --data-path /path/to/your/data
```

### Running Commands with Custom Data Path

When using the CLI, you can specify the data path:

```bash
python scripts/archives_cli.py --data-path /path/to/your/data quick-search "query"
```

### Updating Archives

Regularly update the archives with new knowledge:

```bash
# Add new information
python scripts/archives_cli.py add --project=frontend --section=fixes --title="Fixed Layout Bug" --content="..."
```

### Updating the AI Archives System

To update to the latest version of the AI Archives system:

```bash
cd /path/to/ai.archives
git pull
```

Your archives data will remain untouched, as it's stored in the gitignored `data/` directory.

## Troubleshooting

### File Size Management

The AI Archives system automatically manages file sizes:

- Large files are split into multiple files
- Each file has a maximum line count (configurable in `archives/core/config.json`)

### Configuration Issues

If you need to check or update the system configuration:

```bash
cat /path/to/ai.archives/archives/core/config.json
```

### CLI Not Working

If you encounter issues with the CLI:

```bash
cd /path/to/ai.archives
python scripts/archives_cli.py --help
```

### Get Additional Help

If you encounter any issues not covered here, please create an issue in the [GitHub repository](https://github.com/tylerqr/ai.archives/issues). 