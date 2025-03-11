# AI Archives Integration Guide

This guide explains how to integrate the AI Archives system with your existing projects to enable long-lived memory and knowledge sharing for AI agents.

## Table of Contents

- [Prerequisites](#prerequisites)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Project Integration](#project-integration)
- [Data Management](#data-management)
- [Custom Rules](#custom-rules)
- [REST API for AI Agents](#rest-api-for-ai-agents)
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
│   └── archives/           # Archive data
├── scripts/                # System scripts
│   ├── archives_cli.py     # Command-line interface
│   └── integrate_cursorrules.py # Rule integration tool
├── archives_api.py         # External API for integration
├── custom-rules.md         # Default custom rules template
├── server.py               # REST API server
├── archives_client.py      # REST API client library
├── ai_archives.py          # Simplified CLI wrapper
└── .cursorrules            # Generated cursorrules file
```

## Installation

### ⚠️ IMPORTANT: Repository Placement

When setting up the AI Archives system, repository placement is CRITICAL to avoid Git conflicts and corruption of existing projects. Follow these strict guidelines:

1. **NEVER install the AI Archives inside an existing project directory**
2. **ALWAYS use a completely separate location for the AI Archives**
3. **NEVER clone the AI Archives repository directly into the user's existing Git repository**
4. **ALWAYS use a symbolic link to connect from the user's project to the AI Archives**

Example of CORRECT installation:
```
/Users/username/
├── projects/                  # User's regular projects folder
│   └── my-project/            # User's existing project
│       ├── .git/              # User's project git repo
│       ├── ai.archives -> /Users/username/ai-systems/ai.archives/  # SYMBOLIC LINK to AI Archives
│       └── ...
└── ai-systems/               # Separate location for AI tools
    └── ai.archives/          # AI Archives repository (INSTALL HERE)
        ├── .git/             # AI Archives git repo
        └── ...
```

Example of INCORRECT installation (DO NOT DO THIS):
```
/Users/username/projects/my-project/  # User's existing project
├── .git/                             # User's project git repo
├── ai.archives/                      # ⛔ WRONG! Don't install inside existing project
│   ├── .git/                         # This creates nested Git repositories!
│   └── ...
└── ...
```

### Virtual Environments and Dependencies

#### IMPORTANT: The AI Archives system does not require a virtual environment in your projects

When integrating AI Archives with your projects:

1. **DO NOT create a virtual environment** within your project specifically for AI Archives
2. **DO NOT install Flask or other AI Archives dependencies** within your project
3. The AI Archives system is designed to work with the system Python installation
4. Any necessary dependencies should be installed only in the AI Archives directory, not in individual projects
5. AI agents should not attempt to create virtual environments when using a project with AI Archives integration
6. Keep your project's dependency management separate from the AI Archives system

If your project requires its own virtual environment for other purposes, that's fine, but the AI Archives integration does not need or use it.

### Installation Steps

#### ATTENTION AI AGENTS:

When a user asks you to set up the AI Archives system:

1. Ask the user where they want to store the AI Archives repository
2. Recommend a location OUTSIDE of any existing project directories (e.g., ~/ai-systems/)
3. DO NOT place the archives inside the user's current working project
4. AFTER installing the AI Archives in a separate location, create a SYMBOLIC LINK from the user's project to the AI Archives

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

2. After installation is complete, create a symbolic link from your project to the AI Archives:

```bash
# From your project directory
ln -s /path/to/ai.archives ai.archives
```

The setup script will ask you where you want to store your archives data. The default location is `./data/` within the repository. You can specify a different location with the `--data-path` option.

## Project Integration

### Linking to Existing Projects

To integrate the AI Archives with your existing projects, you MUST create a symbolic link:

```bash
# From your project directory
ln -s /path/to/ai.archives ai.archives
```

This will create a symbolic link to the AI Archives system in your project directory, allowing you to easily access the archives functionality WITHOUT nesting Git repositories.

⚠️ **DO NOT** clone the AI Archives repository directly into your project directory. This will create nested Git repositories and cause problems.

### Usage from Linked Projects

Once linked, you can use the archives from your project:

```bash
# Search the archives
./ai.archives/run_archives.sh search "your search query"

# Add content to the archives
./ai.archives/run_archives.sh add frontend setup "Project Setup" "Your knowledge here"

# Generate cursorrules
./ai.archives/run_archives.sh generate
```

All commands are executed through the wrapper script, which handles server management and environment setup automatically.

## Data Management

### Frontend-Specific Archives

Store frontend knowledge in the `frontend` project:

```bash
# Example: Adding frontend setup information
./ai.archives/run_archives.sh add frontend setup "Project Setup" "Your setup documentation here"

# Example: Adding architecture documentation
./ai.archives/run_archives.sh add frontend architecture "Architecture" "Your architecture docs here"
```

### Backend-Specific Archives

Store backend knowledge in the `backend` project:

```bash
# Example: Adding API documentation
./ai.archives/run_archives.sh add backend apis "API Documentation" "Your API docs here"

# Example: Adding database schema
./ai.archives/run_archives.sh add backend architecture "Database Schema" "Your schema docs here"
```

### Shared Knowledge

Store shared knowledge in the `shared` project:

```bash
# Example: Adding system architecture
./ai.archives/run_archives.sh add shared architecture "System Architecture" "Your system architecture docs"

# Example: Adding authentication flow
./ai.archives/run_archives.sh add shared setup "Authentication Flow" "Your auth flow docs"
```

### Searching Archives

To search for information across all projects:

```bash
# Search for "authentication"
./ai.archives/run_archives.sh search "authentication"
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
./ai.archives/run_archives.sh search "babel config styling"
./ai.archives/run_archives.sh search "styling issues react native"
```

## Custom Rules

Custom rules allow you to define AI agent behavior specifically for your project. They are stored in the root directory and merged into the cursorrules file.

### Adding Custom Rules

```bash
# Add a rule for code style
./ai.archives/run_archives.sh rule-add code_style "# Code Style Guide
- Use 2 spaces for indentation
- Use camelCase for variables
- Use PascalCase for components"

# Add a rule for Git workflow
./ai.archives/run_archives.sh rule-add git_workflow "# Git Workflow
- Use feature branches for all new features
- Create pull requests for code review
- Squash commits when merging"
```

### Listing Custom Rules

```bash
./ai.archives/run_archives.sh rules
```

### Regenerating .cursorrules

After adding or updating custom rules, regenerate the .cursorrules file:

```bash
./ai.archives/run_archives.sh generate
```

## REST API for AI Agents

The AI Archives system includes a REST API specifically designed for AI agents. This API simplifies interaction with the archives by eliminating environment issues and providing a more consistent interface.

### Starting the API Server

To start the REST API server:

```bash
./ai.archives/run_archives.sh server
```

The server will start on http://localhost:5001 by default.

### Using the Wrapper Script

The system includes a wrapper script that AI agents can use to interact with the archives:

```bash
# Search archives
./ai.archives/run_archives.sh search "authentication error"

# Add content
./ai.archives/run_archives.sh add frontend errors "Error Title" "Error message"

# List projects
./ai.archives/run_archives.sh projects

# List sections
./ai.archives/run_archives.sh sections frontend

# Get rules
./ai.archives/run_archives.sh rules

# Add/update rule
./ai.archives/run_archives.sh rule-add code_style "# Code Style Guide..."

# Generate cursorrules
./ai.archives/run_archives.sh generate
```

### REST API Endpoints

The REST API provides the following endpoints:

#### Search Endpoints

- **GET /search?query=QUERY&project=PROJECT**
  - Search the archives with JSON response
  - Optional project parameter to filter by project

- **GET /quick-search?query=QUERY&project=PROJECT&format=FORMAT**
  - AI-optimized search with formatted results
  - format can be "json" or "text" (text is optimized for direct inclusion in AI responses)

#### Content Management

- **POST /add**
  - Add content to archives
  - JSON body: `{"project": "...", "section": "...", "content": "...", "title": "..."}`

#### Custom Rules

- **GET /rules**
  - Get all custom rules

- **POST /rules**
  - Add or update a custom rule
  - JSON body: `{"name": "...", "content": "..."}`

- **POST /generate-cursorrules**
  - Generate combined cursorrules file
  - Optional JSON body: `{"output_path": "..."}`

#### Discovery

- **GET /list-projects**
  - List all available projects

- **GET /list-sections?project=PROJECT**
  - List all sections for a project

#### Health Check

- **GET /ping**
  - Simple health check to verify the server is running

### Advantages for AI Agents

Using the REST API offers several advantages for AI agents:

1. **Simplicity**: No need to deal with Python environment activation
2. **Consistency**: Standardized interface across different environments
3. **Error Handling**: Better error reporting and recovery
4. **Formatted Responses**: Results are formatted specifically for AI agent consumption
5. **Reduced Tool Calls**: Simpler commands mean fewer tool calls, speeding up interactions

### Python Client Library

For more advanced use cases, the system also includes a Python client library:

```python
from archives_client import ArchivesClient

client = ArchivesClient(base_url="http://localhost:5000")

# Search archives
results = client.quick_search("authentication", format_type="text")
print(results)

# Add to archives
client.add("frontend", "errors", "Error message", "Error Title")

# List projects
projects = client.list_projects()
print(projects)
```

## Advanced Configuration

### Customizing Data Location

The data location is configured in the core/config.json file:

```bash
# View current configuration
cat /path/to/ai.archives/core/config.json
```

### Updating Archives

Regularly update the archives with new knowledge:

```bash
# Add new information
./ai.archives/run_archives.sh add frontend fixes "Fixed Layout Bug" "Description of the fix..."
```

### Updating the AI Archives System

To update to the latest version of the AI Archives system:

```bash
cd /path/to/ai.archives
git pull
```

Your archives data will remain untouched, as it's stored separately from the code repository.

## Troubleshooting

### File Size Management

The AI Archives system automatically manages file sizes:

- Large files are split into multiple files
- Each file has a maximum line count (configurable in `core/config.json`)

### Server Connection Issues

If you encounter connection refused errors:

```bash
# Make sure the server is running
./ai.archives/run_archives.sh server
```

### CLI Not Working

If you encounter issues with the CLI:

```bash
# Check if the wrapper script is executable
chmod +x /path/to/ai.archives/run_archives.sh

# Try running with help flag
./ai.archives/run_archives.sh --help
```

### Get Additional Help

If you encounter any issues not covered here, please create an issue in the [GitHub repository](https://github.com/tylerqr/ai.archives/issues). 