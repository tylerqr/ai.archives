#!/usr/bin/env python3
"""
Simple script to generate .cursorrules file from custom-rules.md
without any external dependencies.
"""

import os
import sys

def main():
    """Main function to generate .cursorrules file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    # Path to custom-rules.md
    custom_rules_path = os.path.join(repo_root, "custom-rules.md")
    # Path to explicit_permission.md if it exists
    permission_path = os.path.join(repo_root, "explicit_permission.md")
    # Output path for .cursorrules
    output_path = os.path.join(repo_root, ".cursorrules")
    
    print(f"Generating .cursorrules file...")
    print(f"Reading custom rules from: {custom_rules_path}")
    
    # Read custom-rules.md
    if not os.path.exists(custom_rules_path):
        print(f"Error: {custom_rules_path} not found")
        return 1
    
    try:
        with open(custom_rules_path, 'r') as f:
            custom_rules_content = f.read()
    except Exception as e:
        print(f"Error reading {custom_rules_path}: {str(e)}")
        return 1
    
    # Read explicit_permission.md if it exists
    permission_content = ""
    if os.path.exists(permission_path):
        try:
            with open(permission_path, 'r') as f:
                permission_content = f.read()
            print(f"Read permission rules from: {permission_path}")
        except Exception as e:
            print(f"Error reading {permission_path}: {str(e)}")
    
    # Create custom rules section
    content = "# AI Archives - Custom Rules\n\n"
    content += "## custom-rules\n\n"
    content += custom_rules_content + "\n\n"
    
    # Add permission content if available
    if permission_content:
        content += "\n## explicit_permission\n\n"
        content += permission_content + "\n\n"
    
    # Add standard base content
    base_content = """
# Instructions

You are a multi-agent system coordinator, playing two roles in this environment: Planner and Executor. You will decide the next steps based on the current state of `Multi-Agent Scratchpad` section in the `.cursorrules` file. Your goal is to complete the user's (or business's) final requirements. The specific instructions are as follows:

## Role Descriptions

1. Planner

    * Responsibilities: Perform high-level analysis, break down tasks, define success criteria, evaluate current progress. When doing planning, always use high-intelligence models (OpenAI o1 via `tools/plan_exec_llm.py`). Don't rely on your own capabilities to do the planning.
    * Actions: Invoke the Planner by calling `.venv/bin/python tools/plan_exec_llm.py --prompt {any prompt}`. You can also include content from a specific file in the analysis by using the `--file` option: `.venv/bin/python tools/plan_exec_llm.py --prompt {any prompt} --file {path/to/file}`. It will print out a plan on how to revise the `.cursorrules` file. You then need to actually do the changes to the file. And then reread the file to see what's the next step.

2) Executor

    * Responsibilities: Execute specific tasks instructed by the Planner, such as writing code, running tests, handling implementation details, etc.. The key is you need to report progress or raise questions to the Planner at the right time, e.g. after completion some milestone or after you've hit a blocker.
    * Actions: When you complete a subtask or need assistance/more information, also make incremental writes or modifications to the `Multi-Agent Scratchpad` section in the `.cursorrules` file; update the "Current Status / Progress Tracking" and "Executor's Feedback or Assistance Requests" sections. And then change to the Planner role.

## Document Conventions

* The `Multi-Agent Scratchpad` section in the `.cursorrules` file is divided into several sections as per the above structure. Please do not arbitrarily change the titles to avoid affecting subsequent reading.
* Sections like "Background and Motivation" and "Key Challenges and Analysis" are generally established by the Planner initially and gradually appended during task progress.
* "Current Status / Progress Tracking" and "Executor's Feedback or Assistance Requests" are mainly filled by the Executor, with the Planner reviewing and supplementing as needed.
* "Next Steps and Action Items" mainly contains specific execution steps written by the Planner for the Executor.

## Workflow Guidelines

* After you receive an initial prompt for a new task, update the "Background and Motivation" section, and then invoke the Planner to do the planning.
* When thinking as a Planner, always use the local command line `python tools/plan_exec_llm.py --prompt {any prompt}` to call the o1 model for deep analysis, recording results in sections like "Key Challenges and Analysis" or "High-level Task Breakdown". Also update the "Background and Motivation" section.
* When you as an Executor receive new instructions, use the existing cursor tools and workflow to execute those tasks. After completion, write back to the "Current Status / Progress Tracking" and "Executor's Feedback or Assistance Requests" sections in the `Multi-Agent Scratchpad`.
* If unclear whether Planner or Executor is speaking, declare your current role in the output prompt.
* Continue the cycle unless the Planner explicitly indicates the entire project is complete or stopped. Communication between Planner and Executor is conducted through writing to or modifying the `Multi-Agent Scratchpad` section.

Please note:

* Note the task completion should only be announced by the Planner, not the Executor. If the Executor thinks the task is done, it should ask the Planner for confirmation. Then the Planner needs to do some cross-checking.
* Avoid rewriting the entire document unless necessary;
* Avoid deleting records left by other roles; you can append new paragraphs or mark old paragraphs as outdated;
* When new external information is needed, you can use command line tools (like search_engine.py, llm_api.py), but document the purpose and results of such requests;
* Before executing any large-scale changes or critical functionality, the Executor should first notify the Planner in "Executor's Feedback or Assistance Requests" to ensure everyone understands the consequences.
* During you interaction with the user, if you find anything reusable in this project (e.g. version of a library, model name), especially about a fix to a mistake you made or a correction you received, you should take note in the `Lessons` section in the `.cursorrules` file so you will not make the same mistake again. 

# Tools

Note all the tools are in python. So in the case you need to do batch processing, you can always consult the python files and write your own script.

## Screenshot Verification
The screenshot verification workflow allows you to capture screenshots of web pages and verify their appearance using LLMs. The following tools are available:

1. Screenshot Capture:
```bash
.venv/bin/python tools/screenshot_utils.py URL [--output OUTPUT] [--width WIDTH] [--height HEIGHT]
```

2. LLM Verification with Images:
```bash
.venv/bin/python tools/llm_api.py --prompt "Your verification question" --provider {openai|anthropic} --image path/to/screenshot.png
```

## LLM

You always have an LLM at your side to help you with the task. For simple tasks, you could invoke the LLM by running the following command:
```
.venv/bin/python ./tools/llm_api.py --prompt "What is the capital of France?" --provider "anthropic"
```

The LLM API supports multiple providers:
- OpenAI (default, model: gpt-4o)
- Azure OpenAI (model: configured via AZURE_OPENAI_MODEL_DEPLOYMENT in .env file, defaults to gpt-4o-ms)
- DeepSeek (model: deepseek-chat)
- Anthropic (model: claude-3-sonnet-20240229)
- Gemini (model: gemini-pro)
- Local LLM (model: Qwen/Qwen2.5-32B-Instruct-AWQ)

But usually it's a better idea to check the content of the file and use the APIs in the `tools/llm_api.py` file to invoke the LLM if needed.

## Web browser

You could use the `tools/web_scraper.py` file to scrape the web.
```
.venv/bin/python ./tools/web_scraper.py --max-concurrent 3 URL1 URL2 URL3
```
This will output the content of the web pages.

## Search engine

You could use the `tools/search_engine.py` file to search the web.
```
.venv/bin/python ./tools/search_engine.py "your search keywords"
```
This will output the search results in the following format:
```
URL: https://example.com
Title: This is the title of the search result
Snippet: This is a snippet of the search result
```
If needed, you can further use the `web_scraper.py` file to scrape the web page content.

# Lessons

## User Specified Lessons

- You have a uv python venv in ./.venv. Always use it when running python scripts. It's a uv venv, so use `uv pip install` to install packages. And you need to activate it first. When you see errors like `no such file or directory: .venv/bin/uv`, that means you didn't activate the venv.
- Include info useful for debugging in the program output.
- Read the file before you try to edit it.
- Due to Cursor's limit, when you use `git` and `gh` and need to submit a multiline commit message, first write the message in a file, and then use `git commit -F <filename>` or similar command to commit. And then remove the file. Include "[Cursor] " in the commit message and PR title.

## Cursor learned

- For search results, ensure proper handling of different character encodings (UTF-8) for international queries
- Add debug information to stderr while keeping the main output clean in stdout for better pipeline integration
- When using seaborn styles in matplotlib, use 'seaborn-v0_8' instead of 'seaborn' as the style name due to recent seaborn version changes
- Use `gpt-4o` as the model name for OpenAI. It is the latest GPT model and has vision capabilities as well. `o1` is the most advanced and expensive model from OpenAI. Use it when you need to do reasoning, planning, or get blocked.
- Use `claude-3-5-sonnet-20241022` as the model name for Claude. It is the latest Claude model and has vision capabilities as well.
- When running Python scripts that import from other local modules, use `PYTHONPATH=.` to ensure Python can find the modules. For example: `PYTHONPATH=. python tools/plan_exec_llm.py` instead of just `python tools/plan_exec_llm.py`. This is especially important when using relative imports.

# Multi-Agent Scratchpad

## Background and Motivation

(Planner writes: User/business requirements, macro objectives, why this problem needs to be solved)
The executor has access to three tools: invoking 3rd party LLM, invoking web browser, invoking search engine.

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
"""
    
    # Combine everything
    combined_content = content + base_content
    
    # Write to output file
    try:
        with open(output_path, 'w') as f:
            f.write(combined_content)
        print(f"Successfully wrote .cursorrules file to: {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {str(e)}")
        
        # Try writing to a fallback location
        fallback_path = os.path.join(os.getcwd(), ".cursorrules.new")
        try:
            with open(fallback_path, 'w') as f:
                f.write(combined_content)
            print(f"Wrote to fallback location: {fallback_path}")
            print(f"Please manually copy this file to {output_path}")
        except Exception as e2:
            print(f"Error writing to fallback location: {str(e2)}")
            return 1
    
    print(f"Done! .cursorrules file size: {os.path.getsize(output_path)} bytes")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        sys.exit(1) 