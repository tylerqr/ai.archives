#!/bin/bash
# archive_scratchpad.sh
#
# This script archives the entire content of the scratchpad.md file
# and then resets it to the default empty state.
#
# Usage: ./archive_scratchpad.sh <project> <section> "Title"

# Check if arguments are provided
if [ $# -lt 3 ]; then
    echo "Usage: ./archive_scratchpad.sh <project> <section> \"Title\""
    echo "Example: ./archive_scratchpad.sh shared fixes \"NativeWind Removal - Complete Migration Guide\""
    exit 1
fi

PROJECT="$1"
SECTION="$2"
TITLE="$3"

# Check if scratchpad.md exists
if [ ! -f "./ai.archives/scratchpad.md" ] && [ ! -f "./scratchpad.md" ]; then
    echo "Error: scratchpad.md not found in ./ai.archives/ or current directory."
    exit 1
fi

# Determine the path to scratchpad.md
SCRATCHPAD_PATH=""
if [ -f "./ai.archives/scratchpad.md" ]; then
    SCRATCHPAD_PATH="./ai.archives/scratchpad.md"
elif [ -f "./scratchpad.md" ]; then
    SCRATCHPAD_PATH="./scratchpad.md"
fi

echo "Archiving content from $SCRATCHPAD_PATH..."

# Read scratchpad content
SCRATCHPAD_CONTENT=$(cat "$SCRATCHPAD_PATH")

# Add to archives
if [ -f "./ai.archives/run_archives.sh" ]; then
    ./ai.archives/run_archives.sh add "$PROJECT" "$SECTION" "$TITLE" "$SCRATCHPAD_CONTENT"
elif [ -f "./run_archives.sh" ]; then
    ./run_archives.sh add "$PROJECT" "$SECTION" "$TITLE" "$SCRATCHPAD_CONTENT"
else
    echo "Error: run_archives.sh not found in ./ai.archives/ or current directory."
    exit 1
fi

# Reset scratchpad to default empty state
cat > "$SCRATCHPAD_PATH" << 'EOF'
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

echo "Scratchpad has been archived and reset to default empty state."
echo "Archive location: $PROJECT/$SECTION/$TITLE" 