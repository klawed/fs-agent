import ollama
import logging

# Enable basic logging to see the HTTP status
logging.basicConfig(level=logging.INFO)

def main():
    print("--- Final debug test for Ollama tool calling ---")
    
    client = ollama.Client(host='http://localhost:11434')
    model_to_test = 'llama3.1:8b'
    
    messages = [{'role': 'user', 'content': 'list the files in the current directory'}]
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

    try:
        print(f"\nAttempting to call client.chat with model: '{model_to_test}'...")
        
        # The API call we know works
        response = client.chat(
            model=model_to_test,
            messages=messages,
            tools=tools,
        )
        
        print("\n--- SUCCESS! ---")
        print("The API call was successful. Raw response from the library:")
        
        # The FIX: Print the response directly. It has a readable representation.
        # This avoids the JSON serialization error entirely.
        print(response)
        
        print("\nDrilling into the 'message' part:")
        print(response['message'])
        
        print("\nDrilling into the 'tool_calls' part:")
        print(response['message']['tool_calls'])

    except ollama.ResponseError as e:
        print(f"\n--- FAILURE! ---")
        print(f"Status code: {e.status_code}, Error: {e.error}")
        
    except Exception as e:
        print(f"\n--- UNEXPECTED SCRIPT ERROR! ---")
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
