#!/usr/bin/env python3
"""
Simple debugging script to test the fs-agent read functionality
Usage: python debug_read_test.py
"""

import sys
import os

# Add the current directory to the path so we can import fs_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fs_agent.agent import run_agent

def main():
    print("🔍 Testing fs-agent read functionality...")
    print("=" * 50)
    
    # Test the exact command that's hanging
    test_prompt = "and what's in ./next-steps.md?"
    
    print(f"🧪 Testing prompt: '{test_prompt}'")
    print("-" * 30)
    
    try:
        run_agent(test_prompt)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
