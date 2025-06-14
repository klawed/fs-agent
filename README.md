# FS-Agent 🤖📁

A local filesystem AI assistant that can explore directories, read files, and **create/modify files** using Ollama and local LLMs.

## DIY-Why? 🤔

**Why build another AI tool when there are so many already?**

Because sometimes you need an AI that can actually *see* and *modify* your files without uploading them to the cloud. Here's why FS-Agent exists:

### The Problem
- **Privacy Concerns**: You don't want to upload sensitive code/documents to external AI services
- **Local Development**: You need an AI that understands your local project structure
- **File Management**: You want AI assistance for creating and organizing files locally
- **Offline Capability**: You want AI assistance even without internet
- **Custom Control**: You need fine-grained control over what the AI can access

### The Solution
FS-Agent runs entirely locally using Ollama, giving you:
- 🔒 **Complete Privacy**: Your files never leave your machine
- ⚡ **Fast Response**: No network latency for file operations
- 🛠️ **Extensible**: Easy to add new filesystem tools
- 🎯 **Focused**: Purpose-built for filesystem tasks
- ✍️ **Creative**: Can create and modify files safely

### When to Use FS-Agent
- Exploring unfamiliar codebases
- Creating project templates and boilerplate code
- Generating configuration files and documentation
- Summarizing project structures
- Finding specific files or code patterns
- Getting quick overviews of configuration files
- Analyzing log files or data files locally
- **NEW**: Creating files, documentation, and project structures

## Features ✨

- **Directory Listing**: Explore folder contents with natural language
- **File Reading**: Read and analyze text files up to 100KB
- **🆕 File Writing**: Create new files and safely modify existing ones
- **🆕 Backup System**: Automatic backups when overwriting files
- **Security First**: Built-in protections against path traversal and system file access
- **Extensible Architecture**: Easy to add new filesystem tools
- **Local LLM**: Uses Ollama for complete privacy

## Installation & Setup 🚀

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running locally

#### Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or visit https://ollama.ai for other installation methods
```

#### Pull a Model
```bash
# Download the recommended model (about 4.7GB)
ollama pull llama3.1:8b

# Or use a smaller model if you have limited resources
ollama pull llama3.2:1b
```

### Install FS-Agent

#### Option 1: Development Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/klawed/fs-agent.git
cd fs-agent

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

#### Option 2: Direct Installation
```bash
pip install git+https://github.com/klawed/fs-agent.git
```

### Verify Installation
```bash
# Check that Ollama is running
ollama list

# Test FS-Agent
fs-agent "What files are in the current directory?"
```

## Usage 📖

### Basic Commands

**List directory contents:**
```bash
fs-agent "What files are in this directory?"
fs-agent "Show me the contents of the src folder"
```

**Read file contents:**
```bash
fs-agent "What's in the README.md file?"
fs-agent "Can you read pyproject.toml and tell me about the dependencies?"
fs-agent "Show me the contents of config.json"
```

**🆕 Create new files:**
```bash
fs-agent "Create a TODO.md file with a list of project tasks"
fs-agent "Create a .gitignore file for a Python project"
fs-agent "Generate a basic Flask app and save it as app.py"
```

**🆕 Modify existing files (with confirmation):**
```bash
fs-agent "Add error handling to the main.py file"
fs-agent "Update the README with installation instructions"
fs-agent "Add a new function to utils.py"
```

**Combined operations:**
```bash
fs-agent "List the Python files, then create a simple test file for main.py"
fs-agent "Read the config file and create a new one with better defaults"
fs-agent "Create a complete project structure for a web scraper"
```

### Environment Configuration

**Custom Ollama Host:**
```bash
# Use a remote Ollama instance
OLLAMA_HOST=http://my-server:11434 fs-agent "List files"

# Or export for the session
export OLLAMA_HOST=http://remote-ollama:11434
fs-agent "What's in this directory?"
```

**Different Model:**
Edit `fs_agent/agent.py` and change the model name:
```python
model='llama3.2:1b'  # Use a smaller/different model
```

## Development 🛠️

### Project Structure
```
fs-agent/
├── fs_agent/
│   ├── __init__.py
│   ├── agent.py          # Main agent logic
│   ├── cli.py           # Command-line interface  
│   └── tools.py         # Filesystem tools (extensible)
├── tests/
│   ├── test_write_file.py      # Unit tests for write functionality
│   └── run_functional_tests.py # Functional test runner
├── pyproject.toml       # Project configuration
├── README.md           # This file
├── demo_write_capabilities.py  # Demo script
└── write-file.md       # Implementation plan
```

### Running Tests

```bash
# Run unit tests with pytest
pytest tests/test_write_file.py -v

# Run functional tests
python tests/run_functional_tests.py

# Run the demo
python demo_write_capabilities.py

# Run tests with coverage
pytest --cov=fs_agent tests/
```

### Adding New Tools

The architecture is designed for easy extension. To add a new tool:

1. **Add the function** to `fs_agent/tools.py`:
```python
def your_new_tool(param: str):
    """Your new tool description."""
    # Implementation here
    return json.dumps({"result": "success"})
```

2. **Add to ALL_TOOLS list**:
```python
ALL_TOOLS.append({
    "schema": {
        'type': 'function',
        'function': {
            'name': 'your_new_tool',
            'description': 'Description of what your tool does.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'param': {'type': 'string', 'description': 'Parameter description'}
                },
                'required': ['param']
            },
        },
    },
    "function": your_new_tool
})
```

3. **Update the system prompt** in `agent.py` to tell the model about the new capability.

That's it! The agent will automatically load and use your new tool.

## Security 🔒

FS-Agent includes several security measures:

### File Reading Security
- **Path Traversal Protection**: Blocks `../` attempts to escape directory bounds
- **System Directory Blocking**: Prevents access to `/`, `/etc`, `~` and other sensitive paths  
- **File Size Limits**: Restricts file reading to 100KB to prevent memory issues
- **Binary File Detection**: Gracefully handles non-text files

### 🆕 File Writing Security
- **Path Validation**: Strict validation of file paths and locations
- **Extension Whitelist**: Only allows safe file types (`.txt`, `.py`, `.json`, `.md`, etc.)
- **Overwrite Protection**: Requires explicit confirmation to overwrite existing files
- **Automatic Backups**: Creates timestamped backups before any file modifications
- **Size Limits**: Prevents creation of extremely large files (1MB limit)
- **System Directory Protection**: Blocks writes to sensitive system locations
- **Hidden File Protection**: Prevents modification of most hidden files

### General Security
- **Local-Only**: Everything runs on your machine, no data transmission
- **Comprehensive Error Handling**: Graceful handling of all error conditions
- **Audit Trail**: All file operations are logged for transparency

## Troubleshooting 🔧

**"Connection refused" errors:**
- Check that Ollama is running: `ollama list`
- Verify the host: `echo $OLLAMA_HOST`
- Try: `ollama serve` if Ollama isn't running

**"Model not found" errors:**
- Pull the model: `ollama pull llama3.1:8b`
- Check available models: `ollama list`

**"Permission denied" errors:**
- Check file permissions
- Ensure you're in a directory you can read/write
- Try with a simple text file first

**"File too large" errors:**
- Files over 100KB (read) or 1MB (write) are blocked for security
- Use other tools for large files or increase the limit in `tools.py`

**🆕 "File extension not allowed" errors:**
- Only safe file types are allowed for writing
- Check the `ALLOWED_EXTENSIONS` list in `tools.py`
- Add your extension if it's safe, or use a different extension

**🆕 "Backup failed" errors:**
- Check disk space and permissions
- Backup directory `.fs-agent-backups` needs to be writable
- Ensure original file is readable

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Add your changes (especially new tools!)
4. **Write tests** for your changes
5. Test thoroughly with both unit and functional tests
6. Submit a pull request

## License 📄

MIT License - see LICENSE file for details.

## What's Next? 🚀

The architecture is designed to be highly extensible. Planned features include:

- **Interactive Confirmation**: Better user prompts for destructive operations
- **File Templates**: Create files from predefined templates
- **Version Control Integration**: Auto-commit changes with git
- **Configuration Management**: User-configurable security settings
- **Multi-file Operations**: Create entire project structures at once

Check out `write-file.md` for the complete implementation plan and future roadmap.
