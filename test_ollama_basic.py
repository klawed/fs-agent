#!/usr/bin/env python3
"""
Quick test to isolate if the issue is with Ollama connection or the tool logic
Usage: python test_ollama_basic.py
"""

import ollama
import json

def test_basic_ollama():
    """Test basic Ollama connection without tools"""
    print("🔧 Testing basic Ollama connection...")
    
    try:
        client = ollama.Client(host='http://localhost:11434')
        response = client.chat(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': 'Hello, just say "Hi back" please.'}]
        )
        print("✅ Basic Ollama connection works!")
        print(f"Response: {response['message']['content']}")
        return True
    except Exception as e:
        print(f"❌ Basic Ollama connection failed: {e}")
        return False

def test_ollama_with_simple_tool():
    """Test Ollama with a very simple tool to see if tools work at all"""
    print("\n🛠️  Testing Ollama with simple tool...")
    
    try:
        client = ollama.Client(host='http://localhost:11434')
        
        tools = [{
            'type': 'function',
            'function': {
                'name': 'get_weather',
                'description': 'Get weather information',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'}
                    },
                    'required': ['location']
                }
            }
        }]
        
        response = client.chat(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': 'What is the weather in Paris?'}],
            tools=tools
        )
        
        print("✅ Tool-enabled Ollama connection works!")
        print(f"Response message: {response['message']}")
        
        if response['message'].get('tool_calls'):
            print("🎯 Model wants to use tools!")
            for tool_call in response['message']['tool_calls']:
                print(f"Tool call: {tool_call}")
        else:
            print("ℹ️  Model responded without using tools")
            
        return True
    except Exception as e:
        print(f"❌ Tool-enabled Ollama failed: {e}")
        return False

def test_fs_agent_tools_directly():
    """Test our actual fs-agent tools directly (without Ollama)"""
    print("\n📁 Testing fs-agent tools directly...")
    
    try:
        # Import our tools
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from fs_agent.tools import list_directory_contents, read_file_contents
        
        # Test list_directory_contents
        print("Testing list_directory_contents...")
        result = list_directory_contents(".")
        print(f"✅ list_directory_contents result: {result[:100]}...")
        
        # Test read_file_contents
        print("Testing read_file_contents on next-steps.md...")
        result = read_file_contents("./next-steps.md")
        parsed = json.loads(result)
        if 'error' in parsed:
            print(f"❌ read_file_contents error: {parsed['error']}")
        else:
            print(f"✅ read_file_contents success: read {len(parsed['content'])} characters")
            
        return True
    except Exception as e:
        print(f"❌ Direct tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Running diagnostic tests...")
    print("=" * 50)
    
    # Test 1: Basic Ollama
    basic_works = test_basic_ollama()
    
    # Test 2: Ollama with tools
    tools_work = test_ollama_with_simple_tool()
    
    # Test 3: Our tools directly
    our_tools_work = test_fs_agent_tools_directly()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"  Basic Ollama: {'✅' if basic_works else '❌'}")
    print(f"  Ollama with tools: {'✅' if tools_work else '❌'}")
    print(f"  Our tools directly: {'✅' if our_tools_work else '❌'}")
    
    if all([basic_works, tools_work, our_tools_work]):
        print("\n🎉 All tests passed! The hang issue is likely in the agent loop logic.")
        print("💡 Try: python debug_read_test.py")
    else:
        print("\n⚠️  Some tests failed. Check the individual errors above.")

if __name__ == "__main__":
    main()
