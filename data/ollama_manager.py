#!/usr/bin/env python3
"""
Ollama Management Utility for Marimo Docker Setup

This script provides utilities for managing Ollama models and checking service status.
"""

import ollama
import requests
import json
import time
from typing import List, Dict, Any, Optional

class OllamaManager:
    """Manager class for Ollama operations."""
    
    def __init__(self, host: str = "http://ollama:11434"):
        """Initialize Ollama manager with host URL."""
        self.host = host
        self.client = ollama.Client(host=host)
    
    def check_connection(self) -> Dict[str, Any]:
        """Check if Ollama service is running and accessible."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return {
                    'status': 'connected',
                    'models_count': len(models),
                    'models': [model['name'] for model in models]
                }
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except requests.exceptions.ConnectionError:
            return {'status': 'error', 'message': 'Connection refused - Ollama not running'}
        except requests.exceptions.Timeout:
            return {'status': 'error', 'message': 'Connection timeout'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models with details."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def install_model(self, model_name: str) -> Dict[str, Any]:
        """Install a model with progress tracking."""
        try:
            print(f"Installing {model_name}... This may take several minutes.")
            
            # Start the pull operation
            response = requests.post(
                f"{self.host}/api/pull",
                json={'name': model_name},
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if 'status' in data:
                            print(f"Status: {data['status']}")
                        if 'completed' in data and 'total' in data:
                            progress = (data['completed'] / data['total']) * 100
                            print(f"Progress: {progress:.1f}%")
                
                return {'status': 'success', 'message': f'Successfully installed {model_name}'}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def remove_model(self, model_name: str) -> Dict[str, Any]:
        """Remove a model."""
        try:
            response = requests.delete(f"{self.host}/api/delete", json={'name': model_name})
            if response.status_code == 200:
                return {'status': 'success', 'message': f'Successfully removed {model_name}'}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def chat(self, model: str, message: str, stream: bool = False) -> Dict[str, Any]:
        """Send a chat message to a model."""
        try:
            response = self.client.chat(
                model=model,
                messages=[{'role': 'user', 'content': message}],
                stream=stream
            )
            
            if stream:
                return {'status': 'success', 'stream': response}
            else:
                return {
                    'status': 'success',
                    'response': response['message']['content']
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def benchmark_model(self, model: str, test_prompt: str = "Hello, how are you?") -> Dict[str, Any]:
        """Benchmark a model's performance."""
        try:
            start_time = time.time()
            response = self.chat(model, test_prompt)
            end_time = time.time()
            
            if response['status'] == 'success':
                response_text = response['response']
                response_time = end_time - start_time
                word_count = len(response_text.split())
                
                return {
                    'status': 'success',
                    'model': model,
                    'response_time': response_time,
                    'response_length': len(response_text),
                    'word_count': word_count,
                    'words_per_second': word_count / response_time if response_time > 0 else 0
                }
            else:
                return response
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ollama Management Utility')
    parser.add_argument('--host', default='http://ollama:11434', help='Ollama host URL')
    parser.add_argument('--action', choices=['status', 'list', 'install', 'remove', 'chat', 'benchmark'], 
                       required=True, help='Action to perform')
    parser.add_argument('--model', help='Model name for install/remove/chat/benchmark')
    parser.add_argument('--message', help='Message for chat action')
    
    args = parser.parse_args()
    
    manager = OllamaManager(args.host)
    
    if args.action == 'status':
        status = manager.check_connection()
        print(json.dumps(status, indent=2))
    
    elif args.action == 'list':
        models = manager.list_models()
        if models:
            print("Available models:")
            for model in models:
                size_gb = model.get('size', 0) / (1024**3)
                print(f"  - {model['name']} ({size_gb:.2f} GB)")
        else:
            print("No models installed.")
    
    elif args.action == 'install':
        if not args.model:
            print("Error: --model required for install action")
            return
        result = manager.install_model(args.model)
        print(json.dumps(result, indent=2))
    
    elif args.action == 'remove':
        if not args.model:
            print("Error: --model required for remove action")
            return
        result = manager.remove_model(args.model)
        print(json.dumps(result, indent=2))
    
    elif args.action == 'chat':
        if not args.model or not args.message:
            print("Error: --model and --message required for chat action")
            return
        result = manager.chat(args.model, args.message)
        print(json.dumps(result, indent=2))
    
    elif args.action == 'benchmark':
        if not args.model:
            print("Error: --model required for benchmark action")
            return
        result = manager.benchmark_model(args.model, args.message or "Hello, how are you?")
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
