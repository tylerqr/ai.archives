#!/usr/bin/env python3
"""
AI Archives REST API Server

A simple, fast REST API for AI agents to interact with the AI Archives system.
Provides endpoints for reading, searching, writing to archives and managing custom rules.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path so we can import the archives module
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
sys.path.append(repo_root)

# Import archives functionality
from archives_api import get_archives_api

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get archives API instance
api = get_archives_api()

@app.route('/ping', methods=['GET'])
def ping():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "AI Archives REST API is running"})

@app.route('/search', methods=['GET'])
def search_archives():
    """
    Search the archives
    
    Query parameters:
    - query: Search query (required)
    - project: Project to search in (optional)
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing required parameter: query"}), 400
    
    project = request.args.get('project')
    results = api.search_archives(query, project)
    
    # Format results in an AI-friendly way
    formatted_results = {
        "query": query,
        "count": len(results),
        "results": results
    }
    
    return jsonify(formatted_results)

@app.route('/quick-search', methods=['GET'])
def quick_search():
    """
    Optimized search endpoint for AI agents
    
    Query parameters:
    - query: Search query (required)
    - project: Project to search in (optional)
    - format: Response format (text or json, default: json)
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing required parameter: query"}), 400
    
    project = request.args.get('project')
    format_type = request.args.get('format', 'json')
    
    results = api.search_archives(query, project)
    
    if format_type == 'text':
        # Format as plain text for direct inclusion in AI responses
        if not results:
            return f"No archives found for query: '{query}'. The information you're looking for is not in the archives."
        
        output = f"ARCHIVES SEARCH RESULTS FOR: '{query}'\n"
        output += "=" * 80 + "\n\n"
        output += f"Found {len(results)} relevant entries in the archives:\n\n"
        
        for i, result in enumerate(results, 1):
            project_name = result.get('project', 'unknown')
            title = result.get('title', 'Untitled Entry')
            snippet = result.get('snippet', '').strip()
            file_path = result.get('file', '')
            
            output += f"RESULT {i}: {title}\n"
            output += "-" * 80 + "\n"
            output += f"Project: {project_name}\n"
            output += f"Location: {file_path}\n\n"
            output += f"CONTENT PREVIEW:\n{snippet}\n\n"
        
        return output
    else:
        # Format as JSON
        formatted_results = {
            "query": query,
            "count": len(results),
            "results": results
        }
        
        return jsonify(formatted_results)

@app.route('/add', methods=['POST'])
def add_to_archives():
    """
    Add content to archives
    
    JSON body parameters:
    - project: Project name (required)
    - section: Section name (required)
    - content: Content to add (required)
    - title: Entry title (optional)
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    required_fields = ['project', 'section', 'content']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        file_path = api.add_to_archives(
            project=data['project'],
            section=data['section'],
            content=data['content'],
            title=data.get('title')
        )
        
        return jsonify({
            "status": "success",
            "message": "Content added to archives",
            "file": file_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rules', methods=['GET'])
def get_rules():
    """Get all custom rules"""
    try:
        rules = api.get_custom_rules()
        return jsonify({
            "count": len(rules),
            "rules": rules
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rules', methods=['POST'])
def add_rule():
    """
    Add or update a custom rule
    
    JSON body parameters:
    - name: Rule name (required)
    - content: Rule content (required)
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    required_fields = ['name', 'content']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        file_path = api.update_custom_rule(
            rule_content=data['content'],
            rule_name=data['name']
        )
        
        return jsonify({
            "status": "success",
            "message": f"Rule '{data['name']}' updated",
            "file": file_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-cursorrules', methods=['POST'])
def generate_cursorrules():
    """Generate combined cursorrules file"""
    try:
        output_path = request.json.get('output_path') if request.json else None
        file_path = api.generate_combined_cursorrules(output_path)
        
        return jsonify({
            "status": "success",
            "message": "Generated combined cursorrules file",
            "file": file_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list-projects', methods=['GET'])
def list_projects():
    """List all available projects"""
    try:
        # Access the config directly from the manager
        projects = api.manager.config["settings"]["archive_structure"]["projects"]
        return jsonify({
            "count": len(projects),
            "projects": projects
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list-sections', methods=['GET'])
def list_sections():
    """
    List all sections for a project
    
    Query parameters:
    - project: Project name (required)
    """
    project = request.args.get('project')
    if not project:
        return jsonify({"error": "Missing required parameter: project"}), 400
    
    try:
        # Get sections for the specified project
        project_dir = os.path.join(api.manager.projects_dir, project)
        if not os.path.exists(project_dir):
            return jsonify({"error": f"Project not found: {project}"}), 404
        
        sections = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]
        
        return jsonify({
            "project": project,
            "count": len(sections),
            "sections": sections
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run with 0.0.0.0 to make it externally visible if needed
    app.run(host='0.0.0.0', port=port, debug=True) 