# tests/test_llm_provider.py
"""
Unit tests for the app.llm_provider module, focusing on the custom
Phi3OnnxLocal class and potentially the _get_llm_instance helper later.
"""

import pytest
import requests
import requests_mock # Import the mocking library
import json
from unittest.mock import AsyncMock
from unittest.mock import MagicMock 

import inspect
from app.llm_provider import _get_llm_instance, Phi3OnnxLocal # Import the function and custom class
from config.settings import settings # Import the settings instance to mock its attributes
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import HuggingFaceHub
from pydantic import HttpUrl # Import for type consistency when mocking URLs

# Import the class to test and potentially other components if needed
from app.llm_provider import Phi3OnnxLocal
# Note: We don't need to import 'llm' or 'classifier_llm' here,
# as we are testing the class definition itself.

# Define constants for testing
MOCK_SERVER_URL_BASE = "http://mock-phi3-server:5000"
MOCK_SERVER_ENDPOINT = f"{MOCK_SERVER_URL_BASE}/generate"
TEST_PROMPT = "What is the status of service X?"

# --- Tests for Phi3OnnxLocal._call ---

def test_phi3onnxlocal_call_success(requests_mock):
    """Test successful call to the _call method."""
    # Arrange
    expected_response_text = "Service X is running normally."
    mock_response_json = {"generated_text": expected_response_text}
    # Configure requests_mock to intercept POST requests to the endpoint
    requests_mock.post(MOCK_SERVER_ENDPOINT, json=mock_response_json, status_code=200)
    # Instantiate the class with the mock URL
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Act
    result = llm_instance._call(TEST_PROMPT) # Directly call the method under test

    # Assert
    # 1. Check the returned value
    assert result == expected_response_text
    # 2. Check the request mock history
    history = requests_mock.request_history
    assert len(history) == 1
    assert history[0].method == 'POST'
    assert history[0].url == MOCK_SERVER_ENDPOINT
    assert history[0].json() == {"prompt": TEST_PROMPT}

def test_phi3onnxlocal_call_server_error_json(requests_mock):
    """Test handling of a server error returned in JSON format (causes HTTPError first)."""
    mock_error_json = {"error": "Model processing failed"}
    requests_mock.post(MOCK_SERVER_ENDPOINT, json=mock_error_json, status_code=500)
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Expect RuntimeError raised by the RequestException handler due to raise_for_status()
    with pytest.raises(RuntimeError) as excinfo:
        llm_instance._call(TEST_PROMPT)
    # Check the beginning of the error message
    assert "Failed to connect to Phi3 server" in str(excinfo.value)
    # Optionally check the nested exception type if needed
    # assert isinstance(excinfo.value.__cause__, requests.exceptions.HTTPError)
    assert requests_mock.call_count == 1

def test_phi3onnxlocal_call_server_error_http(requests_mock):
    """Test handling of a generic HTTP error (e.g., 503 Service Unavailable)."""
    # Arrange
    requests_mock.post(MOCK_SERVER_ENDPOINT, status_code=503, text="Service Unavailable")
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Act & Assert: raise_for_status should trigger HTTPError, caught and re-raised as RuntimeError
    # The specific message comes from requests library based on status code
    with pytest.raises(RuntimeError) as excinfo:
         llm_instance._call(TEST_PROMPT)
    # Check that the underlying cause is likely related to requests
    assert "Failed to connect to Phi3 server" in str(excinfo.value) or "503 Server Error" in str(excinfo.value)
    assert requests_mock.call_count == 1


def test_phi3onnxlocal_call_connection_error(requests_mock):
    """Test handling of a connection error."""
    # Arrange
    requests_mock.post(MOCK_SERVER_ENDPOINT, exc=requests.exceptions.ConnectionError("Connection refused"))
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Act & Assert
    with pytest.raises(RuntimeError, match=r"Failed to connect to Phi3 server: Connection refused"):
        llm_instance._call(TEST_PROMPT)
    assert requests_mock.call_count == 1

def test_phi3onnxlocal_call_timeout(requests_mock):
    """Test handling of a request timeout."""
    # Arrange
    requests_mock.post(MOCK_SERVER_ENDPOINT, exc=requests.exceptions.Timeout("Request timed out"))
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Act & Assert
    with pytest.raises(RuntimeError, match=r"Timeout connecting to Phi3 server"):
        llm_instance._call(TEST_PROMPT)
    assert requests_mock.call_count == 1

def test_phi3onnxlocal_call_invalid_json_response(requests_mock):
    """Test handling when the server returns non-JSON content with a 200 status."""
    # Arrange
    requests_mock.post(MOCK_SERVER_ENDPOINT, status_code=200, text="<html Error Page>")
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Act & Assert: Expect ValueError from json.JSONDecodeError catch block
    with pytest.raises(ValueError, match="Invalid JSON response from Phi3 server"):
        llm_instance._call(TEST_PROMPT)
    assert requests_mock.call_count == 1

def test_phi3onnxlocal_call_missing_key_response(requests_mock):
    """Test handling when the server returns valid JSON but missing the expected key."""
    # Arrange
    mock_response_json = {"other_key": "some data", "status": "complete"}
    requests_mock.post(MOCK_SERVER_ENDPOINT, json=mock_response_json, status_code=200)
    llm_instance = Phi3OnnxLocal(server_url=MOCK_SERVER_ENDPOINT)

    # Act & Assert: Expect ValueError raised by the logic checking the JSON structure
    with pytest.raises(ValueError, match=r"Invalid response format received from Phi3 server."):
        llm_instance._call(TEST_PROMPT)

    # Verify the request was still made
    assert requests_mock.call_count == 1


# === Tests for _get_llm_instance ===

# --- OpenAI Tests ---
def test_get_llm_instance_openai_success(mocker):
    """Verify returns ChatOpenAI instance when provider is 'openai' and settings are valid."""
    # Arrange: Mock necessary settings attributes
    mocker.patch.object(settings, 'openai_api_key', "fake-openai-key")
    # mocker.patch.object(settings, 'openai_model', "gpt-test") # Already has default

    # Act
    llm_instance = _get_llm_instance(
        provider="openai",
        model=settings.openai_model, # Use model from settings
        api_key=settings.openai_api_key, # Use mocked key
        api_url=None,
        hf_api_key=None
    )

    # Assert
    assert isinstance(llm_instance, ChatOpenAI)
    assert llm_instance.model_name == settings.openai_model
    assert llm_instance.openai_api_key.get_secret_value() == "fake-openai-key"

def test_get_llm_instance_openai_missing_key(mocker):
    """Verify ValueError if provider is 'openai' but key is missing."""
    mocker.patch.object(settings, 'openai_api_key', None) # Ensure key is None
    # mocker.patch.object(settings, 'openai_model', "gpt-test")

    with pytest.raises(ValueError, match=r"OPENAI_API_KEY setting required for provider 'openai'"):
        _get_llm_instance(provider="openai", model=settings.openai_model, api_key=None, api_url=None, hf_api_key=None)

def test_get_llm_instance_openai_missing_model(mocker):
    """Verify ValueError if provider is 'openai' but model is missing."""
    mocker.patch.object(settings, 'openai_api_key', "fake-key")

    with pytest.raises(ValueError, match=r"OPENAI_MODEL setting required for provider 'openai'"):
        _get_llm_instance(provider="openai", model=None, api_key="fake-key", api_url=None, hf_api_key=None)

# --- Ollama Tests ---
def test_get_llm_instance_ollama_success(mocker):
    """Verify returns ChatOllama instance when provider is 'ollama' and settings are valid."""
    mock_url = HttpUrl("http://mock-ollama:11434")
    mock_model = "test-llama"
    mocker.patch.object(settings, 'local_llm_url', mock_url)
    mocker.patch.object(settings, 'local_llm_model', mock_model)

    llm_instance = _get_llm_instance(
        provider="ollama",
        model=mock_model,
        api_key=None,
        api_url=mock_url, # Pass the mocked URL
        hf_api_key=None
    )
    assert isinstance(llm_instance, ChatOllama)
    # Check attributes specific to ChatOllama if possible/needed
    # assert llm_instance.model == mock_model # (Attribute name might differ based on version)

def test_get_llm_instance_ollama_missing_url(mocker):
    """Verify ValueError if provider is 'ollama' but URL is missing."""
    mocker.patch.object(settings, 'local_llm_url', None)
    mocker.patch.object(settings, 'local_llm_model', 'test-model')
    with pytest.raises(ValueError, match=r"LOCAL_LLM_URL setting required for provider 'ollama'"):
        _get_llm_instance(provider="ollama", model='test-model', api_key=None, api_url=None, hf_api_key=None)

def test_get_llm_instance_ollama_missing_model(mocker):
    """Verify ValueError if provider is 'ollama' but model is missing."""
    mock_url = HttpUrl("http://mock-ollama:11434")
    mocker.patch.object(settings, 'local_llm_url', mock_url)
    mocker.patch.object(settings, 'local_llm_model', None)
    with pytest.raises(ValueError, match=r"LOCAL_LLM_MODEL setting required for provider 'ollama'"):
        _get_llm_instance(provider="ollama", model=None, api_key=None, api_url=mock_url, hf_api_key=None)


# --- HuggingFace Tests ---
def test_get_llm_instance_huggingface_success(mocker):
    """Verify _get_llm_instance attempts to init HuggingFaceHub with correct args."""
    mock_key = "fake-hf-key"
    mock_model = "hf-test/model"
    # Mock settings attributes needed for this path
    # mocker.patch.object(settings, 'huggingface_api_key', mock_key) # Not needed if passing directly
    # mocker.patch.object(settings, 'huggingface_model', mock_model) # Not needed if passing directly

    # --- Mock the HuggingFaceHub class constructor ---
    # Patch the class where it's imported/used in app.llm_provider
    mock_hub_constructor = mocker.patch(
        'app.llm_provider.HuggingFaceHub',
        return_value=MagicMock(spec=HuggingFaceHub) # Return a mock object pretending to be a Hub instance
    )

    # Act: Call the function which should now call the mocked constructor
    llm_instance = _get_llm_instance(
        provider="huggingface",
        model=mock_model,
        api_key=None,
        api_url=None,
        hf_api_key=mock_key # Pass the key here
    )

    # Assert
    # 1. Check that our mock constructor was called
    mock_hub_constructor.assert_called_once()

    # 2. Check the arguments passed to the constructor
    call_args, call_kwargs = mock_hub_constructor.call_args
    assert call_kwargs.get('repo_id') == mock_model
    assert call_kwargs.get('huggingfacehub_api_token') == mock_key
    # Check model_kwargs if necessary
    assert "temperature" in call_kwargs.get('model_kwargs', {})
    assert "max_new_tokens" in call_kwargs.get('model_kwargs', {})

    # 3. Check the returned object is the mock we created (optional)
    assert isinstance(llm_instance, MagicMock)

def test_get_llm_instance_huggingface_missing_key(mocker):
    """Verify ValueError if provider is 'huggingface' but key is missing."""
    mocker.patch.object(settings, 'huggingface_api_key', None)
    mocker.patch.object(settings, 'huggingface_model', 'hf-model')
    with pytest.raises(ValueError, match=r"HUGGINGFACE_API_KEY setting required"):
        _get_llm_instance(provider="huggingface", model='hf-model', api_key=None, api_url=None, hf_api_key=None)

def test_get_llm_instance_huggingface_missing_model(mocker):
    """Verify ValueError if provider is 'huggingface' but model is missing."""
    mocker.patch.object(settings, 'huggingface_api_key', 'fake-key')
    mocker.patch.object(settings, 'huggingface_model', None)
    with pytest.raises(ValueError, match=r"HUGGINGFACE_MODEL setting required"):
        _get_llm_instance(provider="huggingface", model=None, api_key=None, api_url=None, hf_api_key='fake-key')


# --- Phi3OnnxLocal Tests ---
def test_get_llm_instance_phi3_success(mocker):
    """Verify returns Phi3OnnxLocal instance when provider is 'phi3_onnx_local'."""
    mock_url = HttpUrl("http://mock-phi3:5000")
    mocker.patch.object(settings, 'local_llm_url', mock_url)

    llm_instance = _get_llm_instance(
        provider="phi3_onnx_local",
        model=None, # Model name not needed by this provider's init
        api_key=None,
        api_url=mock_url,
        hf_api_key=None
    )
    assert isinstance(llm_instance, Phi3OnnxLocal)
    expected_endpoint = f"{str(mock_url).strip('/')}/generate"
    assert llm_instance.server_url == expected_endpoint

def test_get_llm_instance_phi3_missing_url(mocker):
    """Verify ValueError if provider is 'phi3_onnx_local' but URL is missing."""
    mocker.patch.object(settings, 'local_llm_url', None)
    with pytest.raises(ValueError, match=r"LOCAL_LLM_URL setting required for provider 'phi3_onnx_local'"):
        _get_llm_instance(provider="phi3_onnx_local", model=None, api_key=None, api_url=None, hf_api_key=None)


# --- OpenAI Compatible Local Tests ---
def test_get_llm_instance_openai_compatible_success(mocker):
    """Verify returns ChatOpenAI instance for 'openai_compatible_local'."""
    # Arrange: Define mock values and patch settings
    mock_url = HttpUrl("http://mock-oai-compat:8000/v1")
    mock_model = "vicuna-7b"
    mock_key = "optional-key"
    mocker.patch.object(settings, 'local_llm_url', mock_url)
    mocker.patch.object(settings, 'local_llm_model', mock_model)
    mocker.patch.object(settings, 'openai_api_key', mock_key)

    # Act: Call the function with all required arguments
    llm_instance = _get_llm_instance(
        provider="openai_compatible_local",
        model=mock_model,
        api_key=mock_key,
        api_url=mock_url,
        hf_api_key=None # Pass None for unused optional args
    )

    # Assert
    assert isinstance(llm_instance, ChatOpenAI)
    assert llm_instance.model_name == mock_model
    # Removed base_url check as previously discussed
    assert llm_instance.openai_api_key.get_secret_value() == mock_key

def test_get_llm_instance_openai_compatible_success_no_key(mocker):
    """Verify returns ChatOpenAI instance for 'openai_compatible_local' even without API key."""
    # Arrange: Define mock values and patch settings
    mock_url = HttpUrl("http://mock-oai-compat:8000/v1")
    mock_model = "vicuna-7b"
    mocker.patch.object(settings, 'local_llm_url', mock_url)
    mocker.patch.object(settings, 'local_llm_model', mock_model)
    mocker.patch.object(settings, 'openai_api_key', None) # Mock key as None

    # Act: Call the function with all required arguments (api_key is None)
    llm_instance = _get_llm_instance(
        provider="openai_compatible_local",
        model=mock_model,
        api_key=None, # Pass None explicitly
        api_url=mock_url,
        hf_api_key=None # Pass None for unused optional args
    )

    # Assert
    assert isinstance(llm_instance, ChatOpenAI)
    assert llm_instance.model_name == mock_model
    # Removed base_url check as previously discussed
    # Check that the dummy key was used internally by the function
    assert llm_instance.openai_api_key.get_secret_value() == "not-needed"

def test_get_llm_instance_openai_compatible_missing_url(mocker):
    """Verify ValueError if provider is 'openai_compatible_local' but URL is missing."""
    mocker.patch.object(settings, 'local_llm_url', None)
    mocker.patch.object(settings, 'local_llm_model', 'test-model')
    with pytest.raises(ValueError, match=r"LOCAL_LLM_URL setting required.*openai_compatible_local"):
        _get_llm_instance(provider="openai_compatible_local", model='test-model', api_key=None, api_url=None, hf_api_key=None)

def test_get_llm_instance_openai_compatible_missing_model(mocker):
    """Verify ValueError if provider is 'openai_compatible_local' but model is missing."""
    mock_url = HttpUrl("http://mock-oai-compat:8000/v1")
    mocker.patch.object(settings, 'local_llm_url', mock_url)
    mocker.patch.object(settings, 'local_llm_model', None)
    with pytest.raises(ValueError, match=r"LOCAL_LLM_MODEL setting required.*openai_compatible_local"):
        _get_llm_instance(provider="openai_compatible_local", model=None, api_key=None, api_url=mock_url, hf_api_key=None)


# --- Unsupported Provider Test ---
def test_get_llm_instance_unsupported_provider(mocker):
    # ... setup ...
    unsupported_provider = "no_such_llm"
    # CORRECTED match pattern
    with pytest.raises(ValueError, match="Unsupported LLM provider configured"):
         _get_llm_instance(provider=unsupported_provider, model=None, api_key=None, api_url=None, hf_api_key=None)