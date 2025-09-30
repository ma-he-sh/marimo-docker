# Ollama Integration Example

This notebook demonstrates how to use Ollama models within Marimo.

## Setup and Configuration

```python
import ollama
import marimo as mo
import json
import time
from typing import List, Dict, Any

# Configure Ollama client
OLLAMA_HOST = "http://ollama:11434"  # Docker service name
```

## Check Ollama Connection

```python
def check_ollama_connection():
    """Check if Ollama service is running and accessible."""
    try:
        response = ollama.list()
        return mo.md(f"✅ Ollama is running! Found {len(response['models'])} models.")
    except Exception as e:
        return mo.md(f"❌ Ollama connection failed: {str(e)}")

connection_status = check_ollama_connection()
connection_status
```

## List Available Models

```python
def list_available_models():
    """List all available Ollama models."""
    try:
        models = ollama.list()
        if not models['models']:
            return mo.md("No models installed. Use the model installation section below.")
        
        model_list = []
        for model in models['models']:
            model_list.append(f"- **{model['name']}** (Size: {model['size']:,} bytes)")
        
        return mo.md(f"## Available Models:\n\n" + "\n".join(model_list))
    except Exception as e:
        return mo.md(f"Error listing models: {str(e)}")

available_models = list_available_models()
available_models
```

## Install a Model

```python
# Model selection for installation
model_to_install = mo.ui.dropdown(
    options=[
        "llama3.2:3b",      # Small, fast model
        "llama3.2:1b",      # Very small model
        "phi3:mini",        # Microsoft's Phi-3 mini
        "gemma2:2b",        # Google's Gemma 2B
        "qwen2.5:3b",       # Alibaba's Qwen 2.5
        "mistral:7b",       # Mistral 7B
        "codellama:7b",     # Code-focused model
    ],
    value="llama3.2:3b",
    label="Select model to install:"
)

def install_model(model_name: str):
    """Install a specific Ollama model."""
    try:
        mo.status.update("Installing model... This may take several minutes.")
        ollama.pull(model_name)
        mo.status.update("Model installed successfully!")
        return mo.md(f"✅ Successfully installed **{model_name}**")
    except Exception as e:
        mo.status.update("Installation failed.")
        return mo.md(f"❌ Failed to install {model_name}: {str(e)}")

mo.vstack([
    model_to_install,
    mo.ui.button(
        label="Install Model",
        on_click=lambda: install_model(model_to_install.value)
    )
])
```

## Chat with Ollama

```python
# Chat interface
selected_model = mo.ui.dropdown(
    options=["llama3.2:3b", "llama3.2:1b", "phi3:mini", "gemma2:2b"],
    value="llama3.2:3b",
    label="Select model for chat:"
)

chat_input = mo.ui.text_area(
    placeholder="Enter your message here...",
    label="Your message:",
    rows=3
)

def chat_with_ollama(model: str, message: str) -> str:
    """Send a message to Ollama and get response."""
    if not message.strip():
        return "Please enter a message."
    
    try:
        mo.status.update("Generating response...")
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': message
            }]
        )
        mo.status.update("Response generated!")
        return response['message']['content']
    except Exception as e:
        mo.status.update("Error occurred.")
        return f"Error: {str(e)}"

chat_response = mo.ui.button(
    label="Send Message",
    on_click=lambda: chat_with_ollama(selected_model.value, chat_input.value)
)

mo.vstack([
    selected_model,
    chat_input,
    chat_response,
    mo.md("**Response:**"),
    mo.md(chat_response.value if chat_response.value else "Click 'Send Message' to get a response.")
])
```

## Code Generation Example

```python
# Code generation interface
code_prompt = mo.ui.text_area(
    placeholder="Describe the code you want to generate...",
    label="Code generation prompt:",
    rows=3
)

def generate_code(prompt: str) -> str:
    """Generate code using Ollama."""
    if not prompt.strip():
        return "Please enter a code generation prompt."
    
    try:
        mo.status.update("Generating code...")
        response = ollama.chat(
            model="codellama:7b" if "codellama:7b" in [m['name'] for m in ollama.list()['models']] else selected_model.value,
            messages=[{
                'role': 'user',
                'content': f"Generate Python code for: {prompt}. Return only the code with proper comments."
            }]
        )
        mo.status.update("Code generated!")
        return f"```python\n{response['message']['content']}\n```"
    except Exception as e:
        mo.status.update("Error occurred.")
        return f"Error: {str(e)}"

code_generation_button = mo.ui.button(
    label="Generate Code",
    on_click=lambda: generate_code(code_prompt.value)
)

mo.vstack([
    code_prompt,
    code_generation_button,
    mo.md("**Generated Code:**"),
    mo.md(code_generation_button.value if code_generation_button.value else "Click 'Generate Code' to get code.")
])
```

## Batch Processing

```python
# Batch processing example
batch_input = mo.ui.text_area(
    placeholder="Enter multiple prompts, one per line...",
    label="Batch prompts:",
    rows=5
)

def process_batch(prompts_text: str) -> str:
    """Process multiple prompts in batch."""
    prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
    if not prompts:
        return "Please enter at least one prompt."
    
    results = []
    for i, prompt in enumerate(prompts, 1):
        try:
            mo.status.update(f"Processing prompt {i}/{len(prompts)}...")
            response = ollama.chat(
                model=selected_model.value,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            results.append(f"**Prompt {i}:** {prompt}\n**Response:** {response['message']['content']}\n---")
        except Exception as e:
            results.append(f"**Prompt {i}:** {prompt}\n**Error:** {str(e)}\n---")
    
    mo.status.update("Batch processing complete!")
    return "\n".join(results)

batch_button = mo.ui.button(
    label="Process Batch",
    on_click=lambda: process_batch(batch_input.value)
)

mo.vstack([
    batch_input,
    batch_button,
    mo.md("**Batch Results:**"),
    mo.md(batch_button.value if batch_button.value else "Click 'Process Batch' to process all prompts.")
])
```

## Model Management

```python
# Model management
def get_model_info():
    """Get detailed information about installed models."""
    try:
        models = ollama.list()
        info = []
        for model in models['models']:
            info.append(f"""
**Model:** {model['name']}
- **Size:** {model['size']:,} bytes ({model['size'] / (1024**3):.2f} GB)
- **Modified:** {model['modified_at']}
- **Digest:** {model['digest'][:12]}...
""")
        return "\n".join(info) if info else "No models installed."
    except Exception as e:
        return f"Error getting model info: {str(e)}"

model_info = get_model_info()
mo.md(f"## Model Information\n\n{model_info}")
```

## Performance Monitoring

```python
# Performance monitoring
def benchmark_model(model_name: str, test_prompt: str = "Hello, how are you?") -> Dict[str, Any]:
    """Benchmark a model's response time."""
    try:
        start_time = time.time()
        response = ollama.chat(
            model=model_name,
            messages=[{
                'role': 'user',
                'content': test_prompt
            }]
        )
        end_time = time.time()
        
        return {
            'model': model_name,
            'response_time': end_time - start_time,
            'response_length': len(response['message']['content']),
            'tokens_per_second': len(response['message']['content'].split()) / (end_time - start_time)
        }
    except Exception as e:
        return {'error': str(e)}

benchmark_button = mo.ui.button(
    label="Run Benchmark",
    on_click=lambda: benchmark_model(selected_model.value)
)

mo.vstack([
    mo.md("## Performance Benchmark"),
    benchmark_button,
    mo.md("**Benchmark Results:**"),
    mo.md(str(benchmark_button.value) if benchmark_button.value else "Click 'Run Benchmark' to test performance.")
])
```

## Usage Tips

```python
mo.md("""
## Usage Tips

### Getting Started
1. **Install a model** using the model installation section above
2. **Select the model** for your chat or code generation
3. **Start chatting** or generating code!

### Recommended Models
- **For general chat:** `llama3.2:3b` or `phi3:mini`
- **For code generation:** `codellama:7b` or `qwen2.5:3b`
- **For lightweight use:** `llama3.2:1b` or `gemma2:2b`

### Performance Tips
- Smaller models (1B-3B parameters) are faster but less capable
- Larger models (7B+ parameters) are more capable but slower
- Use GPU acceleration if available (uncomment GPU settings in docker-compose.yml)
- Monitor memory usage with larger models

### Troubleshooting
- If models don't appear, try restarting the Ollama service
- Check Docker logs: `docker-compose logs ollama`
- Ensure sufficient disk space for model downloads
- Monitor system resources during model operations
""")
```
