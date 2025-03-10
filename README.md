# AI Archives System

Give long-lived memories and searchable archives to LLMs using Cursor.

## Overview

The AI Archives system is an extension of the [multi-agent cursorrules system](https://github.com/grapeot/devin.cursorrules/tree/multi-agent). It provides a way for AI agents to maintain knowledge across sessions, learn from past experiences, and effectively work across multiple projects.

## Repository Structure

The AI Archives system has a simple structure:

```
ai.archives/
├── archives/           # System code
│   ├── core/           # Core functionality
│   ├── api/            # External API
│   ├── examples/       # Example content
│   └── custom_rules/   # Default custom rules
├── scripts/            # Utility scripts
├── data/               # User data (gitignored)
│   └── archives/       # Archive content
│       ├── projects/   # Project-specific archives
│       └── custom_rules/ # User custom rules
└── README.md
```

The `data/` directory is gitignored, meaning your archives content won't be included in updates to the system. This separation allows you to keep your project knowledge private while still benefiting from system updates.

## ⚠️ IMPORTANT: Installation Location

ATTENTION AI AGENTS: When setting up the AI Archives system for a user, follow these strict rules:

1. **NEVER install the AI Archives inside an existing Git project directory**
2. **ALWAYS install into a separate, standalone location outside of the user's current project**
3. **Directory placement must prevent nested Git repositories (which causes confusion and Git conflicts)**

Example of CORRECT installation:
```
/Users/username/
├── projects/                  # User's regular projects folder
│   └── my-project/            # User's existing project (where they might be when they ask for integration)
│       └── ...
└── ai-systems/               # Separate location for AI tools
    └── ai.archives/          # AI Archives repository (INSTALL HERE)
```

Example of INCORRECT installation (DO NOT DO THIS):
```
/Users/username/projects/my-project/  # User's existing project
├── .git/                             # User's project git repo
├── ai.archives/                      # WRONG! Don't install inside existing project
└── ...
```

## Key Features

- **Persistent Knowledge Base**: Preserves insights, error solutions, and project knowledge across sessions
- **Multi-Project Support**: Enables AI agents to share knowledge between frontend and backend projects
- **Custom Rules Management**: Maintains custom rules separate from the base cursorrules file
- **Intelligent Search**: Uses tokenized search for better results with multi-word queries
- **Searchable Archives**: Quickly find relevant information in your archives

## Quick Start

### Installation

To install the AI Archives system, run:

```bash
# Clone the repository outside of any existing project
git clone https://github.com/tylerqr/ai.archives.git ~/ai-systems/ai.archives
cd ~/ai-systems/ai.archives

# Set up the system with the setup script
python scripts/setup.py --install
```

The setup script will:

1. Ask where you want to store your archives data (default: ./data/)
2. Create the necessary directory structure
3. Initialize the archives with sample content
4. Generate a .cursorrules file

### Usage

Once installed, you can interact with the archives using the CLI:

```bash
# Add content to the archives
python scripts/archives_cli.py add --project=frontend --section=errors --title="JWT Authentication Error" --content="Detailed description of the issue..."

# Search the archives
python scripts/archives_cli.py quick-search "authentication error"

# List available archives
python scripts/archives_cli.py list

# Add custom rules
python scripts/archives_cli.py rule add --name=code_style --content="# Code Style Rules\n\nUse 2 spaces for indentation..."

# Generate .cursorrules file (after updating custom rules)
python scripts/integrate_cursorrules.py
```

### Integrating with Your Projects

To use the archives with your existing projects:

1. Link the archives to your project:
   ```bash
   python scripts/setup.py --link /path/to/your/project
   ```

2. This will create a .cursorrules file in your project that instructs AI agents how to use the archives.

3. When working in your project, you can use the archives with:
   ```bash
   # In your project directory
   python /path/to/ai.archives/scripts/archives_cli.py quick-search "query"
   ```

## Detailed Setup Options

The setup script provides several options:

```bash
python scripts/setup.py --help
```

Key options:

- `--install`: Full installation process
- `--install-path PATH`: Where to install the system
- `--data-path PATH`: Where to store the archives data
- `--link PROJECT_PATH`: Link archives to an existing project
- `--no-examples`: Skip creating example archives

## Documentation

For detailed instructions on using the AI Archives system, please see the [Integration Guide](INTEGRATION_GUIDE.md). This guide covers:

- Setting up the archives in your projects
- Custom rules management
- Advanced configuration options
- Troubleshooting common issues

## Command-Line Interface

The AI Archives system includes a command-line interface for easy interaction:

```bash
python scripts/archives_cli.py --help
```

Available commands:

- `add`: Add content to archives
- `search`: Search archives
- `quick-search`: AI-optimized search
- `list`: List available archives
- `rule`: Manage custom rules
- `generate`: Generate combined cursorrules file

## How it Works

1. **Knowledge Storage**: Content is stored in Markdown files organized by project and section
2. **Custom Rules**: Rules are stored in separate files and merged into the cursorrules file
3. **AI Integration**: The generated .cursorrules file instructs AI agents how to use the archives
4. **Search**: The search functionality finds relevant information across all archives

## Contributing

Contributions to improve the AI Archives system are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
