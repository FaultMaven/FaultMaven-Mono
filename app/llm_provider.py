import os
import requests
import openai
from app.logger import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get selected LLM provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# API Keys
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "mistral": os.getenv("MISTRAL_API_KEY"),
    "deepseek": os.getenv("DEEPSEEK_API_KEY"),
    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
}

# Models per provider
LLM_MODELS = {
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-3-opus"),
    "mistral": os.getenv("MISTRAL_MODEL", "mistralai/Mistral-7B-Instruct-v0.1"),
    "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    "huggingface": os.getenv("HUGGINGFACE_MODEL", "tiiuae/falcon-7b-instruct"),
}

# API URLs for non-OpenAI models
API_URLS = {
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "mistral": "https://api.mistral.ai/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "huggingface": "https://api-inference.huggingface.co/models/",
}


class LLMProvider:
    """Unified interface for different LLM providers."""

    def __init__(self):
        self.provider = LLM_PROVIDER
        self.api_key = API_KEYS.get(self.provider)
        self.model = LLM_MODELS.get(self.provider)
        self.api_url = API_URLS.get(self.provider)

        if not self.api_key and self.provider != "huggingface":  # Hugging Face allows some public models
            raise ValueError(f"❌ Missing API key for {self.provider}. Set the correct environment variable.")

        if not self.model:
            raise ValueError(f"❌ Missing model for {self.provider}. Set the correct environment variable.")

        logger.info(f"✅ Using LLM Provider: {self.provider}")
        logger.info(f"✅ Using LLM Model: {self.model}")

    def query(self, prompt: str):
        """Routes query to the selected LLM provider."""
        if self.provider == "openai":
            return self._query_openai(prompt)
        elif self.provider == "anthropic":
            return self._query_anthropic(prompt)
        elif self.provider == "mistral":
            return self._query_mistral(prompt)
        elif self.provider == "deepseek":
            return self._query_deepseek(prompt)
        elif self.provider == "huggingface":
            return self._query_huggingface(prompt)
        else:
            raise ValueError(f"❌ Unsupported LLM provider: {self.provider}")

    def _query_openai(self, prompt: str) -> str:
        """Handles OpenAI API calls."""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except openai.OpenAIError as e:
            logger.error(f"❌ OpenAI Query Failed: {e}")
            return {"error": "OpenAI query failed", "details": str(e)}

    def _query_anthropic(self, prompt: str) -> str:
        """Handles Anthropic API calls."""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"❌ Anthropic API Error: {response_json}")
                return {"error": "Anthropic query failed", "details": response_json}

            return response_json["content"]
        except requests.RequestException as e:
            logger.error(f"❌ Anthropic Query Failed: {e}")
            return {"error": "Anthropic query failed", "details": str(e)}

    def _query_huggingface(self, prompt: str) -> str:
        """Handles Hugging Face API calls."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"inputs": prompt, "parameters": {"max_length": 300}}

            response = requests.post(f"{self.api_url}{self.model}", json=payload, headers=headers)

            # DEBUG: Print raw response
            logger.info(f"🔍 Hugging Face Raw Response: {response.status_code} - {response.text}")

            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"❌ Hugging Face API Error: {response_json}")
                return {"error": "Hugging Face query failed", "details": response_json}

            return response_json[0]["generated_text"]

        except requests.RequestException as e:
            logger.error(f"❌ Hugging Face Query Failed: {e}")
            return {"error": "Hugging Face query failed", "details": str(e)}

    def _query_mistral(self, prompt: str) -> str:
        """Handles Mistral API calls."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"❌ Mistral API Error: {response_json}")
                return {"error": "Mistral query failed", "details": response_json}

            return response_json["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"❌ Mistral Query Failed: {e}")
            return {"error": "Mistral query failed", "details": str(e)}

    def _query_deepseek(self, prompt: str) -> str:
        """Handles DeepSeek API calls."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"❌ DeepSeek API Error: {response_json}")
                return {"error": "DeepSeek query failed", "details": response_json}

            return response_json["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"❌ DeepSeek Query Failed: {e}")
            return {"error": "DeepSeek query failed", "details": str(e)}


