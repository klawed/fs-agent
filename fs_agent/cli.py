# fs_agent/cli.py

import sys
from .agent import run_agent

def main():
    if len(sys.argv) < 2:
        print("Usage: fs-agent \"Your question about the file system here\"")
        print("Example: fs-agent \"What files are in my current directory?\"")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    
    print(f"🤔 You asked: \"{user_prompt}\"")
    print("-" * 20)
    
    try:
        run_agent(user_prompt)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure the Ollama service is running.")
        
