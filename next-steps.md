### The Plan:
1.  **Refactor `tools.py`:** We'll define a master list of tools, where each tool includes both its function *and* its API schema.
2.  **Add the `read_file` Tool:** We'll implement the new function in `tools.py` with necessary security checks.
3.  **Update `agent.py`:** The agent will now dynamically load its capabilities from `tools.py`.
4.  **Update the System Prompt:** We'll tell the model about its new superpower.

---

### Step 1: Upgrade `fs_agent/tools.py`

This is the biggest change. We're turning this file into a self-contained tool library. Replace the entire contents of `fs_agent/tools.py` with the following:

```python
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
```

### Step 2: Update `fs_agent/agent.py` to be Extensible

Now, we'll modify the agent to dynamically use the `ALL_TOOLS` list. This makes it much cleaner. Replace the contents of `fs_agent/agent.py` with this:

```python
# fs_agent/agent.py

import ollama
import json
from .tools import ALL_TOOLS # Import the master tool list

# --- Dynamic Tool Configuration ---
# Build the tools payload for the API from our master list
API_TOOLS = [tool['schema'] for tool in ALL_TOOLS]

# Build a mapping from tool name to the actual Python function
AVAILABLE_FUNCTIONS = {tool['schema']['function']['name']: tool['function'] for tool in ALL_TOOLS}

# --- Updated System Prompt ---
# We've added the new 'read_file_contents' capability here.
SYSTEM_PROMPT = """
You are a helpful AI assistant that can interact with the user's local file system.
You have access to the following tools:
- `list_directory_contents`: Use this to see the files and folders in a directory.
- `read_file_contents`: Use this to read the text content of a specific file.

When asked to read a file, you must provide its full path. First, list the files if you are unsure of the path.
Be concise and clear in your answers.
"""

def run_agent(user_prompt: str):
    client = ollama.Client(host='http://localhost:11434')
    
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': user_prompt}
    ]
    
    while True:
        response = client.chat(
            model='llama3.1:8b', 
            messages=messages,
            tools=API_TOOLS # Use our dynamically generated tool list
        )
        
        response_message = response['message']
        messages.append(response_message)

        if not response_message.get('tool_calls'):
            print(f"\n✅ Final Answer:\n{response_message['content']}")
            return

        tool_calls = response_message['tool_calls']
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            function_args = tool_call['function']['arguments']
            
            # Look up the function to call from our dynamic mapping
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
            
            if function_to_call:
                tool_output = function_to_call(**function_args)
                messages.append({
                    'role': 'tool',
                    'content': tool_output,
                })
            else:
                print(f"Error: Model tried to call unknown tool '{function_name}'")

```

### What Changed and Why

*   **`fs_agent/tools.py`:** Is now the single source of truth. To add a new tool (like `write_file`), you'll just add a new function and a new entry to the `ALL_TOOLS` list.
*   **`fs_agent/agent.py`:** Is now "tool-agnostic." It doesn't know or care what the tools are; it just loads them from `tools.py`. You will not need to edit this file again to add more tools.

### Try Your Upgraded Agent!

You don't need to reinstall anything since we used the editable install (`pip install -e .`). Just run the command with new prompts!

**First, ask it to list the files so it knows what's there:**
```bash
fs-agent "What files are in the current directory?"
```

**Then, ask it to read one of those files:**
```bash
fs-agent "Can you read the contents of pyproject.toml for me?"
```

Or combine them in one go:
```bash
fs-agent "First list the files, then tell me what's inside README.md"
```

