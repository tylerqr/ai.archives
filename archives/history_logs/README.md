# History Logs

This directory contains logs of interactions with the AI Archives system. Each log records details about an action performed by an AI agent, including the reasoning behind decisions and the rules that were followed.

## Purpose

The primary purpose of history logging is to provide visibility into how AI agents are using the archives system and to aid in debugging and improving the system over time. History logs help users understand:

1. What changes were made to the archives
2. Why specific decisions were made (e.g., creating a new file vs. appending to an existing one)
3. How AI agents interpreted and applied the archive system rules
4. The thought process behind archive organization and categorization

## Log Format

Each history log is stored as a markdown file with a filename pattern of `YYYY-MM-DD_HH-MM-SS_action.md`. The content of each log follows this structure:

```markdown
# Archive Interaction Log - action_name

**Timestamp**: YYYY-MM-DD HH:MM:SS
**Action**: action_name

## Details

**parameter1**: value1
**parameter2**: value2
...

## Decision Explanation

Detailed explanation of the decisions made during this interaction, including why a new file was created or an existing file was appended.

## Rules Followed

- Rule 1 that influenced the decision
- Rule 2 that influenced the decision
...
```

## Managing History Logs

You can manage history logs using the following commands:

```bash
# View recent history logs
python scripts/archives_cli.py history list

# Search through history logs
python scripts/archives_cli.py history search "query"

# View a specific history log
python scripts/archives_cli.py history view <log_file>

# Enable/disable history logging
python scripts/archives_cli.py history toggle --enable
python scripts/archives_cli.py history toggle --disable

# Clean up old logs
python scripts/archives_cli.py history cleanup
python scripts/archives_cli.py history cleanup --days 15 --force
```

## Retention Policy

By default, history logs are kept for 30 days. You can adjust this setting in the configuration file:

```json
"history_logging": {
  "enabled": true,
  "log_dir": "archives/history_logs",
  "max_retention_days": 30
}
``` 