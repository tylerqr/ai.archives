# AI Archives Usage Rules

## Core Rules

- **ALWAYS USE WRAPPER SCRIPT**: Use `./ai.archives/run_archives.sh` for all archive operations
- **NEVER EDIT .cursorrules DIRECTLY**: This file is auto-generated
- **SEARCH BEFORE ADDING**: Always search archives before adding new content to avoid duplicates
- **ARCHIVE ENTIRE SCRATCHPAD**: When archiving, always include the entire scratchpad content

## Quick Reference

```bash
# Search archives (ALWAYS search first)
./ai.archives/run_archives.sh search "your search query"

# Add to archives (only when explicitly requested)
./ai.archives/run_archives.sh add <project> <section> "Title" "Content"

# Projects: frontend, backend, shared
# Sections: setup, errors, fixes, architecture, etc.
```

## Content Guidelines

- **SEARCH FIRST**: When archives are mentioned, search before taking other actions
- **ADD WHEN REQUESTED**: Only add content when explicitly requested
- **PROPER CATEGORIZATION**: 
  - Use `frontend` for UI/client-side content
  - Use `backend` for server-side content
  - Use `shared` for cross-cutting concerns
- **CLEAR SECTIONS**: Use descriptive section names (setup, errors, fixes, etc.)
- **PRESERVE FORMATTING**: Maintain all markdown formatting, code blocks, and structure when archiving
- **COMPLETE CONTENT**: When archiving from scratchpad, include the ENTIRE content of the scratchpad.md file
- **RESET SCRATCHPAD**: After archiving, reset the scratchpad to its default empty state for the next task

## Archiving Process

1. When asked to "add to archives" or similar:
   - First check if there's content in the scratchpad.md file
   - If yes, use the ENTIRE content of scratchpad.md as the "Content" parameter
   - Use a descriptive title that summarizes the content
   - After successful archiving, reset the scratchpad.md to its default empty state
   - If no scratchpad content exists, use relevant information from the conversation

2. For archiving from scratchpad:
```bash
# Read scratchpad content and add to archives
SCRATCHPAD_CONTENT=$(cat ./ai.archives/scratchpad.md)
./ai.archives/run_archives.sh add <project> <section> "Title" "$SCRATCHPAD_CONTENT"

# Reset scratchpad after archiving
cat > ./ai.archives/scratchpad.md << 'EOF'
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

## Updating Rules

1. When asked to "add to the rules" or "update the rules":
   - Edit `/ai.archives/custom-rules.md`
   - Run `./ai.archives/run_archives.sh generate`
   - The script will handle copying to the project

## Server Issues

If you get connection errors:
```bash
./ai.archives/run_archives.sh server  # Start the server
```
