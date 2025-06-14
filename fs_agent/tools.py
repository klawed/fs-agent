# fs_agent/tools.py

import os
import json

def list_directory_contents(path: str = "."):
    """
    Lists the contents (files and directories) of a specified directory path.
    
    Args:
        path (str): The path to the directory to inspect. Defaults to the current directory ('.').
    
    Returns:
        A JSON string containing a list of items in the directory, or an error message.
    """
    print(f"[Tool: Running 'ls' on path: '{path}']")
    try:
        # Basic security: prevent traversing up to root, etc. In a real app, this needs to be much more robust.
        if ".." in path:
            return json.dumps({"error": "Path traversal is not allowed."})
            
        # Get the list of files and directories
        items = os.listdir(path)
        
        # Return the list as a JSON string
        return json.dumps({"path": path, "contents": items})

    except FileNotFoundError:
        return json.dumps({"error": f"The path '{path}' was not found."})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
