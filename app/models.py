# app/models.py
# Central location for all Pydantic models and related Enums for the application

import time
from enum import Enum
from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, Field, field_validator, constr, ConfigDict, HttpUrl
import re

# --- Enums ---
class DataType(str, Enum):
    """Enumeration for classifying the type of uploaded data based on content."""

    # Tickets, user descriptions, messages, contextual snippets, etc.
    ISSUE_DESCRIPTION = "issue_description"

    SYSTEM_LOGS = "log"
    MONITORING_METRICS = "metric"
    CONFIGURATION_DATA = "config"
    SOURCE_CODE = "source_code"

    # Renamed from TEXT, serves as the content-based fallback:
    # Any text that doesn't fit a more specific category above.
    GENERIC_TEXT = "text"

    UNKNOWN = "unknown"

# --- Input Validation Constants ---

MAX_QUERY_LENGTH = 10000
MAX_FEEDBACK_LENGTH = 2000
# Basic regex, allows common characters in technical queries. May need refinement.
QUERY_REGEX = r"^[a-zA-Z0-9\s.,;:'\"?!-]+$"

# --- Request Models (Used in API endpoint inputs) ---

class QueryRequest(BaseModel):
    """Model for incoming user queries via the /query endpoint."""
    query: str = Field(..., max_length=MAX_QUERY_LENGTH, description="User's troubleshooting query.")

    @field_validator("query")
    def check_query(cls, v):
        """Validates the query length first, then format."""
        if not isinstance(v, str):
             raise ValueError("Query must be a string")

        # --- Check length constraint FIRST ---
        if not (1 <= len(v) <= MAX_QUERY_LENGTH):
             raise ValueError(f"Query length must be between 1 and {MAX_QUERY_LENGTH}")
        # --- END Length Check ---

        # --- Check for allowed characters using the regex SECOND ---
        if not re.match(QUERY_REGEX, v, re.IGNORECASE):
            # This check will now only run if the string has valid length (is not empty)
            raise ValueError(f"Query contains invalid characters. Only letters, numbers, spaces, and .,;:'\"?!- are allowed.")
        # --- END Character Check ---

        return v # Return the validated value

class FeedbackRequest(BaseModel):
    """Model for user feedback submission via the /feedback endpoint."""
    query: str = Field(..., max_length=MAX_FEEDBACK_LENGTH, description="The query associated with the feedback.")
    feedback: constr(strip_whitespace=True, min_length=1, max_length=MAX_FEEDBACK_LENGTH) = Field(..., description="User feedback text.")


# --- Internal Data Structures & Specialized Results ---

class BrowserContextData(BaseModel):
    """Model for structured data submitted from browser context."""
    url: Optional[str] = None
    title: Optional[str] = None
    selected_text: Optional[str] = None
    page_content_snippet: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class LogInsights(BaseModel):
    """Structured insights from processed log data."""
    level_counts: Dict[str, int] = Field(default_factory=dict)
    error_messages: List[str] = Field(default_factory=list)
    anomalies: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    summary: str = Field("")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class UploadedData(BaseModel):
    """Internal representation for storing uploaded data and processed results."""
    original_type: str = Field(description="'file', 'text', or 'browser_context'")
    content_snippet: Optional[str] = Field(None, description="A snippet of the original content.")
    classified_type: DataType
    timestamp: float = Field(default_factory=time.time)
    filename: Optional[str] = None
    # Union order updated: Dict first
    processed_results: Optional[Union[Dict[str, Any], LogInsights, str]] = Field(None, description="Structured results (Dict, LogInsights, str summary/error).")
    processing_status: str = Field("Pending", description="Status: Pending, Processing, Processed, Failed.")

class DataClassification(BaseModel):
    """Output model returned by the data classification function/service."""
    data_type: DataType
    confidence: float = Field(ge=0, le=1, description="Classifier confidence score (0.0 to 1.0).")
    key_features: List[str] = Field(description="Key features or reasons for the classification.")
    suggested_tool: str = Field(description="Suggested tool for further analysis based on type.")

class ClassificationOutput(BaseModel):
    """Internal model specifically for parsing simple LLM classification output."""
    data_type: DataType = Field(description="The most likely data type.")

# --- Response Models (Used in API endpoint outputs) ---

class TroubleshootingResponse(BaseModel):
    """Structured response for the /query endpoint."""
    answer: str = Field(description="The primary answer or analysis provided by the main chat LLM.")
    action_items: Optional[List[str]] = Field(None, description="A list of suggested next steps or actions for the user.")

class DataInsightsResponse(BaseModel):
    """Response model for the /data endpoint, returning processing insights."""
    message: str = Field(description="User-facing message indicating processing status.")
    classified_type: str = Field(description="String representation of the classified DataType.")
    session_id: str = Field(description="The session ID.")
    insights: Optional[Union[LogInsights, Dict[str, Any], str]] = Field(None, description="Structured insights or summary.")
    next_prompt: Optional[str] = Field(None, description="Suggested next action or clarifying question for the user.") # Added field
    
    @field_validator('insights', mode='before')
    @classmethod
    def coerce_insights_dict(cls, v: Any) -> Any:
        """
        If the input 'insights' is a dictionary, attempt to parse it as LogInsights first.
        """
        if isinstance(v, dict):
            try:
                # Try creating a LogInsights object. Pydantic handles validation
                # and applies default values for missing fields.
                return LogInsights(**v)
            except Exception:
                # If it fails validation as LogInsights (e.g., wrong field types,
                # extra fields if config forbids it, etc.), or if it's just meant
                # to be a generic dict, return the original dict.
                # This allows the Union[..., Dict[str, Any], ...] to still match.
                return v
        # If it's not a dict (e.g., already LogInsights, str, None), pass it through.
        return v