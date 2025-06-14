# fs_agent/tools.py

import os
import json

# --- Tool 1: List Directory Contents ---

def list_directory_contents(path: str = "."):
    """
    Lists the contents (files and directories) of a specified directory path.
    
    Args:
        path (str): The path to the directory to inspect. Defaults to the current directory ('.').
    
    Returns:
        A JSON string containing a list of items in the directory, or an error message.
    """
    print(f"[Tool: Running 'ls' on path: '{path}']")
    # Basic security: prevent traversing up to root, etc.
    if ".." in path:
        return json.dumps({"error": "Path traversal is not allowed."})
            
    try:
        items = os.listdir(path)
        return json.dumps({"path": path, "contents": items})
    except FileNotFoundError:
        return json.dumps({"error": f"The path '{path}' was not found."})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})


# --- Tool 2: Read File Contents ---

def read_file_contents(path: str):
    """
    Reads and returns the content of a specified text file.
    
    Args:
        path (str): The full path to the file to read.
    
    Returns:
        A JSON string containing the file's content, or an error message.
    """
    print(f"[Tool: Running 'read' on file: '{path}']")
    
    # SECURITY: More stringent checks for reading files
    if ".." in path:
        return json.dumps({"error": "Path traversal is not allowed."})
    
    # SECURITY: Prevent reading from sensitive or system directories.
    # This is a basic example; a real app would need a more robust allow/deny list.
    if path.startswith(('/', '~', '/etc')):
        return json.dumps({"error": "Access to absolute or sensitive paths is denied."})

    try:
        # SECURITY: Check file size before reading to avoid memory issues.
        file_size = os.path.getsize(path)
        if file_size > 100 * 1024:  # 100 KB limit
            return json.dumps({"error": f"File is too large ({file_size} bytes). Max size is 100KB."})

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return json.dumps({"path": path, "content": content})

    except FileNotFoundError:
        return json.dumps({"error": f"The file '{path}' was not found."})
    except UnicodeDecodeError:
        return json.dumps({"error": f"Cannot read the file '{path}'. It may be a binary file, not text."})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})


# --- Master Tool Definitions ---
# This is the extensible part. We create a list where each entry defines a tool.
# The agent will load this list automatically.

ALL_TOOLS = [
    {
        "schema": {
            'type': 'function',
            'function': {
                'name': 'list_directory_contents',
                'description': 'List the files and folders in a specified directory path.',
                'parameters': { 'type': 'object', 'properties': {'path': {'type': 'string'}}},
            },
        },
        "function": list_directory_contents
    },
    {
        "schema": {
            'type': 'function',
            'function': {
                'name': 'read_file_contents',
                'description': 'Reads and returns the contents of a specified text file.',
                'parameters': {
                    'type': 'object',
                    'properties': {'path': {'type': 'string', 'description': 'The path to the file.'}},
                    'required': ['path']
                },
            },
        },
        "function": read_file_contents
    }
]
