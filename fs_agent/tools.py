# fs_agent/tools.py

import os
import json
from datetime import datetime
from pathlib import Path

# --- Security Configuration ---
ALLOWED_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.log', '.html', '.css', '.sh', '.sql'}
MAX_FILE_SIZE = 1024 * 1024  # 1MB limit
FORBIDDEN_PATHS = {'/etc', '/bin', '/usr', '/sys', '/proc', '/root', '/boot'}
BACKUP_DIR = '.fs-agent-backups'

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


# --- Tool 3: Write File Contents ---

def _validate_write_path(path: str) -> dict:
    """
    Validate a file path for write operations.
    
    Returns:
        dict: {"valid": bool, "error": str or None}
    """
    # Check for path traversal
    if ".." in path:
        return {"valid": False, "error": "Path traversal is not allowed."}
    
    # Check for absolute paths to sensitive directories
    abs_path = os.path.abspath(path)
    for forbidden in FORBIDDEN_PATHS:
        if abs_path.startswith(forbidden):
            return {"valid": False, "error": f"Access to system directory '{forbidden}' is denied."}
    
    # Check for hidden files (starting with .)
    filename = os.path.basename(path)
    if filename.startswith('.') and filename not in {'.gitignore', '.env.example', '.editorconfig'}:
        return {"valid": False, "error": "Writing to hidden files is not allowed."}
    
    # Check file extension
    file_ext = Path(path).suffix.lower()
    if file_ext and file_ext not in ALLOWED_EXTENSIONS:
        return {"valid": False, "error": f"File extension '{file_ext}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}
    
    return {"valid": True, "error": None}


def _create_backup(file_path: str) -> str:
    """
    Create a backup of an existing file.
    
    Returns:
        str: Path to the backup file
    """
    # Create backup directory if it doesn't exist
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    backup_name = f"{filename}.backup.{timestamp}"
    backup_path = backup_dir / backup_name
    
    # Copy the file
    import shutil
    shutil.copy2(file_path, backup_path)
    
    return str(backup_path)


def write_file_contents(path: str, content: str, overwrite: bool = False):
    """
    Write content to a file with comprehensive security checks.
    
    Args:
        path (str): The path where to write the file
        content (str): The content to write
        overwrite (bool): Whether to overwrite existing files
    
    Returns:
        A JSON string containing the operation result or error message.
    """
    print(f"[Tool: Running 'write' to file: '{path}']")
    
    # Validate the path
    validation = _validate_write_path(path)
    if not validation["valid"]:
        return json.dumps({"error": validation["error"], "error_type": "invalid_path"})
    
    # Check content size
    content_size = len(content.encode('utf-8'))
    if content_size > MAX_FILE_SIZE:
        return json.dumps({
            "error": f"Content is too large ({content_size} bytes). Max size is {MAX_FILE_SIZE // 1024}KB.",
            "error_type": "size_exceeded"
        })
    
    try:
        file_exists = os.path.exists(path)
        backup_path = None
        
        # Handle existing file
        if file_exists:
            if not overwrite:
                return json.dumps({
                    "error": f"File '{path}' already exists. Set overwrite=true to replace it.",
                    "error_type": "file_exists",
                    "suggested_action": "Use overwrite=true parameter or choose a different filename"
                })
            
            # Create backup before overwriting
            try:
                backup_path = _create_backup(path)
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to create backup: {str(e)}",
                    "error_type": "backup_failed"
                })
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Prepare success response
        response = {
            "success": True,
            "path": path,
            "size_bytes": content_size,
            "operation": "overwrite" if file_exists else "create"
        }
        
        if backup_path:
            response["backup_created"] = backup_path
        
        return json.dumps(response)
    
    except PermissionError:
        return json.dumps({
            "error": f"Permission denied writing to '{path}'. Check file/directory permissions.",
            "error_type": "permission_denied"
        })
    except OSError as e:
        if "No space left on device" in str(e):
            return json.dumps({
                "error": "Insufficient disk space to write file.",
                "error_type": "disk_full"
            })
        return json.dumps({
            "error": f"OS error: {str(e)}",
            "error_type": "os_error"
        })
    except Exception as e:
        return json.dumps({
            "error": f"An unexpected error occurred: {str(e)}",
            "error_type": "unexpected"
        })


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
    },
    {
        "schema": {
            'type': 'function',
            'function': {
                'name': 'write_file_contents',
                'description': 'Create a new file or update an existing file with specified content. IMPORTANT: Always ask user for confirmation before overwriting existing files.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path': {
                            'type': 'string', 
                            'description': 'Path where to write the file (relative paths only)'
                        },
                        'content': {
                            'type': 'string', 
                            'description': 'Content to write to the file'
                        },
                        'overwrite': {
                            'type': 'boolean', 
                            'description': 'Whether to overwrite existing files (requires user confirmation)',
                            'default': False
                        }
                    },
                    'required': ['path', 'content']
                },
            },
        },
        "function": write_file_contents
    }
]
