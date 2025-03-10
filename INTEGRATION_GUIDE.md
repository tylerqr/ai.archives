# AI Archives Integration Guide

This guide explains how to integrate the AI Archives system with your projects.

## Directory Structure

The AI Archives system consists of two repositories:

1. **Main Repository (ai.archives)**: Contains the core code and integration scripts.
2. **Data Repository (ai.archives.reko)**: Contains the actual archives data, custom rules, and other user-specific content.

When integrating with your projects, you should link **only the data repository**, not the main repository. The main repository is used only for running scripts and managing the archives.

## Setup Process

The setup process involves these key steps:

1. Clone both repositories
2. Initialize the data repository
3. Link the data repository to your projects
4. Generate the combined .cursorrules file

### Step 1: Clone the Repositories

Clone both the main repository and data repository:

```bash
git clone https://github.com/your-username/ai.archives.git
git clone https://github.com/your-username/ai.archives.reko.git
```

### Step 2: Initialize the Data Repository

Run the setup script from the main repository:

```bash
cd ai.archives
python scripts/setup.py
```

This will initialize the data repository with the necessary directory structure and configuration.

### Step 3: Link to Your Projects

During setup, you'll be asked if you want to link the archives to your projects. Say yes and provide the paths to your projects.

The setup will:
- Create a symlink to the data repository in your project (recommended)
- Copy the combined .cursorrules file to your project

Note: We no longer recommend creating a symlink to the main repository. Only the data repository should be linked to your projects.

### Step 4: Generate the Combined .cursorrules File

The setup process will automatically generate the combined .cursorrules file, but you can regenerate it anytime:

```bash
cd ai.archives
python scripts/integrate_cursorrules.py
```

## Custom Rules

Custom rules are now stored in a single file in the data repository at `archives/custom_rules/reko-rules.md`. This makes it easier to review and edit them via the file explorer in Cursor.

To add a custom rule:

```bash
cd ai.archives
python scripts/archives_cli.py rule add --name=rule_name --content="Rule content"
```

This will add the rule to the reko-rules.md file under a section with the specified name.

After adding a rule, regenerate the combined .cursorrules file and copy it to your projects:

```bash
python scripts/integrate_cursorrules.py
cp ../ai.archives.reko/.cursorrules /path/to/your/project/
```

## Directory Structure Cleanup

If you've been using the previous approach with symlinks to both repositories, you can clean up your project directories:

```bash
cd ai.archives
python scripts/cleanup_directories.py --project=/path/to/your/project
```

This will remove the symlink to the main repository while keeping the symlink to the data repository.

## Combined File Structure

The combined .cursorrules file now has this structure:

1. **AI Archives System Reference**: Brief instructions for interacting with the archives system
2. **Custom Rules**: Your custom rules from the data repository
3. **Base Content**: The original content from the base .cursorrules file

This places your custom rules at the top, making them more prominent and ensuring they take precedence.

## Archives Usage Instructions

Detailed instructions for using the archives system can be found in `archives/custom_rules/how-to-use-archive-system.md` in the main repository.

The AI agent will be instructed to refer to these instructions when asked to interact with the archives system. 