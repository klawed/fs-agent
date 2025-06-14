# Write File Feature Implementation Plan

## Overview
This document outlines the implementation plan for adding write file capabilities to fs-agent. The write-file feature will allow the AI assistant to create and modify files while maintaining strict security controls.

## Goals
- **Enable File Creation**: Allow the agent to create new files with specified content
- **Enable File Modification**: Support updating existing files (with backup/safety mechanisms)
- **Maintain Security**: Implement robust security controls to prevent malicious file operations
- **User Control**: Provide clear confirmation mechanisms for destructive operations
- **Extensible Design**: Follow the existing architecture pattern for easy maintenance

## Security Considerations

### Critical Security Requirements
1. **Path Traversal Prevention**: Block `../` and absolute paths outside working directory
2. **File Extension Restrictions**: Only allow safe file types (configurable whitelist)
3. **Size Limits**: Prevent creation of extremely large files
4. **Overwrite Protection**: Require explicit confirmation for overwriting existing files
5. **System File Protection**: Block writes to system directories and hidden files
6. **Backup Mechanism**: Create backups before modifying existing files

### Proposed Security Controls
```python
ALLOWED_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.log'}
MAX_FILE_SIZE = 1024 * 1024  # 1MB limit
FORBIDDEN_PATHS = {'/etc', '/bin', '/usr', '/sys', '/proc', '~'}
BACKUP_DIR = '.fs-agent-backups'
```

## Implementation Plan

### Phase 1: Core Write Function
**File**: `fs_agent/tools.py`

Add new function with security layers:
```python
def write_file_contents(path: str, content: str, overwrite: bool = False):
    """
    Write content to a file with comprehensive security checks.
    
    Args:
        path (str): The path where to write the file
        content (str): The content to write
        overwrite (bool): Whether to overwrite existing files
    
    Returns:
        JSON response with status or error
    """
```

**Security Implementation Steps**:
1. Validate path (no traversal, no system dirs)
2. Check file extension against whitelist
3. Verify content size limits
4. Handle existing file protection
5. Create backup if overwriting
6. Write with proper error handling

### Phase 2: Backup System
**File**: `fs_agent/backup.py` (new)

Create backup utilities:
```python
def create_backup(file_path: str) -> str:
    """Create timestamped backup of existing file."""
    
def restore_backup(backup_path: str, original_path: str) -> bool:
    """Restore file from backup."""
    
def cleanup_old_backups(max_age_days: int = 7):
    """Remove old backup files."""
```

### Phase 3: Interactive Confirmation
**File**: `fs_agent/confirmation.py` (new)

Add user confirmation for destructive operations:
```python
def confirm_overwrite(file_path: str) -> bool:
    """Ask user to confirm file overwrite."""
    
def confirm_large_file(size: int) -> bool:
    """Ask user to confirm large file creation."""
```

### Phase 4: Enhanced Agent Integration
**File**: `fs_agent/agent.py`

Update system prompt to include write capabilities and safety guidelines:
```python
SYSTEM_PROMPT = """
...existing content...
- `write_file_contents`: Create or modify files with content. Always confirm before overwriting.

IMPORTANT SAFETY RULES:
- Always ask for confirmation before overwriting existing files
- Never write to system directories or hidden files
- Inform the user about backup creation when modifying files
- Be cautious with large files or sensitive content
"""
```

### Phase 5: Tool Registration
**File**: `fs_agent/tools.py`

Add to `ALL_TOOLS` list:
```python
{
    "schema": {
        'type': 'function',
        'function': {
            'name': 'write_file_contents',
            'description': 'Create a new file or update an existing file with specified content. Use with caution.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {
                        'type': 'string', 
                        'description': 'Path where to write the file'
                    },
                    'content': {
                        'type': 'string', 
                        'description': 'Content to write to the file'
                    },
                    'overwrite': {
                        'type': 'boolean', 
                        'description': 'Whether to overwrite existing files (requires confirmation)',
                        'default': False
                    }
                },
                'required': ['path', 'content']
            },
        },
    },
    "function": write_file_contents
}
```

## Usage Examples

### Safe Use Cases
```bash
# Create a new file
fs-agent "Create a TODO.md file with a list of project tasks"

# Generate configuration
fs-agent "Create a .gitignore file for a Python project"

# Create documentation
fs-agent "Write a quick start guide and save it as quickstart.md"
```

### Advanced Use Cases
```bash
# Update existing file (with confirmation)
fs-agent "Add error handling to the main.py file"

# Create from template
fs-agent "Create a basic Flask app structure in app.py"

# Batch file creation
fs-agent "Create basic project structure with README, requirements.txt, and main.py"
```

## Error Handling

### Expected Error Scenarios
1. **Permission Denied**: File/directory not writable
2. **Disk Full**: Insufficient space for file creation
3. **Invalid Path**: Path contains forbidden characters or locations
4. **File Locked**: File is currently in use by another process
5. **Size Exceeded**: Content exceeds maximum file size limit

### Error Response Format
```json
{
    "error": "Description of what went wrong",
    "error_type": "permission_denied|disk_full|invalid_path|file_locked|size_exceeded",
    "suggested_action": "What the user can do to resolve this"
}
```

## Testing Strategy

### Unit Tests
- Path validation functions
- Content size checking
- File extension validation
- Backup creation and restoration

### Integration Tests
- Full write workflow
- Error handling scenarios
- Backup system functionality
- User confirmation flows

### Security Tests
- Path traversal attempts
- System file write attempts
- Large file creation
- Malicious content handling

## Configuration Options

### User-Configurable Settings
```python
# In ~/.fs-agent-config.json
{
    "write_permissions": {
        "enabled": true,
        "max_file_size_mb": 1,
        "allowed_extensions": [".txt", ".md", ".py", ".js", ".json"],
        "backup_enabled": true,
        "backup_retention_days": 7,
        "require_confirmation": true
    }
}
```

## Rollback Plan

If issues arise, provide easy rollback:
1. **Disable Feature**: Quick config flag to disable write functionality
2. **Restore Backups**: Tool to restore all files from backups
3. **Remove Function**: Simple removal from `ALL_TOOLS` list disables immediately

## Future Enhancements

### Phase 6: Advanced Features (Future)
- **File Templating**: Create files from templates
- **Multi-file Operations**: Create entire directory structures
- **Content Validation**: Check syntax for code files before writing
- **Version Control Integration**: Auto-commit changes with git
- **Diff Preview**: Show changes before applying to existing files

## Implementation Timeline

- **Week 1**: Core write function with basic security
- **Week 2**: Backup system and error handling
- **Week 3**: Interactive confirmation and testing
- **Week 4**: Documentation and user acceptance testing

## Success Criteria

✅ **Security**: No successful path traversal or system file access  
✅ **Reliability**: Handles errors gracefully without data loss  
✅ **Usability**: Intuitive prompts work as expected  
✅ **Safety**: Backup system prevents accidental data loss  
✅ **Performance**: Fast response for typical file operations  

## Risk Mitigation

### High-Risk Scenarios
1. **Data Loss**: Mitigated by backup system and confirmation prompts
2. **Security Breach**: Mitigated by path validation and extension restrictions
3. **System Damage**: Mitigated by forbidden path blocking
4. **Performance Issues**: Mitigated by file size limits

### Monitoring & Alerting
- Log all write operations for audit
- Alert on suspicious patterns (many overwrites, large files)
- Track backup disk usage
- Monitor for repeated security violations

This implementation plan provides a secure, user-friendly way to add write capabilities while maintaining the safety and security standards established in the existing codebase.
