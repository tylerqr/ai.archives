# AI Archives Usage Rules

## Core Rules

- **SEARCH USING WRAPPER SCRIPT**: Use `./ai.archives/run_archives.sh search` for searching archives
- **WRITE DIRECTLY TO ARCHIVES**: Always write archive content directly to the archives directory via the symlink
- **NEVER EDIT .cursorrules DIRECTLY**: This file is auto-generated
- **SEARCH BEFORE ADDING**: Always search archives before adding new content to avoid duplicates
- **INTELLIGENTLY CATEGORIZE CONTENT**: Analyze content to determine the most appropriate project and section

## Quick Reference

```bash
# Search archives (ALWAYS search first)
./ai.archives/run_archives.sh search "your search query"

# Add to archives (write directly to the archives directory)
# Generate timestamp for the filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
# Analyze content to determine appropriate project and section
PROJECT="..."  # Determine based on content: frontend, backend, or shared
SECTION="..."  # Determine based on content: setup, errors, fixes, etc.
FILENAME="${PROJECT}_${SECTION}_${TIMESTAMP}.md"
mkdir -p ./ai.archives/archives/$PROJECT/$SECTION
# Write content to the file
echo "# Title" > ./ai.archives/archives/$PROJECT/$SECTION/$FILENAME
echo "" >> ./ai.archives/archives/$PROJECT/$SECTION/$FILENAME
echo "Content goes here" >> ./ai.archives/archives/$PROJECT/$SECTION/$FILENAME
```

## Content Guidelines

- **SEARCH FIRST**: When archives are mentioned, search before taking other actions
- **ADD WHEN REQUESTED**: Only add content when explicitly requested
- **INTELLIGENT CATEGORIZATION**: 
  - Analyze the content to determine the most appropriate project and section
  - Use `frontend` for UI/client-side content (React, CSS, UI components, etc.)
  - Use `backend` for server-side content (APIs, databases, server logic, etc.)
  - Use `shared` for cross-cutting concerns (authentication, configuration, architecture, etc.)
  - Create appropriate sections based on content type (setup, errors, fixes, architecture, etc.)
  - If content spans multiple areas, choose the most dominant theme or use `shared`
- **DESCRIPTIVE SECTIONS**: Create or use sections that clearly describe the content type:
  - `setup`: Installation, configuration, environment setup
  - `errors`: Error messages, debugging, troubleshooting
  - `fixes`: Solutions, workarounds, bug fixes
  - `architecture`: System design, patterns, structure
  - `security`: Authentication, authorization, data protection
  - `performance`: Optimization, scaling, efficiency
  - `testing`: Testing strategies, frameworks, examples
  - `deployment`: CI/CD, hosting, containerization
  - Feel free to create new sections as appropriate for the content
- **PRESERVE FORMATTING**: Maintain all markdown formatting, code blocks, and structure when archiving

## Updating Rules

1. When asked to "add to the rules" or "update the rules":
   - Edit `/ai.archives/custom-rules.md`
   - Run `./ai.archives/run_archives.sh generate`
   - The script will handle copying to the project

## Server Issues

If you get connection errors when searching:
```bash
./ai.archives/run_archives.sh server  # Start the server
```
