#!/usr/bin/env python3
"""
Simple test runner for fs-agent write functionality.
Run this to verify the write file feature is working correctly.
"""

import os
import sys
import tempfile
import shutil
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fs_agent.tools import write_file_contents, read_file_contents, list_directory_contents


def run_test(test_name, test_func):
    """Run a single test and report results."""
    print(f"Running {test_name}... ", end="")
    try:
        test_func()
        print("✅ PASS")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_basic_file_creation():
    """Test basic file creation functionality."""
    result = write_file_contents("test_basic.txt", "Hello, World!")
    response = json.loads(result)
    assert response["success"] is True
    assert response["operation"] == "create"
    
    # Verify file exists
    assert os.path.exists("test_basic.txt")
    with open("test_basic.txt", 'r') as f:
        assert f.read() == "Hello, World!"


def test_overwrite_protection():
    """Test that files are protected from accidental overwrite."""
    # Create initial file
    write_file_contents("test_overwrite.txt", "Original content")
    
    # Try to overwrite without flag (should fail)
    result = write_file_contents("test_overwrite.txt", "New content")
    response = json.loads(result)
    assert "error" in response
    assert response["error_type"] == "file_exists"
    
    # File should still have original content
    with open("test_overwrite.txt", 'r') as f:
        assert f.read() == "Original content"


def test_overwrite_with_backup():
    """Test overwriting with backup creation."""
    # Create initial file
    write_file_contents("test_backup.txt", "Original content")
    
    # Overwrite with flag
    result = write_file_contents("test_backup.txt", "New content", overwrite=True)
    response = json.loads(result)
    assert response["success"] is True
    assert response["operation"] == "overwrite"
    assert "backup_created" in response
    
    # Verify new content
    with open("test_backup.txt", 'r') as f:
        assert f.read() == "New content"
    
    # Verify backup exists and has original content
    backup_path = response["backup_created"]
    assert os.path.exists(backup_path)
    with open(backup_path, 'r') as f:
        assert f.read() == "Original content"


def test_security_path_traversal():
    """Test that path traversal is blocked."""
    result = write_file_contents("../malicious.txt", "Malicious content")
    response = json.loads(result)
    assert "error" in response
    assert response["error_type"] == "invalid_path"
    assert "Path traversal is not allowed" in response["error"]


def test_security_file_extensions():
    """Test that dangerous file extensions are blocked."""
    result = write_file_contents("malware.exe", "Malicious content")
    response = json.loads(result)
    assert "error" in response
    assert response["error_type"] == "invalid_path"
    assert "not allowed" in response["error"]


def test_directory_creation():
    """Test creating files in new directories."""
    result = write_file_contents("newdir/subdir/test.py", "def hello():\n    print('Hello!')")
    response = json.loads(result)
    assert response["success"] is True
    
    # Verify directory structure was created
    assert os.path.exists("newdir/subdir")
    assert os.path.exists("newdir/subdir/test.py")
    
    with open("newdir/subdir/test.py", 'r') as f:
        content = f.read()
        assert "def hello():" in content


def test_unicode_content():
    """Test writing Unicode content."""
    unicode_content = "Hello 世界! 🌍 Café con ñoño"
    result = write_file_contents("unicode_test.txt", unicode_content)
    response = json.loads(result)
    assert response["success"] is True
    
    # Verify Unicode content is preserved
    with open("unicode_test.txt", 'r', encoding='utf-8') as f:
        assert f.read() == unicode_content


def test_integration_with_read():
    """Test integration between write and read tools."""
    # Write a file
    content = "This is a test file.\nWith multiple lines.\nAnd some content."
    write_result = write_file_contents("integration_test.md", content)
    write_response = json.loads(write_result)
    assert write_response["success"] is True
    
    # Read it back using the read tool
    read_result = read_file_contents("integration_test.md")
    read_response = json.loads(read_result)
    assert read_response["path"] == "integration_test.md"
    assert read_response["content"] == content


def test_integration_with_list():
    """Test integration with directory listing."""
    # Create some test files
    write_file_contents("file1.txt", "Content 1")
    write_file_contents("file2.py", "print('Hello')")
    write_file_contents("subdir/file3.json", '{"test": true}')
    
    # List current directory
    list_result = list_directory_contents(".")
    list_response = json.loads(list_result)
    assert "contents" in list_response
    
    # Check that our files are listed
    contents = list_response["contents"]
    assert "file1.txt" in contents
    assert "file2.py" in contents
    assert "subdir" in contents


def main():
    """Run all functional tests."""
    print("🧪 Running FS-Agent Write File Functional Tests")
    print("=" * 50)
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="fs_agent_test_")
    original_cwd = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"Test directory: {test_dir}")
        print()
        
        # Run all tests
        tests = [
            ("Basic File Creation", test_basic_file_creation),
            ("Overwrite Protection", test_overwrite_protection),
            ("Overwrite with Backup", test_overwrite_with_backup),
            ("Security: Path Traversal", test_security_path_traversal),
            ("Security: File Extensions", test_security_file_extensions),
            ("Directory Creation", test_directory_creation),
            ("Unicode Content", test_unicode_content),
            ("Integration with Read", test_integration_with_read),
            ("Integration with List", test_integration_with_list),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            if run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1
        
        print()
        print("=" * 50)
        print(f"Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! Write file functionality is working correctly.")
            return 0
        else:
            print("❌ Some tests failed. Please check the implementation.")
            return 1
            
    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    sys.exit(main())
