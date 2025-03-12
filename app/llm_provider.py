import requests
import openai
from app.logger import logger
from config.settings import settings
from typing import Any


class LLMParsingError(Exception):
    """Custom exception for LLM response parsing errors."""
    pass

class LLMProvider:
    """Unified interface for different LLM providers."""

    def __init__(self):
        self.provider = settings.llm_provider
        self.api_key = getattr(settings, f"{self.provider}_api_key")
        self.model = getattr(settings, f"{self.provider}_model")
        self.api_url = getattr(settings, f"{self.provider}_api_url", None) # Default to None if not specified

        if not self.api_key and self.provider != "huggingface":
            raise ValueError(f"Missing API key for {self.provider}. Set the correct environment variable.")

        if not self.model:
            raise ValueError(f"Missing model for {self.provider}. Set the correct environment variable.")

        logger.info(f"Using LLM Provider: {self.provider}")
        logger.info(f"Using LLM Model: {self.model}")

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
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _query_openai(self, prompt: str) -> str:
        """Handles OpenAI API calls."""
        try:
            openai.api_key = self.api_key # set api key here
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse_response(response)
        except openai.OpenAIError as e:
            logger.error(f"OpenAI Query Failed: {e}")
            return f"OpenAI query failed: {e}"

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
                logger.error(f"Anthropic API Error: {response_json}")
                return f"Anthropic query failed: {response_json}"

            return self._parse_response(response_json)
        except requests.RequestException as e:
            logger.error(f"Anthropic Query Failed: {e}")
            return f"Anthropic query failed: {e}"

    def _query_huggingface(self, prompt: str) -> str:
        """Handles Hugging Face API calls."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"inputs": prompt, "parameters": {"max_length": 300, "return_full_text": False}}

            # Increase timeout here.  Default is probably 5 seconds.
            response = requests.post(f"{self.api_url}/{self.model}", json=payload, headers=headers, timeout=90)  # Example: 90 seconds

            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"Hugging Face API Error: {response_json}")
                return f"Hugging Face query failed: {response_json}"  # Return error as string

            return self._parse_response(response_json)

        except requests.RequestException as e:
            logger.error(f"Hugging Face Query Failed: {e}")
            return f"Hugging Face query failed: {e}"  # Return error as string


    def _query_mistral(self, prompt: str) -> str:
        """Handles Mistral API calls."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"Mistral API Error: {response_json}")
                return f"Mistral query failed: {response_json}"
            return self._parse_response(response_json)

        except requests.RequestException as e:
            logger.error(f"Mistral Query Failed: {e}")
            return f"Mistral query failed: {e}"

    def _query_deepseek(self, prompt: str) -> str:
        """Handles DeepSeek API calls."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"DeepSeek API Error: {response_json}")
                return f"DeepSeek query failed: {response_json}"

            return self._parse_response(response_json)

        except requests.RequestException as e:
            logger.error(f"DeepSeek Query Failed: {e}")
            return f"DeepSeek query failed: {e}"

    def _parse_response(self, response: Any) -> str:
        """Parses the LLM response and extracts the generated text."""
        try:
            # More robust and flexible parsing logic:
            if isinstance(response, list) and response:
                first_item = response[0]
                if isinstance(first_item, dict):
                    if "generated_text" in first_item:
                        text = first_item["generated_text"].strip()
                        text = text.replace("<p>", "").replace("</p>", "").strip()  # Remove HTML tags
                        return text
                    elif "text" in first_item:  # Fallback option
                        text = first_item["text"].strip()
                        text = text.replace("<p>", "").replace("</p>", "").strip()  # Remove HTML tags
                        return text
                    # Add more fallback keys as needed based on potential responses.
                # Consider adding checks for other response types (e.g., if it's a string directly)

            # Check if response is already a string.
            if isinstance(response, str):
                return response
            raise LLMParsingError(f"Unexpected LLM response format: {response}")

        except Exception as e:
            raise LLMParsingError(f"Error during LLM response parsing: {e}") from e