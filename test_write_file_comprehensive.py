#!/usr/bin/env python3
"""
Comprehensive test suite for the write-file functionality
Tests both basic functionality and potential hanging scenarios
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the current directory to the path so we can import fs_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tools_directly():
    """Test the tools directly without going through the agent"""
    print("🧪 Testing tools directly...")
    
    try:
        from fs_agent.tools import list_directory_contents, read_file_contents, write_file_contents
        
        # Test 1: List directory
        print("1. Testing list_directory_contents...")
        result = list_directory_contents(".")
        parsed = json.loads(result)
        print(f"   ✅ Found {len(parsed.get('contents', []))} items")
        
        # Test 2: Write a new file
        print("2. Testing write_file_contents (new file)...")
        test_content = "# Test File\n\nThis is a test file created by the fs-agent write functionality.\n\nTimestamp: " + str(time.time())
        result = write_file_contents("test_output.md", test_content)
        parsed = json.loads(result)
        if parsed.get("success"):
            print(f"   ✅ Successfully created file: {parsed['path']}")
        else:
            print(f"   ❌ Failed to create file: {parsed.get('error', 'Unknown error')}")
        
        # Test 3: Read the file we just wrote
        print("3. Testing read_file_contents on our test file...")
        result = read_file_contents("test_output.md")
        parsed = json.loads(result)
        if "content" in parsed:
            print(f"   ✅ Successfully read {len(parsed['content'])} characters")
        else:
            print(f"   ❌ Failed to read file: {parsed.get('error', 'Unknown error')}")
        
        # Test 4: Try to overwrite without permission (should fail)
        print("4. Testing overwrite protection...")
        result = write_file_contents("test_output.md", "This should fail", overwrite=False)
        parsed = json.loads(result)
        if "error" in parsed and "already exists" in parsed["error"]:
            print("   ✅ Overwrite protection working correctly")
        else:
            print(f"   ❌ Overwrite protection failed: {parsed}")
        
        # Test 5: Overwrite with permission (should succeed and create backup)
        print("5. Testing overwrite with permission...")
        new_content = "# Updated Test File\n\nThis file has been overwritten.\n\nTimestamp: " + str(time.time())
        result = write_file_contents("test_output.md", new_content, overwrite=True)
        parsed = json.loads(result)
        if parsed.get("success") and parsed.get("backup_created"):
            print(f"   ✅ Successfully overwrote file, backup created: {parsed['backup_created']}")
        else:
            print(f"   ❌ Overwrite failed: {parsed}")
        
        print("✅ All direct tool tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Direct tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_basic():
    """Test basic agent functionality"""
    print("\n🤖 Testing basic agent functionality...")
    
    try:
        from fs_agent.agent import run_agent
        
        # Test simple file listing (should work quickly)
        print("Testing: 'What files are in the current directory?'")
        start_time = time.time()
        run_agent("What files are in the current directory?")
        duration = time.time() - start_time
        
        if duration > 30:  # If it takes more than 30 seconds, something's wrong
            print(f"⚠️  Agent took {duration:.1f} seconds - might be hanging")
            return False
        else:
            print(f"✅ Agent completed in {duration:.1f} seconds")
            return True
            
    except Exception as e:
        print(f"❌ Basic agent test failed: {e}")
        return False

def test_agent_write_functionality():
    """Test agent write functionality with potential hanging scenarios"""
    print("\n✍️  Testing agent write functionality...")
    
    try:
        from fs_agent.agent import run_agent
        
        # Test 1: Simple file creation
        print("Test 1: Simple file creation")
        start_time = time.time()
        run_agent("Create a simple test file called 'agent_test.txt' with the content 'Hello from fs-agent!'")
        duration = time.time() - start_time
        
        if duration > 45:
            print(f"⚠️  Write test took {duration:.1f} seconds - might be hanging")
            return False
        else:
            print(f"✅ Write test completed in {duration:.1f} seconds")
        
        # Test 2: Read the file we just created
        print("Test 2: Reading the file we created")
        start_time = time.time()
        run_agent("Can you read the contents of agent_test.txt?")
        duration = time.time() - start_time
        
        if duration > 30:
            print(f"⚠️  Read test took {duration:.1f} seconds - might be hanging")
            return False
        else:
            print(f"✅ Read test completed in {duration:.1f} seconds")
            
        return True
        
    except Exception as e:
        print(f"❌ Agent write test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases that might cause hanging"""
    print("\n🔍 Testing edge cases...")
    
    try:
        from fs_agent.tools import write_file_contents
        
        # Test 1: Invalid file extension
        print("1. Testing invalid file extension...")
        result = write_file_contents("test.exe", "content")
        parsed = json.loads(result)
        if "error" in parsed and "extension" in parsed["error"]:
            print("   ✅ Invalid extension correctly rejected")
        else:
            print(f"   ❌ Invalid extension not handled: {parsed}")
        
        # Test 2: Path traversal attempt
        print("2. Testing path traversal protection...")
        result = write_file_contents("../test.txt", "content")
        parsed = json.loads(result)
        if "error" in parsed and "traversal" in parsed["error"]:
            print("   ✅ Path traversal correctly blocked")
        else:
            print(f"   ❌ Path traversal not blocked: {parsed}")
        
        # Test 3: Very large content (should be rejected)
        print("3. Testing size limit...")
        large_content = "x" * (2 * 1024 * 1024)  # 2MB content
        result = write_file_contents("large.txt", large_content)
        parsed = json.loads(result)
        if "error" in parsed and ("large" in parsed["error"] or "size" in parsed["error"]):
            print("   ✅ Size limit correctly enforced")
        else:
            print(f"   ❌ Size limit not enforced: {parsed}")
        
        print("✅ All edge case tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files created during testing"""
    print("\n🧹 Cleaning up test files...")
    
    test_files = ["test_output.md", "agent_test.txt"]
    backup_dir = Path(".fs-agent-backups")
    
    for file in test_files:
        if Path(file).exists():
            try:
                Path(file).unlink()
                print(f"   🗑️  Removed {file}")
            except:
                print(f"   ⚠️  Could not remove {file}")
    
    # Clean up backup directory if it exists and is empty
    if backup_dir.exists():
        try:
            # List contents
            backups = list(backup_dir.glob("*"))
            if backups:
                print(f"   📁 Found {len(backups)} backup files in {backup_dir}")
            else:
                backup_dir.rmdir()
                print(f"   🗑️  Removed empty backup directory")
        except:
            print(f"   ⚠️  Could not clean backup directory")

def main():
    print("🚀 Starting comprehensive fs-agent write-file branch test...")
    print("=" * 60)
    
    # Track which tests pass
    results = {
        "direct_tools": False,
        "basic_agent": False,
        "write_functionality": False,
        "edge_cases": False
    }
    
    # Run tests
    try:
        results["direct_tools"] = test_tools_directly()
        results["basic_agent"] = test_agent_basic()
        results["write_functionality"] = test_agent_write_functionality()
        results["edge_cases"] = test_edge_cases()
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
    
    # Clean up
    cleanup_test_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The feature/write-file branch is working correctly.")
    elif passed_tests > 0:
        print("⚠️  Some tests passed, but there may be issues to investigate.")
    else:
        print("❌ All tests failed. There are significant issues with the branch.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
