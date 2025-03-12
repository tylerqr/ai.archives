# AI Archives System

Give long-lived memories and searchable archives to LLMs using Cursor.

## Overview

The AI Archives system is an extension of the [multi-agent cursorrules system](https://github.com/grapeot/devin.cursorrules/tree/multi-agent). It provides a way for AI agents to maintain knowledge across sessions, learn from past experiences, and effectively work across multiple projects.

## Repository Structure

The AI Archives system has a simple structure:

```
ai.archives/
├── archives/           # Archive content organized by project and section
├── templates/          # Templates for various files
├── scripts/            # Utility scripts
├── archives_api.py     # External API
├── custom-rules.md     # Default custom rules
├── server.py           # REST API server
├── archives_client.py  # REST API client library
├── ai_archives.py      # Simplified CLI wrapper
└── README.md
```

The `archives/` directory is used for storing your knowledge. This organization allows you to keep your project knowledge private while still benefiting from system updates.

## Installation

### Prerequisites

- Git
- Python 3.9 or higher

### Installation Steps

1. **Clone the repository** to a location outside your projects:

```bash
git clone https://github.com/tylerqr/ai.archives.git ~/ai-systems/ai.archives
cd ~/ai-systems/ai.archives
```

2. **Install required dependencies**:

```bash
# Using pip
pip install -r requirements.txt

# Using uv (faster)
uv pip install -r requirements.txt
```

3. **Create necessary directories**:

```bash
mkdir -p archives/frontend archives/backend archives/shared
mkdir -p templates
```

4. **Create the empty scratchpad template**:

```bash
cat > templates/empty_scratchpad.md << 'EOF'
# Multi-Agent Scratchpad

## Background and Motivation

(Planner writes: User/business requirements, macro objectives, why this problem needs to be solved)

## Key Challenges and Analysis

(Planner: Records of technical barriers, resource constraints, potential risks)

## Verifiable Success Criteria

(Planner: List measurable or verifiable goals to be achieved)

## High-level Task Breakdown

(Planner: List subtasks by phase, or break down into modules)

## Current Status / Progress Tracking

(Executor: Update completion status after each subtask. If needed, use bullet points or tables to show Done/In progress/Blocked status)

## Next Steps and Action Items

(Planner: Specific arrangements for the Executor)

## Executor's Feedback or Assistance Requests

(Executor: Write here when encountering blockers, questions, or need for more information during execution)
EOF
```

## Integrating with Your Projects

The AI Archives system is designed to be minimally invasive to your coding projects. Integration requires only two things:

1. A symbolic link to the AI Archives system
2. A .cursorrules file in your project

### Integration Steps

1. **Create a symbolic link** to the ai.archives repository from your project:
   ```bash
   # From your project directory
   ln -s /path/to/ai.archives ai.archives
   ```

2. **Generate a .cursorrules file** for your project:
   ```bash
   # From your project directory
   ./ai.archives/run_archives.sh generate
   ```

That's it! The AI Archives system will now be available to AI agents working in your project, without installing any dependencies or creating any virtual environments in your project directory.

## Using Archives from Your Project

Once integrated, you can use the archives directly from your project:

```bash
# Search archives
./ai.archives/run_archives.sh search "your search term"

# Add to archives
./ai.archives/run_archives.sh add frontend errors "Error Title" "Error message"
```

The `run_archives.sh` script handles all the environment setup automatically, so you don't need to worry about activating virtual environments or installing dependencies in your project.

### Project Organization

The archives are organized by project and section:

- **frontend**: UI/client-side content
- **backend**: Server-side content
- **shared**: Cross-cutting concerns

Within each project, you can organize content into sections like:
- **setup**: Installation and configuration
- **errors**: Common errors and solutions
- **fixes**: Bug fixes and workarounds
- **architecture**: System design and architecture

Example usage:
```bash
# Add frontend setup information
./ai.archives/run_archives.sh add frontend setup "React Setup" "Setup instructions..."

# Add backend error information
./ai.archives/run_archives.sh add backend errors "Database Connection Error" "Error details..."

# Add shared architecture information
./ai.archives/run_archives.sh add shared architecture "System Architecture" "Architecture details..."
```

## Archiving Scratchpad Content

The AI Archives system provides two methods for archiving scratchpad content:

### 1. Server-based approach (for smaller content)

```bash
# Using the run_archives.sh script
./ai.archives/run_archives.sh add <project> <section> "Title" "$(cat ./scratchpad.md)"

# Reset scratchpad after archiving
cat ./ai.archives/templates/empty_scratchpad.md > ./scratchpad.md
```

### 2. Direct file approach (for larger content)

For large content that might exceed server request limits:

```bash
# Generate timestamp for the filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PROJECT="shared"  # Change as appropriate: frontend, backend, shared
SECTION="fixes"   # Change as appropriate: setup, errors, fixes, etc.
FILENAME="${PROJECT}_${SECTION}_${TIMESTAMP}.md"

# Create directories if they don't exist
mkdir -p ./ai.archives/archives/$PROJECT/$SECTION

# Write the scratchpad content directly to the archives
cat ./scratchpad.md > ./ai.archives/archives/$PROJECT/$SECTION/$FILENAME

# Reset scratchpad after archiving
cat ./ai.archives/templates/empty_scratchpad.md > ./scratchpad.md

echo "Content archived to: ./ai.archives/archives/$PROJECT/$SECTION/$FILENAME"
```

This direct file approach bypasses the server completely, making it reliable for archiving large scratchpad content.

## Searching Archives

The AI Archives system provides a powerful search capability:

```bash
# Search for information across all projects
./ai.archives/run_archives.sh search "your search query"
```

### Intelligent Tokenized Search

The search system uses an intelligent tokenized search algorithm that:

- Breaks your query into individual words and finds documents containing those words
- Ranks results by the number of token matches, with the most relevant results first
- Shows a "Match Quality" score indicating how many token matches were found
- Prioritizes exact phrase matches

For best results:
- Use specific keywords related to what you're looking for
- Include technical terms that are likely to appear in the content
- Try different variations if you don't find what you need initially

## Available Commands

The AI Archives system provides several commands via the wrapper script:

```bash
# Search archives
./ai.archives/run_archives.sh search "your search query"

# Add to archives
./ai.archives/run_archives.sh add <project> <section> "Title" "Content"

# Generate .cursorrules file
./ai.archives/run_archives.sh generate [output_path]

# List all projects
./ai.archives/run_archives.sh projects

# List sections in a project
./ai.archives/run_archives.sh sections <project>

# Start the server (if you encounter connection issues)
./ai.archives/run_archives.sh server
```

## Troubleshooting

### Server Connection Issues

If you encounter server connection issues:

```bash
# Start the server
./ai.archives/run_archives.sh server
```

### Large Content Errors

If you encounter a 500 Internal Server Error when adding large content:
- Use the direct file approach described above
- Check server logs for specific error details
- Consider breaking your content into smaller chunks if needed

### Updating the AI Archives System

To update to the latest version of the AI Archives system:

```bash
cd /path/to/ai.archives
git pull
```

Your archives data will remain untouched, as it's stored separately from the code repository.

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
