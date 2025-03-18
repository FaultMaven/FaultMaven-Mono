# config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any

class Settings(BaseSettings):
    # LLM Provider Selection - Default to Hugging Face for now
    llm_provider: str = Field("huggingface", env="LLM_PROVIDER")

    # OpenAI API Configuration (Optional, if you use OpenAI)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: Optional[str] = Field("gpt-4o", env="OPENAI_MODEL")

    # Hugging Face API Configuration
    huggingface_api_key: Optional[str] = Field(None, env="HUGGINGFACE_API_KEY")
    huggingface_model: str = Field("mistralai/Mixtral-8x7B-Instruct-v0.1", env="HUGGINGFACE_MODEL") # Using a better model.
    huggingface_api_url: str = Field("https://api-inference.huggingface.co/models", env="HUGGINGFACE_API_URL")

    # Anthropic (Claude) API Configuration  (Optional)
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    anthropic_model: Optional[str] = Field("claude-3-opus", env="ANTHROPIC_MODEL")
    anthropic_api_url: Optional[str] = Field(None, env="ANTHROPIC_API_URL")

    # Mistral AI Configuration (Optional)
    mistral_api_key: Optional[str] = Field(None, env="MISTRAL_API_KEY")
    mistral_model: str = Field("mistral-large", env="MISTRAL_MODEL")
    mistral_api_url: Optional[str] = Field(None, env="MISTRAL_API_URL")

    # DeepSeek AI Configuration (Optional)
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    deepseek_model: str = Field("deepseek-chat", env="DEEPSEEK_MODEL")
    deepseek_api_url: Optional[str] = Field(None, env="DEEPSEEK_API_URL")

    # OpenRouter API Configuration (Optional - Supports various models)
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field("openrouter-default", env="OPENROUTER_MODEL")
    openrouter_api_url: Optional[str] = Field(None, env="OPENROUTER_API_URL")

    # IBM Granite AI Configuration (Optional)
    ibm_granite_api_key: Optional[str] = Field(None, env="IBM_GRANITE_API_KEY")
    ibm_granite_model: str = Field("granite-13b-instruct", env="IBM_GRANITE_MODEL")
    ibm_granite_api_url: Optional[str] = Field(None, env="IBM_GRANITE_API_URL")

    # Log summary prompt (Corrected)
    log_summary_prompt: str = (
        "Summarize the following log data concisely, focusing on key observations, trends, anomalies, and potential issues. "
        "Limit the summary to 150 words.\n\n"
        "**Log Data:**\n{log_data}\n\n"
        "**Key Insights:**"  # Clear output marker
    )

    # General query prompt (Corrected)
    general_query_prompt: str = (
        "You are FaultMaven, a highly skilled SRE and DevOps expert. "
        "Provide a concise and informative answer to the following question. "
        "Assume the user is a technical professional. "
        "Use bullet points or numbered lists if applicable. Keep responses under 200 words.\n\n"
        "**Conversation History:**\n"
        "{context}\n\n"
        "**User:** {query}\n\n" # User:
        "**Assistant:**"  # Assistant:
    )
    # Troubleshooting prompt (Corrected)
    troubleshooting_prompt: str = (
        "You are FaultMaven, an expert troubleshooting assistant specializing in Site Reliability Engineering (SRE) and DevOps. "
        "Analyze the provided system data and user question to determine the MOST LIKELY root cause. "
        "Provide concise, actionable next steps ONLY when supported by the data and directly relevant to the user's question. "
        "Your response MUST be valid JSON. Invalid JSON is not acceptable.\n\n"
        "**Conversation History:**\n"
        "{context}\n\n"
        "**User:** {user_query}\n\n"
        "**System Data Summary:**\n{data_summary}\n\n"
    )


    # Data classification prompt
    data_classification_prompt: str = (
        "Classify the following data into ONE of these categories: log, metric, config, text, or unknown.\n"
        "Return ONLY the category name. Do NOT return anything else.\n\n"
        "Data:\n`\n{data}\n`\n\n"
        "Category:"
    )
    # Prompt for text analysis
    text_analysis_prompt: str = (
        "Summarize and analyze the following text. Identify any key topics, entities, or potential issues. "
        "If the text appears to be related to a technical problem, suggest possible causes or troubleshooting steps.\n\n"
        f"Text:\n`\n{{data}}\n`"
    )

    error_rate_anomaly_threshold_factor: float = 2.0
    min_data_points_for_anomaly_detection: int = 3
    metric_anomaly_threshold_std_dev: float = 2.0
    SESSION_TIMEOUT: int = 1800
    VECTOR_TIMEOUT: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

settings = Settings()