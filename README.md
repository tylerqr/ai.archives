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

## Directory Structure

```
ai.archives/
├── archives/
│   ├── core/            # Core system files and utilities
│   ├── projects/        # Project-specific knowledge
│   │   ├── frontend/    # Frontend project knowledge
│   │   └── backend/     # Backend project knowledge
│   ├── custom_rules/    # Custom cursorrules that survive updates
│   └── api/             # API documentation and cross-project reference
├── scripts/             # Utility scripts for managing the archives
└── .cursorrules         # The combined cursorrules file with custom rules
```

## How It Works

1. **Knowledge Preservation**: AI agents document insights, errors, and solutions in the appropriate archives
2. **Context Refreshing**: Before starting a task, AI agents review relevant archives
3. **Custom Rules**: User-specific rules are stored separately and merged with the base cursorrules
4. **Cross-Project Communication**: Frontend and backend knowledge is shared through the archives

## Usage

Instructions for integrating the AI Archives system with your projects will be provided in the setup documentation.

## Contributing

Contributions to improve the AI Archives system are welcome.

## License

[Specify your license here]
