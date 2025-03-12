# config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any

class Settings(BaseSettings):
    # LLM Provider Selection
    llm_provider: str = Field("openai", env="LLM_PROVIDER")  # Default to OpenAI

    # OpenAI API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")  # Required
    openai_model: str = Field("gpt-4o", env="OPENAI_MODEL")

    # Hugging Face API Configuration
    huggingface_api_key: Optional[str] = Field(None, env="HUGGINGFACE_API_KEY")
    huggingface_model: str = Field("tiiuae/falcon-7b-instruct", env="HUGGINGFACE_MODEL")
    huggingface_api_url: str = Field("https://api-inference.huggingface.co/models", env="HUGGINGFACE_API_URL")

    # Anthropic (Claude) API Configuration
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-3-opus", env="ANTHROPIC_MODEL")
    anthropic_api_url: Optional[str] = Field(None, env="ANTHROPIC_API_URL")  # Add API URL if needed

    # Mistral AI Configuration
    mistral_api_key: Optional[str] = Field(None, env="MISTRAL_API_KEY")
    mistral_model: str = Field("mistral-large", env="MISTRAL_MODEL")
    mistral_api_url: Optional[str] = Field(None, env="MISTRAL_API_URL")  # Add API URL if needed

    # DeepSeek AI Configuration
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    deepseek_model: str = Field("deepseek-chat", env="DEEPSEEK_MODEL")
    deepseek_api_url: Optional[str] = Field(None, env="DEEPSEEK_API_URL")  # Add API URL

    # OpenRouter API Configuration (Supports various models)
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field("openrouter-default", env="OPENROUTER_MODEL") # Change if using a specific model
    openrouter_api_url: Optional[str] = Field(None, env="OPENROUTER_API_URL")  # Add API URL

    # IBM Granite AI Configuration
    ibm_granite_api_key: Optional[str] = Field(None, env="IBM_GRANITE_API_KEY")
    ibm_granite_model: str = Field("granite-13b-instruct", env="IBM_GRANITE_MODEL")
    ibm_granite_api_url: Optional[str] = Field(None, env="IBM_GRANITE_API_URL") # Add API URL


    # Log summary prompt
    log_summary_prompt: str = (
        "Summarize the following log analysis findings in a single, concise paragraph. "
        "Highlight key observations and any detected anomalies.\n\n"
        "**Log Data:**\n{log_data}"
    )

    general_query_prompt: str = (
        "You are FaultMaven, a highly skilled SRE and DevOps expert. "
        "Provide a concise and informative answer to the following general question related to Site Reliability Engineering, DevOps, "
        "system administration, cloud computing, or related technical fields. "
        "Assume the user is a technical professional with foundational knowledge. "
        "Focus on providing a clear explanation, best practices, and examples where appropriate. "
        "Use bullet points or numbered lists for clarity if applicable. Keep responses under 200 words.\n\n"
        "**Question:** {query}\n\n"
        "**Answer:**"
    )

    troubleshooting_prompt: str = (
        "You are FaultMaven, an expert troubleshooting assistant. Analyze the provided system data and user question to determine the MOST LIKELY root cause. "
        "Provide concise, actionable next steps ONLY IF they are directly supported by the data and relevant to the question. "
        "Your response MUST be valid JSON. Invalid JSON is an error.\n\n"
        "**Conversation History:**\n"
        "{context}\n\n"
        "**User's Question:** {user_query}\n\n"
        "**System Data:**\n"
        "{data_summary}\n"  # Use a single, combined data summary
        "Provide a JSON-formatted response:\n"
        "```json\n"
        "{{\n"
        "  \"answer\": \"<Concise answer to the user's question, addressing the likely root cause>\",\n"
        "  \"action_items\": [\"<Action Item 1>\", \"<Action Item 2>\"]\n"  # Optional
        "}}\n"
        "```\n"
        "**JSON Response:**" # Add this to be more clear.
    )

    error_rate_anomaly_threshold_factor: float = 2.0
    min_data_points_for_anomaly_detection: int = 3
    metric_anomaly_threshold_std_dev: float = 2.0
    SESSION_TIMEOUT: int = 1800

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

settings = Settings()