# AI Archives REST API

A fast, simple REST API for AI agents to interact with the AI Archives system. This solution eliminates the Python environment hassles, reduces tool call overhead, and makes it easy for AI agents to search, read, and update archives.

## Features

- **Simple HTTP API**: No environment activation or complex command line arguments needed
- **AI-Optimized Responses**: Formatted specifically for AI agent consumption
- **Fast Search**: Quick access to archives content
- **Custom Rules Management**: Easy updating and regeneration of custom rules
- **Multiple Access Methods**: REST API, Python client library, or simplified command-line wrapper

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

### 2. Start the Server

```bash
python ai_archives.py server
```

The server will start on http://localhost:5000 by default.

### 3. Use the API

You can interact with the API in three ways:

#### A. Direct HTTP Requests

```bash
# Search archives
curl "http://localhost:5000/search?query=authentication"

# Add to archives
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -d '{"project":"frontend", "section":"errors", "content":"Error message", "title":"Error Title"}'
```

#### B. Python Client Library

```python
from archives_client import ArchivesClient

client = ArchivesClient()

# Search archives
results = client.quick_search("authentication", format_type="text")
print(results)

# Add to archives
client.add("frontend", "errors", "Error message", "Error Title")
```

#### C. Command-line Wrapper

```bash
# Search archives
python ai_archives.py search "authentication"

# Add to archives
python ai_archives.py add frontend errors "Error message" "Error Title"

# List all projects
python ai_archives.py projects

# Update a rule
python ai_archives.py rule-add custom_rule "# Custom Rule Content"

# Generate cursorrules
python ai_archives.py generate
```

## API Endpoints

### Search

- `GET /search?query=<query>&project=<project>`
- `GET /quick-search?query=<query>&project=<project>&format=<format>`

### Add Content

- `POST /add` (JSON body: project, section, content, title)

### Rules Management

- `GET /rules`
- `POST /rules` (JSON body: name, content)
- `POST /generate-cursorrules` (JSON body: output_path)

### Discovery

- `GET /list-projects`
- `GET /list-sections?project=<project>`

## For AI Agents

When using this system from an AI agent, follow these simple steps:

1. First, start the server (only needed once):
   ```bash
   python ai_archives.py server
   ```

2. Then, use the client wrapper for all operations:
   ```bash
   # For searching
   python ai_archives.py search "your search query"
   
   # For adding content (only when explicitly requested by user)
   python ai_archives.py add frontend errors "Error message" "Error Title"
   ```

This approach is much simpler and faster than the previous method using the Python virtual environment. 