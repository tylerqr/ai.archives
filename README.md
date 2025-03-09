# AI Archives System

Give long-lived memories and searchable archives to LLMs using Cursor.

## Overview

The AI Archives system is an extension of the [multi-agent cursorrules system](https://github.com/grapeot/devin.cursorrules/tree/multi-agent). It provides a way for AI agents to maintain knowledge across sessions, learn from past experiences, and effectively work across multiple projects.

## Key Features

- **Persistent Knowledge Base**: Preserves insights, error solutions, and project knowledge across sessions
- **Multi-Project Support**: Enables AI agents to share knowledge between frontend and backend projects
- **Custom Rules Management**: Maintains custom rules separate from the base cursorrules file
- **Size-Limited Files**: Keeps individual archive files under 500 lines for optimal AI consumption
- **Searchable Content**: Designed for both human and AI readability and searchability

## Quick Start

### Prerequisites

- Git installed and configured
- Python 3.8 or higher
- Basic understanding of command-line operations

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tylerqr/ai.archives.git
   cd ai.archives
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the setup script:
   ```bash
   python scripts/setup.py
   ```

### Basic Usage

Add knowledge to the archives:
```bash
python scripts/archives_cli.py add --project=frontend --section=setup --title="Project Setup" --content="Your knowledge here"
```

Search the archives:
```bash
python scripts/archives_cli.py search "authentication"
```

Add custom rules:
```bash
python scripts/archives_cli.py rule add --name=code_style --content="Your rule here"
```

Generate a combined cursorrules file:
```bash
python scripts/integrate_cursorrules.py
```

## Core Dependencies

- requests==2.31.0: HTTP requests for API interactions
- PyGithub==1.58.1: GitHub API integration
- pyyaml==6.0: YAML parsing and configuration
- python-dotenv==1.0.0: Environment variable management
- click==8.1.3, rich==13.3.5, typer==0.9.0: CLI tools

For a complete list of dependencies, see [requirements.txt](requirements.txt).

## Directory Structure

```
ai.archives/
├── archives/
│   ├── core/            # Core system files and utilities
│   ├── projects/        # Project-specific knowledge
│   │   ├── frontend/    # Frontend project knowledge
│   │   ├── backend/     # Backend project knowledge
│   │   └── shared/      # Shared knowledge across projects
│   ├── custom_rules/    # Custom cursorrules that survive updates
│   └── api/             # API documentation and cross-project reference
├── scripts/             # Utility scripts for managing the archives
├── INTEGRATION_GUIDE.md # Detailed integration instructions
└── requirements.txt     # Python dependencies
```

## How It Works

1. **Knowledge Preservation**: AI agents document insights, errors, and solutions in the appropriate archives
2. **Context Refreshing**: Before starting a task, AI agents review relevant archives
3. **Custom Rules**: User-specific rules are stored separately and merged with the base cursorrules
4. **Cross-Project Communication**: Frontend and backend knowledge is shared through the archives

## Detailed Integration Guide

For detailed instructions on integrating the AI Archives system with your projects, please see the [Integration Guide](INTEGRATION_GUIDE.md). This guide covers:

- Setting up the AI Archives system
- Integrating with frontend and backend projects
- Managing cross-project knowledge sharing
- Adding and maintaining custom rules
- Troubleshooting common issues

## Command-Line Interface

The AI Archives system includes a command-line interface for easy interaction:

```bash
# Get help
python scripts/archives_cli.py --help

# List available archives
python scripts/archives_cli.py list

# Add to archives
python scripts/archives_cli.py add --project=frontend --section=setup

# Search archives
python scripts/archives_cli.py search "query"

# Manage custom rules
python scripts/archives_cli.py rule list
python scripts/archives_cli.py rule add --name=my_rule
```

## Contributing

Contributions to improve the AI Archives system are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here]
