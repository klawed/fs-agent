# FS-Agent 🤖📁

A local filesystem AI assistant that can explore directories and read files using Ollama and local LLMs.

## DIY-Why? 🤔

**Why build another AI tool when there are so many already?**

Because sometimes you need an AI that can actually *see* your files without uploading them to the cloud. Here's why FS-Agent exists:

### The Problem
- **Privacy Concerns**: You don't want to upload sensitive code/documents to external AI services
- **Local Development**: You need an AI that understands your local project structure
- **Offline Capability**: You want AI assistance even without internet
- **Custom Control**: You need fine-grained control over what the AI can access

### The Solution
FS-Agent runs entirely locally using Ollama, giving you:
- 🔒 **Complete Privacy**: Your files never leave your machine
- ⚡ **Fast Response**: No network latency for file operations
- 🛠️ **Extensible**: Easy to add new filesystem tools
- 🎯 **Focused**: Purpose-built for filesystem tasks

### When to Use FS-Agent
- Exploring unfamiliar codebases
- Summarizing project structures
- Finding specific files or code patterns
- Getting quick overviews of configuration files
- Analyzing log files or data files locally

## Features ✨

- **Directory Listing**: Explore folder contents with natural language
- **File Reading**: Read and analyze text files up to 100KB
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

# Install in editable mode
pip install -e .
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

**Combined operations:**
```bash
fs-agent "List the Python files in this directory, then read the main.py file"
fs-agent "Find configuration files and summarize their contents"
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
├── pyproject.toml       # Project configuration
├── README.md           # This file
└── next-steps.md       # Development roadmap
```

### Adding New Tools

The architecture is designed for easy extension. To add a new tool:

1. **Add the function** to `fs_agent/tools.py`:
```python
def write_file_contents(path: str, content: str):
    """Write content to a file with security checks."""
    # Implementation here
    return json.dumps({"status": "success"})
```

2. **Add to ALL_TOOLS list**:
```python
ALL_TOOLS.append({
    "schema": {
        'type': 'function',
        'function': {
            'name': 'write_file_contents',
            'description': 'Write content to a file.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {'type': 'string'},
                    'content': {'type': 'string'}
                },
                'required': ['path', 'content']
            },
        },
    },
    "function": write_file_contents
})
```

3. **Update the system prompt** in `agent.py` to tell the model about the new capability.

That's it! The agent will automatically load and use your new tool.

### Running Tests
```bash
# Basic functionality test
fs-agent "List files in this directory"

# File reading test  
fs-agent "Read the pyproject.toml file"

# Security test (should be blocked)
fs-agent "Read /etc/passwd"
```

## Security 🔒

FS-Agent includes several security measures:

- **Path Traversal Protection**: Blocks `../` attempts to escape directory bounds
- **System Directory Blocking**: Prevents access to `/`, `/etc`, `~` and other sensitive paths  
- **File Size Limits**: Restricts file reading to 100KB to prevent memory issues
- **Binary File Detection**: Gracefully handles non-text files
- **Local-Only**: Everything runs on your machine, no data transmission

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
- Ensure you're in a directory you can read
- Try with a simple text file first

**"File too large" errors:**
- Files over 100KB are blocked for security
- Use other tools for large files or increase the limit in `tools.py`

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Add your changes (especially new tools!)
4. Test thoroughly
5. Submit a pull request

## License 📄

MIT License - see LICENSE file for details.

## What's Next? 🚀

Check out `next-steps.md` for planned features and improvements. The architecture is designed to be highly extensible, so adding new filesystem capabilities is straightforward.
