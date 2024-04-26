import os
import json
import requests
from configparser import ConfigParser
from openai import OpenAI  # Import OpenAI if you're using GPT directly.

class APIKeyManager:
    _keys = None

    @classmethod
    def load_keys(cls):
        if cls._keys is None:
            config = ConfigParser()
            config_file_directory = os.getenv("API_KEY_FILE_PATH", ".")
            config_file_name = "api_key.conf"
            config_file_path = os.path.join(config_file_directory, config_file_name)
            config.read(config_file_path)
            cls._keys = {
                'palm2': config.get('API_KEYS', 'GOOGLE_API_KEY', fallback=None),
                'gemini-pro': config.get('API_KEYS', 'GOOGLE_API_KEY', fallback=None),
                'mistral': config.get('API_KEYS', 'MISTRAL_API_KEY', fallback=None),
                'openai': config.get('API_KEYS', 'OPENAI_API_KEY', fallback=None),
                'anthropic': config.get('API_KEYS', 'ANTHROPIC_API_KEY', fallback=None)
            }
        return cls._keys

def call_LLM(model, prompt):
    api_keys = APIKeyManager.load_keys()
    api_key = api_keys.get(model)
    headers = {'Content-Type': 'application/json'}
    if model in ['openai', 'mistral', 'anthropic']:  # These models use Bearer tokens
        headers['Authorization'] = f'Bearer {api_key}'

    url, data = None, None

    if model == 'palm2':
        url = f"https://generativelanguage.googleapis.com/v1beta3/models/text-bison-001:generateText?key={api_key}"
        data = {"prompt": {"text": prompt}}
    elif model == 'gemini-pro':
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}
    elif model == 'mistral':
        url = "https://api.mistral.ai/v1/chat/completions"
        data = {"model": "mistral-medium", "messages": [{"role": "user", "content": prompt}]}
    elif model == 'openai':
        url = "https://api.openai.com/v1/chat/completions"
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    elif model == 'anthropic':
        url = "https://api.anthropic.com/v1/messages"
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }

    if url and data:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return extract_text_from_response(model, response.json())
        else:
            return f'Error: {response.status_code}, {response.text}'

    return 'Model or parameters not correctly specified'

def extract_text_from_response(model, response):
    """Extract text content from the LLM response based on the model."""
    if model == 'palm2' or model == 'gemini-pro':
        # Assuming response format is {'candidates': [{'output': '...'}]}
        return response.get('candidates', [{}])[0].get('output', '')
    elif model == 'mistral':
        return response.get('choices', [{}])[0].get('message', {}).get('content', '')
    elif model == 'openai' or model == 'anthropic':
        return response.get('choices', [{}])[0].get('message', {}).get('content', '')
    return "Unsupported model or incorrect response format"

