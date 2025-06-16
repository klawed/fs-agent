# fs_agent/agent.py

import ollama
import json
import os
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
    # Check for OLLAMA_HOST environment variable, default to localhost
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    client = ollama.Client(host=ollama_host)
    
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': user_prompt}
    ]
    
    max_iterations = 10  # Prevent infinite loops
    iteration_count = 0
    
    print(f"🔧 Starting agent with max {max_iterations} iterations...")
    
    while iteration_count < max_iterations:
        iteration_count += 1
        print(f"🔄 Iteration {iteration_count}/{max_iterations}")
        
        try:
            response = client.chat(
                model='llama3.1:8b', 
                messages=messages,
                tools=API_TOOLS  # Use our dynamically generated tool list
            )
        except Exception as e:
            print(f"❌ Error calling Ollama: {e}")
            print("Please ensure the Ollama service is running and the model is available.")
            return
        
        response_message = response['message']
        messages.append(response_message)
        
        print(f"🤖 Model response: {response_message.get('content', '(no content)')}")

        if not response_message.get('tool_calls'):
            print(f"\n✅ Final Answer:\n{response_message['content']}")
            return

        tool_calls = response_message['tool_calls']
        print(f"🛠️  Model wants to call {len(tool_calls)} tool(s)")
        
        for i, tool_call in enumerate(tool_calls):
            function_name = tool_call['function']['name']
            function_args_str = tool_call['function']['arguments']
            
            print(f"🔧 Tool call {i+1}: {function_name} with args: {function_args_str}")
            
            # Look up the function to call from our dynamic mapping
            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
            
            if function_to_call:
                try:
                    # Parse the JSON arguments
                    function_args = json.loads(function_args_str) if isinstance(function_args_str, str) else function_args_str
                    print(f"📋 Parsed args: {function_args}")
                    
                    # Call the function
                    tool_output = function_to_call(**function_args)
                    print(f"📤 Tool output: {tool_output[:200]}{'...' if len(str(tool_output)) > 200 else ''}")
                    
                    messages.append({
                        'role': 'tool',
                        'content': tool_output,
                    })
                except json.JSONDecodeError as e:
                    error_msg = f"Error parsing tool arguments: {e}"
                    print(f"❌ {error_msg}")
                    messages.append({
                        'role': 'tool',
                        'content': json.dumps({"error": error_msg}),
                    })
                except Exception as e:
                    error_msg = f"Error executing tool {function_name}: {e}"
                    print(f"❌ {error_msg}")
                    messages.append({
                        'role': 'tool',
                        'content': json.dumps({"error": error_msg}),
                    })
            else:
                error_msg = f"Model tried to call unknown tool '{function_name}'"
                print(f"❌ {error_msg}")
                messages.append({
                    'role': 'tool',
                    'content': json.dumps({"error": error_msg}),
                })
    
    print(f"\n⚠️  Reached maximum iterations ({max_iterations}). Stopping to prevent infinite loop.")
