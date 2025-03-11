# AI Archives System

Give long-lived memories and searchable archives to LLMs using Cursor.

## Overview

The AI Archives system is an extension of the [multi-agent cursorrules system](https://github.com/grapeot/devin.cursorrules/tree/multi-agent). It provides a way for AI agents to maintain knowledge across sessions, learn from past experiences, and effectively work across multiple projects.

## Repository Structure

The AI Archives system has a simple structure:

```
ai.archives/
├── archives/           # Archive content
│   ├── projects/       # Project-specific archives
│   └── archives/       # Archive data storage
├── scripts/            # Utility scripts
├── archives_api.py     # External API
├── custom-rules.md     # Default custom rules
├── server.py           # REST API server
├── archives_client.py  # REST API client library
├── ai_archives.py      # Simplified CLI wrapper
├── archive_scratchpad.sh # Helper script for archiving scratchpad content
└── README.md
```

The `archives/` directory is used for storing your knowledge. This organization allows you to keep your project knowledge private while still benefiting from system updates.

## Installation

### Prerequisites

- Python 3.9 or higher
- Git

#### macOS Users

If you're on macOS, we recommend using Homebrew for a smoother installation:

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.9 or higher
brew install python@3.9
```

### Installation Steps

1. Clone the repository to a location outside your projects:
```bash
git clone https://github.com/tylerqr/ai.archives.git ~/ai-systems/ai.archives
cd ~/ai-systems/ai.archives
```

2. Run the installation script:
```bash
./install.sh
```

The script will:
- Set up a Python environment (using your system Python or creating a virtual environment if needed)
- Install all required dependencies
- Set up your archives directory
- Create an activation script

3. Activate the environment (if using a virtual environment):
```bash
source activate_archives.sh
```

## Usage

If using a virtual environment, activate it before using AI Archives:

```bash
cd ~/ai-systems/ai.archives  # or wherever you installed it
source activate_archives.sh
```

Then you can use the archives:

```bash
# Add content to the archives
python scripts/archives_cli.py add --project=frontend --section=errors --title="JWT Authentication Error" --content="Detailed description of the issue..."

# Search the archives
python scripts/archives_cli.py quick-search "authentication error"

# List available archives
python scripts/archives_cli.py list
```

### REST API Server

Start the server:

```bash
python ai_archives.py server
```

The server runs on http://localhost:5000.

## Integrating with Your Projects

The AI Archives system is designed to be minimally invasive to your coding projects. Integration requires only two things:

1. A symbolic link to the AI Archives system
2. A .cursorrules file in your project

### Simple Integration Steps

1. Create a symbolic link to the ai.archives repository from your project:
   ```bash
   # From your project directory
   ln -s /path/to/ai.archives ai.archives
   ```

2. Generate a .cursorrules file for your project:
   ```bash
   # From your project directory
   /path/to/ai.archives/run_archives.sh generate
   ```

That's it! The AI Archives system will now be available to AI agents working in your project, without installing any dependencies or creating any virtual environments in your project directory.

### Using Archives from Your Project

Once integrated, you can use the archives directly from your project:

```bash
# Search archives
./ai.archives/run_archives.sh search "your search term"

# Add to archives
./ai.archives/run_archives.sh add frontend errors "Error Title" "Error message"

# Archive entire scratchpad content and reset it
./ai.archives/archive_scratchpad.sh frontend errors "Comprehensive Error Documentation"
```

The `run_archives.sh` script handles all the environment setup automatically, so you don't need to worry about activating virtual environments or installing dependencies in your project.

### Archiving Scratchpad Content

The AI Archives system includes a helper script for archiving the entire content of the scratchpad.md file and resetting it to its default empty state:

```bash
# Usage
./ai.archives/archive_scratchpad.sh <project> <section> "Title"

# Example
./ai.archives/archive_scratchpad.sh shared fixes "NativeWind Removal - Complete Migration Guide"
```

This script:
1. Reads the entire content of the scratchpad.md file
2. Archives it with the specified project, section, and title
3. Resets the scratchpad.md file to its default empty state for the next task

This ensures that all valuable information from the scratchpad is preserved in the archives while keeping the scratchpad clean for new tasks.

## Detailed Setup Options

The AI Archives system provides several options via the wrapper script:

```bash
./run_archives.sh --help
```

Key commands:

- `server`: Start the REST API server
- `search`: Search archives
- `add`: Add content to archives
- `rule-add`: Add/update custom rules
- `rules`: List custom rules
- `generate`: Generate combined cursorrules file
- `projects`: List available projects
- `sections`: List sections for a project

## Documentation

For detailed instructions on using the AI Archives system, please see the [Integration Guide](INTEGRATION_GUIDE.md). This guide covers:

- Setting up the archives in your projects
- Custom rules management
- Advanced configuration options
- REST API for AI agents
- Troubleshooting common issues

## Command-Line Interface

The AI Archives system includes a wrapper script for easy interaction:

```bash
./ai.archives/run_archives.sh --help
```

Available commands:

- `search`: Search archives
- `add`: Add content to archives
- `rules`: List custom rules
- `rule-add`: Add/update custom rules
- `generate`: Generate combined cursorrules file
- `projects`: List available projects
- `sections`: List sections for a project

## REST API

The system includes a REST API for simplified access:

```bash
# Start the REST API server
./ai.archives/run_archives.sh server
```

Key endpoints:
- `GET /search?query=<query>`: Search archives
- `GET /quick-search?query=<query>&format=text`: AI-optimized search
- `POST /add`: Add content to archives
- `GET /rules`: List custom rules
- `POST /rules`: Add/update a rule
- `POST /generate-cursorrules`: Generate cursorrules file

## How it Works

1. **Knowledge Storage**: Content is stored in Markdown files organized by project and section
2. **Custom Rules**: Rules are stored in separate files and merged into the cursorrules file
3. **AI Integration**: The generated .cursorrules file instructs AI agents how to use the archives
4. **Search**: The search functionality finds relevant information across all archives
5. **REST API**: Provides a simplified interface for AI agents that avoids environment issues

## Contributing

Contributions to improve the AI Archives system are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
