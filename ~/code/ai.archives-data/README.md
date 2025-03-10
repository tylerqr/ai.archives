# AI Archives Data Repository

This repository stores the actual archive content for the AI Archives system. It's separated from the system code to allow independent versioning and management of archive content.

## Structure

```
ai.archives-data/
└── archives/
    ├── projects/
    │   ├── frontend/    # Frontend-specific knowledge
    │   ├── backend/     # Backend-specific knowledge
    │   └── shared/      # Shared knowledge across projects
    └── custom_rules/    # Custom rules for AI agent behavior
```

## Purpose

- **Content Preservation**: Safely store accumulated knowledge
- **Versioning Independence**: Archive content versions separate from system code
- **Cross-Project Knowledge**: Share information between frontend and backend projects

## Usage

This repository is designed to be used with the [AI Archives system](https://github.com/tylerqr/ai.archives). It should be linked via symlinks as described in the integration guide.

DO NOT DIRECTLY MODIFY FILES in this repository - all interactions should happen through the AI Archives system's CLI tools. 