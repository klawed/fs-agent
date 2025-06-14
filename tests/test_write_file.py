# tests/test_write_file.py

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the functions we want to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fs_agent.tools import (
    write_file_contents, 
    _validate_write_path, 
    _create_backup,
    ALLOWED_EXTENSIONS,
    FORBIDDEN_PATHS,
    BACKUP_DIR
)


class TestValidateWritePath:
    """Test path validation for write operations."""
    
    def test_valid_relative_path(self):
        """Test that valid relative paths are accepted."""
        result = _validate_write_path("test.txt")
        assert result["valid"] is True
        assert result["error"] is None
    
    def test_valid_nested_path(self):
        """Test that valid nested relative paths are accepted."""
        result = _validate_write_path("folder/subfolder/test.py")
        assert result["valid"] is True
        assert result["error"] is None
    
    def test_path_traversal_blocked(self):
        """Test that path traversal attempts are blocked."""
        result = _validate_write_path("../test.txt")
        assert result["valid"] is False
        assert "Path traversal is not allowed" in result["error"]
    
    def test_system_directory_blocked(self):
        """Test that system directories are blocked."""
        for forbidden_path in ["/etc/passwd", "/bin/bash", "/usr/local/test"]:
            with patch('os.path.abspath', return_value=forbidden_path):
                result = _validate_write_path("test.txt")
                assert result["valid"] is False
                assert "system directory" in result["error"]
    
    def test_hidden_files_blocked(self):
        """Test that most hidden files are blocked."""
        result = _validate_write_path(".secret")
        assert result["valid"] is False
        assert "hidden files is not allowed" in result["error"]
    
    def test_allowed_hidden_files(self):
        """Test that some hidden files are allowed."""
        for allowed_file in [".gitignore", ".env.example", ".editorconfig"]:
            result = _validate_write_path(allowed_file)
            assert result["valid"] is True
    
    def test_file_extension_validation(self):
        """Test file extension validation."""
        # Valid extensions
        for ext in [".txt", ".py", ".json", ".md"]:
            result = _validate_write_path(f"test{ext}")
            assert result["valid"] is True
        
        # Invalid extensions
        for ext in [".exe", ".bat", ".dll"]:
            result = _validate_write_path(f"test{ext}")
            assert result["valid"] is False
            assert "not allowed" in result["error"]
    
    def test_no_extension_allowed(self):
        """Test that files without extensions are allowed."""
        result = _validate_write_path("README")
        assert result["valid"] is True


class TestCreateBackup:
    """Test backup creation functionality."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a test file
        self.test_file = "test.txt"
        with open(self.test_file, 'w') as f:
            f.write("Original content")
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_backup_creation(self):
        """Test that backups are created correctly."""
        backup_path = _create_backup(self.test_file)
        
        # Check that backup directory was created
        assert os.path.exists(BACKUP_DIR)
        
        # Check that backup file exists
        assert os.path.exists(backup_path)
        
        # Check that backup contains original content
        with open(backup_path, 'r') as f:
            content = f.read()
        assert content == "Original content"
        
        # Check backup filename format
        backup_filename = os.path.basename(backup_path)
        assert backup_filename.startswith("test.txt.backup.")
        assert len(backup_filename.split('.')) == 4  # test.txt.backup.timestamp
    
    def test_backup_preserves_metadata(self):
        """Test that backup preserves file metadata."""
        # Modify file timestamp
        import time
        old_time = time.time() - 3600  # 1 hour ago
        os.utime(self.test_file, (old_time, old_time))
        
        backup_path = _create_backup(self.test_file)
        
        # Check that modification time is preserved
        original_mtime = os.path.getmtime(self.test_file)
        backup_mtime = os.path.getmtime(backup_path)
        assert abs(original_mtime - backup_mtime) < 1  # Within 1 second


class TestWriteFileContents:
    """Test the main write file functionality."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_create_new_file(self):
        """Test creating a new file."""
        content = "Hello, world!"
        result = write_file_contents("test.txt", content)
        
        # Parse JSON response
        response = json.loads(result)
        
        # Check success
        assert response["success"] is True
        assert response["path"] == "test.txt"
        assert response["operation"] == "create"
        assert response["size_bytes"] == len(content.encode('utf-8'))
        
        # Check file was actually created
        assert os.path.exists("test.txt")
        with open("test.txt", 'r') as f:
            assert f.read() == content
    
    def test_create_file_in_subdirectory(self):
        """Test creating a file in a subdirectory."""
        content = "Test content"
        result = write_file_contents("subdir/test.txt", content)
        
        response = json.loads(result)
        assert response["success"] is True
        
        # Check directory was created
        assert os.path.exists("subdir")
        assert os.path.exists("subdir/test.txt")
        
        with open("subdir/test.txt", 'r') as f:
            assert f.read() == content
    
    def test_overwrite_requires_flag(self):
        """Test that overwriting requires explicit flag."""
        # Create initial file
        with open("test.txt", 'w') as f:
            f.write("Original content")
        
        # Try to overwrite without flag
        result = write_file_contents("test.txt", "New content")
        response = json.loads(result)
        
        assert "error" in response
        assert response["error_type"] == "file_exists"
        assert "overwrite=true" in response["error"]
        
        # File should still contain original content
        with open("test.txt", 'r') as f:
            assert f.read() == "Original content"
    
    def test_overwrite_with_flag(self):
        """Test overwriting with explicit flag."""
        # Create initial file
        with open("test.txt", 'w') as f:
            f.write("Original content")
        
        # Overwrite with flag
        result = write_file_contents("test.txt", "New content", overwrite=True)
        response = json.loads(result)
        
        assert response["success"] is True
        assert response["operation"] == "overwrite"
        assert "backup_created" in response
        
        # Check new content
        with open("test.txt", 'r') as f:
            assert f.read() == "New content"
        
        # Check backup was created
        backup_path = response["backup_created"]
        assert os.path.exists(backup_path)
        with open(backup_path, 'r') as f:
            assert f.read() == "Original content"
    
    def test_path_traversal_security(self):
        """Test that path traversal is blocked."""
        result = write_file_contents("../test.txt", "malicious content")
        response = json.loads(result)
        
        assert "error" in response
        assert response["error_type"] == "invalid_path"
        assert "Path traversal is not allowed" in response["error"]
    
    def test_system_directory_security(self):
        """Test that system directories are blocked."""
        with patch('os.path.abspath', return_value='/etc/test.txt'):
            result = write_file_contents("test.txt", "malicious content")
            response = json.loads(result)
            
            assert "error" in response
            assert response["error_type"] == "invalid_path"
            assert "system directory" in response["error"]
    
    def test_file_extension_security(self):
        """Test that dangerous file extensions are blocked."""
        result = write_file_contents("malware.exe", "malicious content")
        response = json.loads(result)
        
        assert "error" in response
        assert response["error_type"] == "invalid_path"
        assert "not allowed" in response["error"]
    
    def test_file_size_limit(self):
        """Test that large files are rejected."""
        # Create content larger than limit
        large_content = "x" * (1024 * 1024 + 1)  # 1MB + 1 byte
        
        result = write_file_contents("large.txt", large_content)
        response = json.loads(result)
        
        assert "error" in response
        assert response["error_type"] == "size_exceeded"
        assert "too large" in response["error"]
    
    def test_unicode_content(self):
        """Test writing Unicode content."""
        content = "Hello 世界! 🌍 Ñoño café"
        result = write_file_contents("unicode.txt", content)
        
        response = json.loads(result)
        assert response["success"] is True
        
        # Verify content is preserved
        with open("unicode.txt", 'r', encoding='utf-8') as f:
            assert f.read() == content
    
    @patch('builtins.open', side_effect=PermissionError())
    def test_permission_error(self, mock_file):
        """Test handling of permission errors."""
        result = write_file_contents("test.txt", "content")
        response = json.loads(result)
        
        assert "error" in response
        assert response["error_type"] == "permission_denied"
        assert "Permission denied" in response["error"]
    
    @patch('builtins.open', side_effect=OSError("No space left on device"))
    def test_disk_full_error(self, mock_file):
        """Test handling of disk full errors."""
        result = write_file_contents("test.txt", "content")
        response = json.loads(result)
        
        assert "error" in response
        assert response["error_type"] == "disk_full"
        assert "disk space" in response["error"]
    
    def test_empty_content(self):
        """Test writing empty content."""
        result = write_file_contents("empty.txt", "")
        response = json.loads(result)
        
        assert response["success"] is True
        assert response["size_bytes"] == 0
        
        # Check file exists and is empty
        assert os.path.exists("empty.txt")
        with open("empty.txt", 'r') as f:
            assert f.read() == ""


class TestIntegration:
    """Integration tests for the complete write file workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_complete_workflow(self):
        """Test a complete file creation and modification workflow."""
        # Step 1: Create new file
        result1 = write_file_contents("workflow.py", "def hello():\n    print('Hello')")
        response1 = json.loads(result1)
        assert response1["success"] is True
        assert response1["operation"] == "create"
        
        # Step 2: Modify the file
        new_content = "def hello():\n    print('Hello, World!')\n\ndef goodbye():\n    print('Goodbye')"
        result2 = write_file_contents("workflow.py", new_content, overwrite=True)
        response2 = json.loads(result2)
        assert response2["success"] is True
        assert response2["operation"] == "overwrite"
        
        # Step 3: Verify backup was created
        backup_path = response2["backup_created"]
        assert os.path.exists(backup_path)
        
        # Step 4: Verify current content
        with open("workflow.py", 'r') as f:
            assert f.read() == new_content
        
        # Step 5: Verify backup content
        with open(backup_path, 'r') as f:
            assert f.read() == "def hello():\n    print('Hello')"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
