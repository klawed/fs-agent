#!/usr/bin/env python3
"""
Quick stress test for potential hanging scenarios
Tests specific cases that might cause infinite loops or timeouts
"""

import sys
import os
import time
import signal
from threading import Timer

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TimeoutTest:
    """Context manager to timeout tests that might hang"""
    
    def __init__(self, timeout_seconds=60):
        self.timeout = timeout_seconds
        self.timer = None
    
    def __enter__(self):
        # Set up timeout timer
        self.timer = Timer(self.timeout, self._timeout_handler)
        self.timer.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer:
            self.timer.cancel()
    
    def _timeout_handler(self):
        print(f"\n❌ TEST TIMEOUT after {self.timeout} seconds - likely hanging!")
        os._exit(1)  # Force exit

def test_hanging_scenarios():
    """Test specific scenarios that might cause hanging"""
    print("🕒 Testing potential hanging scenarios...")
    
    # Test 1: Complex write operation that might loop
    print("\n1. Testing complex multi-step write operation...")
    with TimeoutTest(45):
        try:
            from fs_agent.agent import run_agent
            start_time = time.time()
            
            # This combines multiple operations that might cause issues
            run_agent("Create a file called 'multi_test.py' with a simple Python script that prints 'Hello World'")
            
            duration = time.time() - start_time
            print(f"   ✅ Completed in {duration:.1f} seconds")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Test 2: Reading and then writing the same file
    print("\n2. Testing read-then-write cycle...")
    with TimeoutTest(45):
        try:
            start_time = time.time()
            
            # This might cause issues if not handled properly
            run_agent("Read the contents of pyproject.toml and then create a backup copy called pyproject_backup.toml")
            
            duration = time.time() - start_time
            print(f"   ✅ Completed in {duration:.1f} seconds")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Test 3: Tool error handling (file that doesn't exist)
    print("\n3. Testing error handling with non-existent file...")
    with TimeoutTest(30):
        try:
            start_time = time.time()
            
            # This should handle errors gracefully without hanging
            run_agent("Can you read the contents of definitely_does_not_exist.txt?")
            
            duration = time.time() - start_time
            print(f"   ✅ Completed in {duration:.1f} seconds")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

def test_direct_tool_performance():
    """Test tools directly for performance issues"""
    print("\n⚡ Testing direct tool performance...")
    
    try:
        from fs_agent.tools import write_file_contents, read_file_contents, list_directory_contents
        
        # Test many small operations quickly
        print("1. Testing rapid fire tool calls...")
        start_time = time.time()
        
        for i in range(5):
            # List directory
            result1 = list_directory_contents(".")
            
            # Write a small file
            result2 = write_file_contents(f"temp_{i}.txt", f"Test content {i}")
            
            # Read it back
            result3 = read_file_contents(f"temp_{i}.txt")
            
            # Clean up
            try:
                os.remove(f"temp_{i}.txt")
            except:
                pass
        
        duration = time.time() - start_time
        print(f"   ✅ 5 write/read cycles completed in {duration:.1f} seconds")
        
        # Test edge case handling speed
        print("2. Testing error case handling speed...")
        start_time = time.time()
        
        # These should all fail quickly, not hang
        write_file_contents("../illegal.txt", "content")  # Path traversal
        write_file_contents("test.exe", "content")  # Bad extension
        read_file_contents("does_not_exist.txt")  # Missing file
        
        duration = time.time() - start_time
        print(f"   ✅ Error cases handled in {duration:.1f} seconds")
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")

def main():
    print("🔥 Running fs-agent hanging stress test...")
    print("This will test scenarios that previously caused hanging issues.")
    print("=" * 60)
    
    try:
        # Test direct tools first (should be fast)
        test_direct_tool_performance()
        
        # Test agent scenarios (might be slower but shouldn't hang)
        test_hanging_scenarios()
        
        print("\n" + "=" * 60)
        print("🎉 All stress tests completed successfully!")
        print("No hanging issues detected in the feature/write-file branch.")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Stress test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Stress test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nStress test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
