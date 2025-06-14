# fs_agent/agent.py

import ollama
import json
from .tools import list_directory_contents

AVAILABLE_TOOLS = {"list_directory_contents": list_directory_contents}

SYSTEM_PROMPT = """
You are a helpful AI assistant that can answer questions about the user's local file system.
You have access to a tool called `list_directory_contents` which allows you to see the files and folders in a directory.
When a user asks what is in a directory, or asks about files, use this tool.
If the user doesn't specify a path, assume they mean the current directory, which you can query using ".".
Be concise and clear in your answers.
"""

def run_agent(user_prompt: str):
    client = ollama.Client(host='http://localhost:11434')
    
    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'list_directory_contents',
                'description': 'List the files and folders in a specified directory path.',
                'parameters': { 'type': 'object', 'properties': {'path': {'type': 'string'}}},
            },
        }
    ]
    
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': user_prompt}
    ]
    
    while True:
        # Use the model that we have proven works
        response = client.chat(
            model='llama3.1:8b', 
            messages=messages,
            tools=tools
        )
        
        # The ollama library returns a Message object. We append it to our history.
        # The client is smart enough to handle this object in the next request.
        response_message = response['message']
        messages.append(response_message)

        # If the model did NOT call a tool, we are done.
        if not response_message.get('tool_calls'):
            print(f"\n✅ Final Answer:\n{response_message['content']}")
            return

        # The model DID call a tool. We need to process it.
        tool_calls = response_message['tool_calls']
        for tool_call in tool_calls:
            # We access the function details using dictionary-style keys
            function_name = tool_call['function']['name']
            function_args = tool_call['function']['arguments']
            
            function_to_call = AVAILABLE_TOOLS.get(function_name)
            
            if function_to_call:
                # Execute the tool function
                tool_output = function_to_call(**function_args)
                
                # Append the tool's output to the conversation history
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.get('id'), # Pass the ID if available
                    'name': function_name,
                    'content': tool_output,
                })
            else:
                print(f"Error: Model tried to call unknown tool '{function_name}'")
