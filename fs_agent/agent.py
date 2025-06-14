# fs_agent/agent.py

import ollama
import json
from .tools import ALL_TOOLS  # Import the master tool list

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
            tools=API_TOOLS  # Use our dynamically generated tool list
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
