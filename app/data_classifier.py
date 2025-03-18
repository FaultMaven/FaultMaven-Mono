# app/data_classifier.py
import re
import json
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from app.logger import logger
from app.llm_provider import LLMProvider
from config.settings import settings  # Import settings


# --- Data Types ---
class DataType(str, Enum):
    SYSTEM_LOGS = "log"
    MONITORING_METRICS = "metric"
    CONFIGURATION_DATA = "config"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"  # New category for tickets
    TEXT = "text"  # Generic text
    UNKNOWN = "unknown"

# --- Pydantic Model ---
class DataClassification(BaseModel):
    data_type: DataType = Field(description="The type of data.")
    confidence: float = Field(ge=0, le=1, description="Confidence score (0.0 to 1.0).")
    key_features: List[str] = Field(description="Key features that led to the classification.")
    suggested_tool: str = Field(description="Suggested tool for analysis.")

# --- Heuristic Classification Functions ---

def is_likely_json(data: str) -> bool:
    """Checks if the input is likely JSON."""
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def is_likely_syslog(data: str) -> bool:
    """Checks for basic syslog structure (RFC 5424 or RFC 3164)."""
    # More permissive regex.  We just check for *something* that looks like syslog.
    return bool(re.match(r"^\s*<\d+>\d*\s+\S+", data))

def is_likely_csv(data: str) -> bool:
    """Checks if the input is likely CSV (very basic heuristic)."""
    lines = data.splitlines()
    if len(lines) < 2:  # Need at least a header and one data row
        return False
    if not lines[0].strip():
        return False # Empty first line
    parts = lines[0].split(",")
    return len(parts) > 1 # First line should be splittable.


def is_likely_xml(data: str) -> bool:
    """Checks if the input starts with an XML declaration or tag."""
    data = data.lstrip()
    return data.startswith("<?xml") or data.startswith("<")

def contains_metric_keywords(data: str) -> bool:
    """Checks for metric-related keywords."""
    keywords = ["cpu", "memory", "disk", "network", "latency", "throughput", "requests", "errors", "utilization", "bytes", "packets", "iops"]
    data_lower = data.lower()
    return any(keyword in data_lower for keyword in keywords)

def contains_log_keywords(data: str) -> bool:
    """Checks for log-related keywords."""
    keywords = ["log", "error", "warning", "info", "debug", "exception", "trace", "fail", "failed", "critical"]
    data_lower = data.lower()
    return any(keyword in data_lower for keyword in keywords)

def is_root_cause_analysis_ticket(data: str) -> bool:
    """Checks for keywords indicating an incident report/ticket."""
    keywords = ["incident", "problem", "customer support", "root cause", "ticket", "issue", "outage", "failure", "RCA", "case"]
    data_lower = data.lower()
    return any(keyword in data_lower for keyword in keywords)

# --- LLM-Based Classification (Fallback) ---

def classify_with_llm(data: str, llm_provider: LLMProvider) -> DataClassification:
    """Classifies the input data using an LLM (fallback)."""
    prompt = settings.data_classification_prompt.format(data=data[:1000])  # Limit data, USE PROMPT
    try:
        response = llm_provider.query(prompt).strip().lower()
        logger.info(f"LLM raw classification response: {response}")

        # Directly use Enum for type safety and validation
        try:
            data_type = DataType(response)  # Convert string to enum.  This is more robust.
        except ValueError:  # Use ValueError, not KeyError
            logger.warning(f"Invalid data type received from LLM: {response}. Defaulting to UNKNOWN.")
            data_type = DataType.UNKNOWN

        # Provide more specific feedback based on classification (optional)
        if data_type == DataType.SYSTEM_LOGS:
             return DataClassification(data_type=data_type, confidence=0.8, key_features=["LLM classification"], suggested_tool="Fluent Bit/Vector")
        elif data_type == DataType.MONITORING_METRICS:
            return DataClassification(data_type=data_type, confidence=0.8, key_features=["LLM classification"], suggested_tool="Prometheus/Grafana")
        elif data_type == DataType.CONFIGURATION_DATA:
             return DataClassification(data_type=data_type, confidence=0.8, key_features=["LLM classification"], suggested_tool="Configuration management tools")
        elif data_type == DataType.TEXT:  # More general category
            return DataClassification(data_type=data_type, confidence=0.7, key_features=["LLM classification"], suggested_tool="General text analysis")
        else: #unknown
            return DataClassification(data_type=data_type, confidence=0.3, key_features=["LLM classification"], suggested_tool="N/A")

    except Exception as e:
        logger.error(f"LLM classification failed: {e}", exc_info=True)
        return DataClassification(data_type=DataType.UNKNOWN, confidence=0.1, key_features=["LLM failure"], suggested_tool="N/A")  # Consistent return type


# --- Main Classification Function ---

def classify_data(data: str, llm_provider: LLMProvider) -> DataClassification:
    """Classifies the input data into predefined categories."""
    data = data.strip()
    if not data:
        return DataClassification(data_type=DataType.UNKNOWN, confidence=0.0, key_features=["empty input"], suggested_tool="N/A")

    # Prioritize specific format checks
    if is_likely_syslog(data):
        return DataClassification(data_type=DataType.SYSTEM_LOGS, confidence=0.95,
                                  key_features=["Syslog format"], suggested_tool="Fluent Bit/Vector")
    if is_likely_json(data):
        return DataClassification(data_type=DataType.CONFIGURATION_DATA, confidence=0.9,
                                  key_features=["JSON structure"], suggested_tool="Configuration tools")
    if is_likely_xml(data):
         return DataClassification(data_type=DataType.CONFIGURATION_DATA, confidence=0.8,
                                  key_features=["XML structure"], suggested_tool="Configuration tools")

    # Then check for more general indicators
    if is_root_cause_analysis_ticket(data):
        return DataClassification(data_type=DataType.ROOT_CAUSE_ANALYSIS, confidence=0.7,
                                  key_features=["Ticket keywords"], suggested_tool="ServiceNow, Jira")

    # Add log keywords check *before* metric keywords
    if contains_log_keywords(data):
        return DataClassification(data_type=DataType.SYSTEM_LOGS, confidence=0.8,
                                   key_features=["Log keywords"], suggested_tool="Log analysis tools")

    if contains_metric_keywords(data):
        return DataClassification(data_type=DataType.MONITORING_METRICS, confidence=0.7,
                                  key_features=["Metric keywords"], suggested_tool="Prometheus, Grafana")

    if is_likely_csv(data):
        return DataClassification(
            data_type=DataType.MONITORING_METRICS, confidence=0.6, key_features=["CSV format"], suggested_tool="Metric tools")


    # Fallback to LLM-based classification (slower, more flexible)
    return classify_with_llm(data, llm_provider) # Fallback to LLM