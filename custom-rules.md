# AI ARCHIVES USAGE RULES

## Core Operations

- **NEVER USE FILE TOOLS FOR ARCHIVES**: Always use the wrapper script.
- **ALWAYS USE WRAPPER SCRIPT**: `./ai.archives/run_archives.sh` for all operations.
- **NEVER EDIT .cursorrules DIRECTLY**: This file is auto-generated.

## Quick Reference

```bash
./ai.archives/run_archives.sh search "query"    # Search archives
./ai.archives/run_archives.sh add project section "Title" "Content"   # Add entry
./ai.archives/run_archives.sh server            # Start server if needed
```

## Key Guidelines

- **SEARCH FIRST**: When user mentions "archives" or "check archives", search immediately.
- **ADD ONLY WHEN REQUESTED**: Only add content when user explicitly requests it.
- **CATEGORIZE PROPERLY**: Use appropriate project (frontend/backend/shared) and section.
- **SERVER ISSUES**: If connection refused, start the server with `./ai.archives/run_archives.sh server`.

## Updating Rules

- **EDIT CUSTOM RULES**: When user says "add to the rules" or "update the rules", edit `/ai.archives/custom-rules.md`.
- **REGENERATE CURSORRULES**: After editing, run `./ai.archives/run_archives.sh generate` to create a new .cursorrules file.
- **COPY TO REPO**: Copy the new .cursorrules file to the user's project repo to replace the old one.
