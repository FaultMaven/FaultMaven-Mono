# config/settings.py
from pydantic import Field, HttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Holds all application configuration settings, loaded from environment
    variables and/or a .env file.
    """

    # --- LLM Provider Selection ---
    chat_provider: str = Field("phi3_onnx_local", validation_alias="CHAT_PROVIDER", description="Provider for main chat LLM ('openai', 'ollama', 'phi3_onnx_local', 'huggingface', etc.)")
    classifier_provider: str = Field("huggingface", validation_alias="CLASSIFIER_PROVIDER", description="Provider for classification LLM ('openai', 'huggingface', etc.)")

    # --- Provider Specific Settings ---

    # OpenAI
    openai_api_key: Optional[str] = Field(None, validation_alias="OPENAI_API_KEY", description="API Key for OpenAI services.")
    openai_model: str = Field("gpt-4o", validation_alias="OPENAI_MODEL", description="Default OpenAI model for chat/tasks.")
    classifier_model: Optional[str] = Field(None, validation_alias="CLASSIFIER_MODEL", description="Specific OpenAI model for classification (if provider is openai).")

    # Hugging Face
    huggingface_api_key: Optional[str] = Field(None, validation_alias="HUGGINGFACE_API_KEY", description="API Token for Hugging Face Hub/Endpoints.")
    huggingface_model: Optional[str] = Field("tiiuae/falcon-7b-instruct", validation_alias="HUGGINGFACE_MODEL", description="Default Hugging Face model/repo_id.")

    # Local LLM
    local_llm_url: Optional[HttpUrl] = Field(None, validation_alias="LOCAL_LLM_URL", description="Base URL for local LLM server (Ollama, OpenAI-compatible, Phi3 custom server).")
    local_llm_model: Optional[str] = Field(None, validation_alias="LOCAL_LLM_MODEL", description="Model name required by some local providers (e.g., Ollama).")

    # --- External Service Keys/URLs ---
    mcp_server_url: Optional[HttpUrl] = Field(None, validation_alias="MCP_SERVER_URL", description="URL of the external MCP processing server.")
    # --- ADD TAVILY API KEY ---
    tavily_api_key: Optional[str] = Field(None, validation_alias="TAVILY_API_KEY", description="API Key for Tavily Search service (for WebSearchTool).")
    # --- END ADDITION ---

    # --- Application Behavior Settings ---
    error_rate_anomaly_threshold_factor: float = Field(2.0, description="Factor for error rate anomaly detection.")
    min_data_points_for_anomaly_detection: int = Field(3, description="Min data points needed for std dev based anomaly detection.")
    metric_anomaly_threshold_std_dev: float = Field(2.0, description="Number of standard deviations for metric anomaly threshold.")
    SESSION_TIMEOUT: int = Field(1800, validation_alias="SESSION_TIMEOUT", description="Session inactivity timeout in seconds.")
    VECTOR_TIMEOUT: int = Field(60, validation_alias="VECTOR_TIMEOUT", description="Timeout in seconds for the external 'vector' tool subprocess.")

    # --- NEW: Agent Settings ---
    AGENT_VERBOSE: bool = Field(False, validation_alias="AGENT_VERBOSE", description="Enable verbose logging for the agent executor.")
    AGENT_MAX_ITERATIONS: int = Field(10, validation_alias="AGENT_MAX_ITERATIONS", description="Maximum iterations for the agent loop.")
    # --- END NEW SETTINGS ---


    # --- Settings Model Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Validators ---
    # (Existing validators remain unchanged)
    @field_validator('openai_api_key', mode='before')
    @classmethod
    def check_openai_key(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        values = info.data
        # Check if either provider uses openai
        if values.get('chat_provider') == 'openai' or values.get('classifier_provider') == 'openai':
             if not v:
                  raise ValueError("OPENAI_API_KEY environment variable must be set when using 'openai' provider.")
        return v

    @field_validator('huggingface_api_key', mode='before')
    @classmethod
    def check_hf_key(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        values = info.data
        # Check if either provider uses huggingface
        if values.get('chat_provider') == 'huggingface' or values.get('classifier_provider') == 'huggingface':
             if not v:
                  raise ValueError("HUGGINGFACE_API_KEY environment variable must be set when using 'huggingface' provider.")
        return v

    @field_validator('huggingface_model', mode='before')
    @classmethod
    def check_hf_model(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        values = info.data
         # Check if either provider uses huggingface
        if values.get('chat_provider') == 'huggingface' or values.get('classifier_provider') == 'huggingface':
             if not v:
                  raise ValueError("HUGGINGFACE_MODEL environment variable must be set when using 'huggingface' provider.")
        return v

    @field_validator('local_llm_url', mode='before')
    @classmethod
    def check_local_url(cls, v: Optional[HttpUrl], info: ValidationInfo) -> Optional[HttpUrl]:
        values = info.data
        local_providers = ['ollama', 'openai_compatible_local', 'phi3_onnx_local']
        # Check if either provider is one of the local types
        is_local_chat = values.get('chat_provider') in local_providers
        is_local_classifier = values.get('classifier_provider') in local_providers
        if (is_local_chat or is_local_classifier) and not v:
            raise ValueError("LOCAL_LLM_URL environment variable must be set when using a local provider.")
        return v

    @field_validator('local_llm_model', mode='before')
    @classmethod
    def check_local_model(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        values = info.data
         # Check if either provider uses ollama
        if values.get('chat_provider') == 'ollama' or values.get('classifier_provider') == 'ollama':
            if not v:
                raise ValueError("LOCAL_LLM_MODEL environment variable must be set when using 'ollama' provider.")
        return v

    @field_validator('mcp_server_url', mode='before')
    @classmethod
    def check_mcp_url(cls, v: Optional[HttpUrl], info: ValidationInfo) -> Optional[HttpUrl]:
        # No specific validation needed currently
        return v

    # No validator added for tavily_api_key as the tool handles its absence gracefully (placeholder mode)

# --- Instantiate settings once for application-wide use ---
settings = Settings()

# --- Optional: Log loaded settings on startup (example) ---
# from app.logger import logger # Make sure logger is available if you do this
# logger.info(f"Loaded settings: Chat Provider={settings.chat_provider}, Classifier Provider={settings.classifier_provider}")
# logger.info(f"Agent Settings: Verbose={settings.AGENT_VERBOSE}, Max Iterations={settings.AGENT_MAX_ITERATIONS}")
# if settings.tavily_api_key:
#     logger.info("Tavily API Key: Loaded")
# else:
#      logger.warning("Tavily API Key: Not Found (WebSearchTool may be limited)")