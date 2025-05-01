# app/llm_provider.py
"""
Initializes and provides configured LangChain LLM instances for different tasks.

Reads configuration from config.settings and instantiates the appropriate
LangChain LLM or ChatModel classes (e.g., ChatOpenAI, HuggingFaceEndpoint, Ollama)
or custom wrappers (e.g., Phi3OnnxLocal).

Exports:
    llm: The primary LangChain LLM/ChatModel instance for chat/troubleshooting.
    classifier_llm: The LangChain LLM/ChatModel instance used for data classification.
"""

# --- Imports ---
# LangChain Model Wrappers
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import HuggingFaceHub

# LangChain Core Types
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import Generation, LLMResult

# Standard Libraries & Application Modules
from config.settings import settings
from app.logger import logger
from typing import Optional, Union, List, Any, Dict
import requests # For custom Phi3OnnxLocal class
import json


# --- Custom LLM Class for Local Phi-3 ONNX Server ---
class Phi3OnnxLocal(LLM):
    """
    Custom LangChain LLM wrapper to interact with a simple Flask API
    server (like phi3_server.py) hosting a local ONNX model.

    Assumes the server has a '/generate' endpoint accepting POST requests
    with {"prompt": "..."} JSON and returning {"generated_text": "..."}.
    """
    server_url: str # The full URL to the '/generate' endpoint

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "phi3_onnx_local_wrapper"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        try:
            logger.debug(f"Sending request to {self.server_url} with prompt: '{prompt[:100]}...'")
            response = requests.post(
                self.server_url,
                json={"prompt": prompt},
                timeout=120
            )
            response.raise_for_status() # Check for 4xx/5xx first

            # --- Attempt to decode JSON ---
            try:
                result = response.json()
            except json.JSONDecodeError as e: # More specific catch here
                logger.error(f"Invalid JSON response from Phi3 server at {self.server_url}: {e}")
                # Raise the specific ValueError the test expects
                raise ValueError("Invalid JSON response from Phi3 server.") from e

            # --- Process valid JSON ---
            if "generated_text" in result:
                return result["generated_text"]
            elif "error" in result:
                logger.error(f"Phi3 server returned error: {result['error']}")
                raise RuntimeError(f"Phi3 server error: {result['error']}")
            else:
                logger.error(f"Unexpected JSON response format from Phi3 server: {result}")
                raise ValueError("Invalid response format received from Phi3 server.")

        # --- Handle Request/Connection/Timeout errors ---
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out connecting to Phi3 server at {self.server_url}")
            raise RuntimeError(f"Timeout connecting to Phi3 server ({self.server_url}).") from None
        except requests.exceptions.RequestException as e: # Catches connection errors, HTTPError, etc.
            logger.error(f"Failed to connect or communicate with Phi3 server at {self.server_url}: {e}")
            raise RuntimeError(f"Failed to connect to Phi3 server: {e}") from e
        # --- Catch any other unexpected errors ---
        except Exception as e:
            logger.exception(f"An unexpected error occurred during custom Phi3 local LLM call: {e}")
            # Keep existing ValueError or raise a generic RuntimeError?
            # Let's keep raising the original specific ValueErrors if they occur above
            if isinstance(e, ValueError):
                raise # Re-raise specific ValueErrors from JSON handling
            raise RuntimeError(f"Error calling Phi3 local LLM: {e}") from e


# --- Helper Function to Instantiate LLM based on Settings ---
def _get_llm_instance(
    provider: str,
    model: Optional[str],
    api_key: Optional[str], # For OpenAI or OpenAI-compatible API keys
    api_url: Optional[str], # For Base URLs of local servers (Ollama, OpenAI-comp, Phi3)
    hf_api_key: Optional[str] = None # Specific key for Hugging Face Hub/Endpoint
    ) -> Union[BaseChatModel, LLM]:
    """
    Instantiates and returns the appropriate LangChain LLM/ChatModel object
    based on the specified provider and configuration.

    Args:
        provider: The name of the LLM provider (e.g., 'openai', 'ollama', 'huggingface').
        model: The specific model name/ID to use for the provider.
        api_key: API key for OpenAI or compatible services.
        api_url: Base URL for local LLM servers.
        hf_api_key: Specific API token for Hugging Face services.

    Returns:
        An initialized LangChain LLM or BaseChatModel instance.

    Raises:
        ValueError: If required configuration for the selected provider is missing
                    or if the provider name is unsupported.
    """

    logger.info(f"Initializing LLM instance: Provider='{provider}', Model='{model}', URL='{api_url}'")

    # --- Provider specific instantiation logic ---
    logger.info(f"Initializing LLM instance: Provider='{provider}', Model='{model}', URL='{api_url}'")

    # --- Provider specific instantiation logic ---
    if provider == "openai":
        if not api_key: raise ValueError(f"OPENAI_API_KEY setting required for provider '{provider}'.")
        if not model: raise ValueError(f"OPENAI_MODEL setting required for provider '{provider}'.")
        logger.info(f"Using ChatOpenAI with model '{model}'.")
        # Increase default timeout for OpenAI if needed, e.g., request_timeout=120
        return ChatOpenAI(model=model, temperature=0.7, api_key=api_key)

    elif provider == "ollama":
        if not api_url: raise ValueError(f"LOCAL_LLM_URL setting required for provider '{provider}'.")
        if not model: raise ValueError(f"LOCAL_LLM_MODEL setting required for provider '{provider}'.")
        logger.info(f"Using ChatOllama: Model='{model}', Base URL='{api_url}'.")
        # Ensure api_url is a string for base_url
        return ChatOllama(model=model, base_url=str(api_url), temperature=0.7) # Ollama is usually a ChatModel

    elif provider == "openai_compatible_local":
        if not api_url: raise ValueError(f"LOCAL_LLM_URL setting required for provider '{provider}'.")
        if not model: raise ValueError(f"LOCAL_LLM_MODEL setting required for provider '{provider}'.")
        logger.info(f"Using ChatOpenAI (compatible): Model='{model}', Base URL='{api_url}'.")
        # Most OpenAI-compatible servers align with ChatOpenAI interface
        return ChatOpenAI(
            model=model,
            base_url=str(api_url),
            api_key=api_key or "not-needed", # Pass key if provided, else dummy
            temperature=0.7
        )

    elif provider == "phi3_onnx_local":
        if not api_url: raise ValueError(f"LOCAL_LLM_URL setting required for provider '{provider}'.")
        # Construct the full endpoint URL for the custom server
        server_endpoint = f"{str(api_url).strip('/')}/generate"
        logger.info(f"Using Custom Phi3OnnxLocal wrapper pointing to: {server_endpoint}")
        # Instantiate the custom class
        return Phi3OnnxLocal(server_url=server_endpoint) # Returns a base LLM

    elif provider == "huggingface":
        if not hf_api_key: raise ValueError(f"HUGGINGFACE_API_KEY setting required for provider '{provider}'.")
        if not model: raise ValueError(f"HUGGINGFACE_MODEL setting required for provider '{provider}'.")
        logger.info(f"Using HuggingFaceHub (deprecated): Model='{model}'.")
        # Use the deprecated HuggingFaceHub class
        return HuggingFaceHub(
            repo_id=model,
            huggingfacehub_api_token=hf_api_key, # Correct parameter name for Hub
            model_kwargs={"temperature": 0.1, "max_new_tokens": 100}
        )
    else:
        # Handle unsupported provider configuration
        raise ValueError(f"Unsupported LLM provider configured in settings: '{provider}'")


# --- Instantiate Shared LLM Instances ---
# These instances are created once when the module is imported and reused.

# --- 1. Main Chat LLM Instance (`llm`) ---
# Used for the core troubleshooting conversation in app/chains.py
try:
    # Determine configuration based on settings.chat_provider
    _chat_provider = settings.chat_provider
    _chat_model_name = None
    _chat_api_key = None
    _chat_api_url = None
    _chat_hf_api_key = None

    if _chat_provider == 'openai':
        _chat_model_name = settings.openai_model
        _chat_api_key = settings.openai_api_key
    elif _chat_provider == 'huggingface':
        _chat_model_name = settings.huggingface_model
        _chat_hf_api_key = settings.huggingface_api_key
    elif _chat_provider in ['ollama', 'openai_compatible_local', 'phi3_onnx_local']:
        _chat_api_url = settings.local_llm_url
        _chat_model_name = settings.local_llm_model
        if _chat_provider == 'openai_compatible_local':
            _chat_api_key = settings.openai_api_key
    # Add logic for other providers if needed

    # Call the helper function to get the instance
    llm: Union[BaseChatModel, LLM] = _get_llm_instance(
        provider=_chat_provider,
        model=_chat_model_name,
        api_key=_chat_api_key,
        api_url=_chat_api_url,
        hf_api_key=_chat_hf_api_key
    )
    logger.info(f"Successfully initialized main chat LLM (Provider: {_chat_provider}, Model: {_chat_model_name or 'Default'}).")

except Exception as e:
    logger.exception(f"CRITICAL: Failed to initialize main chat LLM. Application might not function correctly. Error: {e}")
    # Raising exception stops the application, which is usually desired if the core LLM fails
    raise RuntimeError(f"Could not initialize the main chat LLM.") from e


# --- 2. Classifier LLM Instance (`classifier_llm`) ---
# Used specifically for the data classification task in app/data_classifier.py
try:
    # Determine configuration based on settings.classifier_provider
    _classifier_provider = settings.classifier_provider
    _classifier_model_name = None
    _classifier_api_key = None
    _classifier_api_url = None
    _classifier_hf_api_key = None

    if _classifier_provider == 'openai':
        # Use specific classifier model from settings, or fall back to main OpenAI model
        _classifier_model_name = settings.classifier_model or settings.openai_model
        _classifier_api_key = settings.openai_api_key
    elif _classifier_provider == 'huggingface':
        _classifier_model_name = settings.huggingface_model
        _classifier_hf_api_key = settings.huggingface_api_key
    elif _classifier_provider in ['ollama', 'openai_compatible_local', 'phi3_onnx_local']:
        _classifier_api_url = settings.local_llm_url
        _classifier_model_name = settings.local_llm_model # Use local model name if set
        if _classifier_provider == 'openai_compatible_local':
            _classifier_api_key = settings.openai_api_key
    # Add logic for other providers if needed

    # Call the helper function to get the instance
    classifier_llm: Union[BaseChatModel, LLM] = _get_llm_instance(
        provider=_classifier_provider,
        model=_classifier_model_name,
        api_key=_classifier_api_key,
        api_url=_classifier_api_url,
        hf_api_key=_classifier_hf_api_key
    )

    # Override temperature for classification tasks if the provider/model allows direct setting
    # HuggingFaceEndpoint sets temperature during initialization via model_kwargs
    if hasattr(classifier_llm, 'temperature') and _classifier_provider != 'huggingface':
         classifier_llm.temperature = 0.0
         logger.debug(f"Set classifier LLM temperature to 0.0 for provider '{_classifier_provider}'.")

    logger.info(f"Successfully initialized classifier LLM (Provider: {_classifier_provider}, Model: {_classifier_model_name or 'Default'}).")

except Exception as e:
    logger.exception(f"CRITICAL: Failed to initialize classifier LLM. Data classification may fail. Error: {e}")
    # Raising exception stops the application
    raise RuntimeError(f"Could not initialize the classifier LLM.") from e