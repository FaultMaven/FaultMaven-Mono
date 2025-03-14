# app/log_metrics_analysis.py
import subprocess
import json
import re  # Import the 're' module
from collections import defaultdict  # Keep existing defaultdict import
from datetime import datetime  # Keep existing datetime import
from typing import Dict, Any, List, Optional
from app.logger import logger
from config.settings import settings  # Import settings
from pydantic import BaseModel, field_validator
import statistics
import os
from app.llm_provider import LLMProvider

class LogInsights(BaseModel):  # Pydantic model for return
    level_counts: Dict[str, int] = {}
    error_messages: List[str] = []
    anomalies: List[str] = []
    metrics: Dict[str, float] = {} # Initialize to empty dict for now.
    summary: str = ""


def process_logs_data(data: str, llm_provider: LLMProvider) -> LogInsights:
    """Processes log data using Vector and performs analysis."""

    try:
        # Determine command based on environment (Docker or local)
        if os.environ.get("RUNNING_IN_DOCKER") == "true":
             command = ["vector", "--config", "app/vector.yaml"]
             timeout = settings.VECTOR_TIMEOUT
        else:
             command = ["vector", "--config", "app/vector.yaml"]
             timeout = settings.VECTOR_TIMEOUT

        # Run Vector as a subprocess, piping the data to its stdin
        process = subprocess.run(
            command,
            input=data.encode("utf-8"),
            capture_output=True,
            check=True,
            timeout=timeout,
        )

        # Vector's output (parsed logs) is on stdout
        vector_output = process.stdout.decode("utf-8")
        logger.info(f"Vector output: {vector_output}")  # Keep for debugging

        # Parse Vector's output (it's JSON, one object per line)
        parsed_logs = []
        for line in vector_output.strip().split("\n"):
            try:
                parsed_logs.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding Vector output: {e}, Line: {line}")
                # Handle JSON parsing errors (skip the line for now)
                continue

        # Analyze the parsed logs
        insights = analyze_logs(parsed_logs)
        logger.info(f"Log analysis insights: {insights}")  # Log insights
        insights["summary"] = process_data_summary(LogInsights(**insights), llm_provider)

        return LogInsights(**insights)


    except subprocess.CalledProcessError as e:
        logger.error(f"Vector process failed: {e}")
        logger.error(f"Vector stderr: {e.stderr.decode()}")  # Log stderr
        raise ValueError(f"Log processing with Vector failed: {e.stderr.decode()}") from e
    except subprocess.TimeoutExpired as e:
        logger.error(f"Vector process timed out")
        raise ValueError("Log processing with Vector timed out.") from e
    except Exception as e:
        logger.error(f"Error during log processing: {e}", exc_info=True)
        raise

def analyze_logs(parsed_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyzes the parsed log data from Vector (syslog format)."""

    level_counts: Dict[str, int] = defaultdict(int)
    error_messages: List[str] = []
    anomalies: List[str] = []
    metrics: Dict[str, List[float]] = defaultdict(list)


    for log_entry in parsed_logs:
        # Count severity levels (using the 'level' field from Vector)
        level = log_entry.get("level")  # Use the 'level' field
        if level:
            level_counts[level] = level_counts.get(level, 0) + 1

        # Extract error messages (check for level = ERROR)
        #The syslog severities are: emerg, alert, crit, err, warning, notice, info, debug
        if level == "ERROR" or level == "err" or level == "crit":  # Use standard syslog severity levels
              error_messages.append(log_entry.get("message", "")) # extract message.

    # Basic Anomaly Detection (Example)
    if level_counts.get("ERROR", 0) > 5:  # Simple threshold
        anomalies.append("High number of errors detected.")

    # Build a basic summary
    summary = (
        f"Processed {len(parsed_logs)} log entries. "
        f"Severity Counts: {dict(level_counts)}" #Convert to dict
    )

    return {
        "level_counts": dict(level_counts),
        "error_messages": error_messages,
        "anomalies": anomalies,
        "metrics": {},  # Return calculated averages
        "summary": summary,
    }

def process_data_summary(log_insights: LogInsights, llm_provider: LLMProvider) -> str:
    """Generates an LLM-powered summary of the log analysis results."""
    try:
        log_data_string = format_log_data_for_summary(log_insights)
        prompt = settings.log_summary_prompt.format(log_data=log_data_string)
        result = llm_provider.query(prompt)
        if result:
            return result
        else:
            logger.error("LLM returned an empty response for data summary.")
            return "Error: LLM returned an empty response."
    except Exception as e:
        logger.error(f"LLM data summary generation failed: {e}", exc_info=True)
        return "Error generating data summary."

def format_log_data_for_summary(log_insights: LogInsights) -> str:
    """Formats LogInsights data for LLM summary."""
    # Construct a string representation of the LogInsights data
    summary = log_insights.summary # Access fields directly

    level_counts_str = ", ".join(
        f"{level}: {count}" for level, count in log_insights.level_counts.items()
    )
    error_messages_str = ", ".join(log_insights.error_messages)
    anomalies_str = ", ".join(log_insights.anomalies)
    metrics_str = ", ".join(
        f"{metric}: {value}" for metric, value in log_insights.metrics.items()
    )

    formatted_data = (
        f"Summary: {summary}\n"
        f"Severity Level Counts: {level_counts_str}\n"
        f"Error Messages: {error_messages_str}\n"
        f"Anomalies Detected: {anomalies_str}\n"
        f"Metrics: {metrics_str}"
    )
    return formatted_data