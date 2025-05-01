# app/data_classifier.py
"""
This module classifies incoming data strings into predefined categories
(defined by the DataType enum). It uses a hybrid approach:
1. Fast heuristic functions (regex, keyword matching) for common, structured types.
2. A fallback call to a configured classifier LLM for ambiguous cases.
"""

import re
import json
from typing import Optional, List, Dict, Any
from app.logger import logger
import time # Good practice, might be used for timing heuristics later

# --- LLM and LangChain Imports ---
# Import the specific LLM instance designated for classification tasks
from app.llm_provider import classifier_llm
# Import necessary LangChain components for building the classification chain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser

# --- Centralized Models and Enums ---
# Import required data structures from the central models file
# Assumes app/models.py defines DataType and DataClassification correctly
from app.models import DataType, DataClassification

# --- Heuristic Classification Functions ---
# These functions provide fast, rule-based checks for common data formats.

def is_likely_json(data: str) -> bool:
    """Checks if the input string is likely valid JSON."""
    data = data.strip()
    if not data: # Empty string is not valid JSON
        return False
    # Rely on json.loads for robust check, allows primitives
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def is_likely_syslog(data: str) -> bool:
    """
    Checks for patterns resembling common syslog formats (RFC 5424 or RFC 3164)
    at the beginning of the string. Handles optional version digit and spaces.
    """
    # Regex matches: optional_space<PRI> (optional_digit + space(s) OR zero_or_more_spaces) + something_else
    pattern = r"^\s*<\d{1,5}>(?:\d\s+|\s*)(\S+)" # Allows PRI up to 5 digits, handles RFC5424/3164 space variations
    return bool(re.match(pattern, data))

def is_likely_csv(data: str) -> bool:
    """
    Checks if the input appears to be Comma Separated Values.
    Requires at least two lines and a comma in the first line.
    """
    lines = data.splitlines()
    # Need at least a header and one data row for this simple check
    if len(lines) < 2 or not lines[0].strip():
        return False
    # Check if the header contains a comma (indicating multiple columns)
    return ',' in lines[0]

def is_likely_xml(data: str) -> bool:
    """Checks if the input starts with common XML patterns."""
    data = data.lstrip()
    # Check for XML declaration or a basic opening tag structure potentially ending with >
    # Note: This is a basic heuristic, not full XML validation.
    return data.startswith("<?xml") or (data.startswith("<") and data.endswith(">"))

def contains_metric_keywords(data: str) -> bool:
    """Checks for the presence of common monitoring metric keywords."""
    # This list can be expanded based on common metric names in your environment
    keywords = {"cpu", "memory", "disk", "network", "latency", "throughput", "request", "requests", "errors", "utilization", "bytes", "packets", "iops", "query_count", "duration_ms", "queue_depth"}
    data_lower = data.lower()
    # Simple substring check for broad matching
    return any(keyword in data_lower for keyword in keywords)

def contains_log_keywords(data: str) -> bool:
    """Checks for the presence of common logging keywords."""
    # Includes levels, common message components, etc.
    keywords = {"log", "error", "err", "warn", "warning", "info", "debug", "exception", "trace", "fail", "failed", "critical", "fatal", "severe", "severity", "timestamp", "message", "userid", "requestid"}
    data_lower = data.lower()
    return any(keyword in data_lower for keyword in keywords)

def is_root_cause_analysis_ticket(data: str) -> bool:
    """Checks for keywords common in incident reports, tickets, or RCA documents."""
    keywords = {"incident", "problem", "customer support", "root cause", "ticket", "issue", "outage", "failure", "rca", "case", "sev", "severity", "impact", "resolution", "postmortem"}
    data_lower = data.lower()
    # Consider requiring multiple keywords for higher confidence if needed
    return any(keyword in data_lower for keyword in keywords)

def is_likely_source_code(data: str) -> bool:
    """Checks for common source code keywords and structures."""
    # Basic keywords across languages
    keywords = {
        "def ", "class ", "import ", "function ", "public ", "private ",
        "static ", "void ", "module ", "require(", "include ", "using ",
        "const ", "let ", "var ", "=>", "->", "#include", "//", "/*"
    }
    # Common symbols often appearing at line start/end or frequently
    symbols = {"{", "}", ";", "(", ")", ":"}
    # Heavier weighting if multiple distinct keywords are found? (Optional improvement)

    data_lower = data.lower() # For case-insensitive keyword checks if needed, though some are case-sensitive
    line_count = data.count('\n')

    # Check 1: Presence of multiple keywords
    found_keywords = sum(1 for kw in keywords if kw in data) # Use original data for case-sensitive checks like 'def '
    if found_keywords >= 2: # Require at least two distinct keywords
         return True

    # Check 2: Presence of common symbols (might be less reliable alone)
    # found_symbols = sum(1 for sym in symbols if sym in data)
    # if found_symbols >= 3 and line_count > 1: # Require symbols and multiple lines
    #     return True

    # Check 3: Specific patterns (e.g., Python function/class defs, Java class defs)
    # Add more language-specific regex if needed, but keep it fast
    if re.search(r"^\s*(?:def|class)\s+\w+\(?", data, re.MULTILINE): # Python-like
        return True
    if re.search(r"^\s*(?:public|private|protected)\s+(?:class|interface|enum)\s+\w+", data, re.MULTILINE): # Java/C#-like
        return True

    # Add more checks as needed...

    return False


# --- LLM Classification Setup ---

# Define the prompt template for the LLM classifier.
# Instructs the LLM on the task and desired output format.
classification_prompt_template = PromptTemplate.from_template(
    """Classify the following data snippet into ONE of these categories: {categories}.
Return ONLY the category name as a single word (e.g., 'issue_description', 'log', 'metric', 'config', 'source_code', 'text').
Do NOT return anything else. The available categories are strictly limited to the list provided.

Data Snippet:
{data_snippet}


Category:"""
)

# Define the simple LangChain chain for classification.
# It pipes the prompt to the classifier LLM and parses the string output.
classification_chain = (
    classification_prompt_template
    | classifier_llm # Uses the LLM instance imported from app.llm_provider
    | StrOutputParser() # Parses the LLM output directly into a string
)

# --- Async LLM-Based Classification Function (Fallback) ---

async def classify_with_llm(data: str) -> DataClassification:
    """
    Classifies data using the LLM chain when heuristic methods are inconclusive.

    Args:
        data: The data string to classify.

    Returns:
        A DataClassification object with the LLM's inferred type and lower confidence.
    """
    # Prepare categories for the prompt, excluding UNKNOWN as a choice for the LLM
    categories = ", ".join([e.value for e in DataType if e != DataType.UNKNOWN])
    # Limit the data snippet sent to the LLM
    input_data = {"categories": categories, "data_snippet": data[:1500]} # Limit to ~1500 chars

    try:
        # Invoke the LangChain classification chain asynchronously
        response = await classification_chain.ainvoke(input_data)
        llm_result = response.strip().lower()
        logger.info(f"LLM classification chain raw response: '{llm_result}'")

        # --- Add/Enhance Synonym Mapping ---
        # Map common LLM variations to our official enum values
        synonym_map = {
            "logs": "log",
            "metrics": "metric",
            "configuration": "config",
            "code": "source_code",
            "script": "source_code",
            "problem": "issue_description",
            "issue": "issue_description",
            "ticket": "issue_description",
            # Add more potential synonyms as observed from LLM behavior
        }
        llm_result_mapped = synonym_map.get(llm_result, llm_result) # Use mapped value if found, otherwise original
        # --- End Synonym Mapping ---

        try:
            # Use the potentially mapped result for enum conversion
            data_type = DataType(llm_result_mapped)
            logger.info(f"LLM classification mapped '{llm_result}' to '{llm_result_mapped}' -> {data_type}")
        except ValueError:
            # If the mapped result still doesn't match any enum value
            logger.warning(f"LLM classification returned unrecognized type: '{llm_result}' (mapped: '{llm_result_mapped}'). Defaulting to UNKNOWN.")
            data_type = DataType.UNKNOWN

        # Assign lower confidence as this is an LLM fallback
        confidence = 0.7 if data_type != DataType.UNKNOWN else 0.3
        key_features = ["LLM classification fallback"]

        # Map determined data type to suggested tools (can be refined)
        tool_map = {
            DataType.ISSUE_DESCRIPTION: "Ticketing/RCA systems (e.g., Jira, ServiceNow)",
            DataType.SYSTEM_LOGS: "Log analysis tools (e.g., ELK, Splunk, Grafana Loki, Vector)",
            DataType.MONITORING_METRICS: "Metric analysis tools (e.g., Prometheus, Grafana, Datadog)",
            DataType.CONFIGURATION_DATA: "Config management/diff tools (e.g., Ansible, Terraform, git diff)",
            DataType.SOURCE_CODE: "Code analysis tools (e.g., IDE, Linter, Static Analysis, Debugger)", # <-- Added
            DataType.TEXT: "General text analysis tools",
            DataType.UNKNOWN: "N/A"
        }
        suggested_tool = tool_map.get(data_type, "N/A") # Existing logic works

        # Construct and return the result object
        return DataClassification(
            data_type=data_type,
            confidence=confidence,
            key_features=key_features,
            suggested_tool=suggested_tool
        )

    except Exception as e:
        # Catch potential errors during the LLM chain invocation (e.g., API errors)
        logger.error(f"LLM classification chain invocation failed: {e}", exc_info=True)
        # Return UNKNOWN with very low confidence on failure
        return DataClassification(
            data_type=DataType.UNKNOWN,
            confidence=0.1,
            key_features=["LLM classification failure"],
            suggested_tool="N/A"
        )

# --- Async Main Classification Function ---

async def classify_data(data: str) -> DataClassification:
    """
    Classifies input data using a combination of heuristics (for speed and
    accuracy on known formats) and an LLM fallback (for ambiguity).

    Args:
        data: The input data string (e.g., from file upload or text input).

    Returns:
        A DataClassification object containing the determined type, confidence score,
        key features identified, and a suggested tool for analysis.
    """
    # 1. Handle empty input
    data = data.strip()
    if not data:
        logger.warning("classify_data called with empty or whitespace-only input.")
        return DataClassification(data_type=DataType.UNKNOWN, confidence=1.0, key_features=["Empty input"], suggested_tool="N/A")

    # 2. Apply Heuristic Checks (ordered by likely specificity/reliability)
    # Check for source code before general text keywords but after structured data/problem statement
    if is_likely_source_code(data):
        logger.debug("Data classified as SOURCE_CODE by heuristic (code keywords/patterns).")
        return DataClassification(data_type=DataType.SOURCE_CODE, confidence=0.80, # Confidence level adjustable
                                  key_features=["Source code keywords/patterns detected"], suggested_tool="Code analysis tools")

    # Check for document-type keywords (Problem Statement)
    if is_root_cause_analysis_ticket(data):
        logger.debug("Data classified as PROBLEM_STATEMENT by heuristic (RCA keywords).")
        return DataClassification(data_type=DataType.PROBLEM_STATEMENT, confidence=0.75,
                                  key_features=["RCA/Ticket keywords found"], suggested_tool="ServiceNow / Jira / Wiki")

    # Check for specific formats first
    if is_likely_syslog(data):
        logger.debug("Data classified as SYSTEM_LOGS by heuristic (syslog format).")
        # Confidence high for format match
        return DataClassification(data_type=DataType.SYSTEM_LOGS, confidence=0.95,
                                  key_features=["Syslog format detected"], suggested_tool="Vector / Fluent Bit / Log Parsers")
    if is_likely_json(data):
        logger.debug("Data classified as CONFIGURATION_DATA or structured log by heuristic (JSON structure).")
        # JSON is often config, but could be structured logs. Defaulting to config.
        # Further checks (e.g., keywords inside JSON) could refine this.
        return DataClassification(data_type=DataType.CONFIGURATION_DATA, confidence=0.9,
                                  key_features=["JSON structure detected"], suggested_tool="Config mgmt / JSON tools / Log Parsers")
    if is_likely_xml(data):
        logger.debug("Data classified as CONFIGURATION_DATA by heuristic (XML structure).")
        return DataClassification(data_type=DataType.CONFIGURATION_DATA, confidence=0.85, # Slightly lower than JSON maybe
                                  key_features=["XML structure detected"], suggested_tool="XML / Config tools")

    # Check for document-type keywords
    if is_root_cause_analysis_ticket(data):
        logger.debug("Data classified as ISSUE_DESCRIPTION by heuristic (RCA keywords).")
        return DataClassification(data_type=DataType.ISSUE_DESCRIPTION, confidence=0.75,
                                  key_features=["RCA/Ticket keywords found"], suggested_tool="ServiceNow / Jira / Wiki")

    # Check for general content keywords (less reliable)
    # Check logs before metrics, as logs might contain metric keywords
    if contains_log_keywords(data):
        logger.debug("Data classified as SYSTEM_LOGS by heuristic (log keywords).")
        return DataClassification(data_type=DataType.SYSTEM_LOGS, confidence=0.8,
                                  key_features=["Log keywords found"], suggested_tool="Log analysis tools")
    if contains_metric_keywords(data):
        logger.debug("Data classified as MONITORING_METRICS by heuristic (metric keywords).")
        return DataClassification(data_type=DataType.MONITORING_METRICS, confidence=0.7,
                                  key_features=["Metric keywords found"], suggested_tool="Prometheus / Datadog / Metric tools")

    # Check for generic tabular format (ambiguous)
    if is_likely_csv(data):
        logger.debug("Data classified as MONITORING_METRICS by heuristic (CSV format).")
        # Defaulting to metrics, but could be other tabular data.
        return DataClassification(data_type=DataType.MONITORING_METRICS, confidence=0.6,
                                  key_features=["CSV format detected"], suggested_tool="Spreadsheets / Metric tools")
    

    # 3. Fallback to LLM Classification if no heuristic matched confidently
    logger.debug("No high-confidence heuristic match found. Falling back to LLM classification.")
    return await classify_with_llm(data)