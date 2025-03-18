# app/log_metrics_analysis.py
import subprocess
import json
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from app.logger import logger
from config.settings import settings
from pydantic import BaseModel, ConfigDict
import statistics
import os
from app.llm_provider import LLMProvider

class LogInsights(BaseModel):  # Pydantic model for return
    level_counts: Dict[str, int] = {}
    error_messages: List[str] = []
    anomalies: List[str] = []
    metrics: Dict[str, float] = {}
    summary: str = ""
    model_config = ConfigDict(arbitrary_types_allowed=True)

def process_data(data: str, data_type: str, llm_provider: LLMProvider) -> Union[LogInsights, Dict]:
    """
    Processes the incoming data based on its type.  This is the main entry point
    for data processing.
    """
    if data_type == "log":
        return process_logs_data(data, llm_provider)
    elif data_type == "metric":
        return process_metrics_data(data)  # Placeholder
    elif data_type == "config":
        return process_config_data(data)  # Placeholder
    elif data_type == "root_cause_analysis":
        return process_problem_report_data(data)  # NEW Placeholder
    elif data_type == "text":
        return process_text_data(data, llm_provider)  # Direct LLM processing, now uses settings
    else:
        logger.warning(f"Unknown data type: {data_type}")
        return {"error": f"Unsupported data type: {data_type}"}

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
        logger.info(f"Vector output: {vector_output}")

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
        insights_dict = analyze_logs(parsed_logs)
        logger.info(f"Log analysis insights: {insights_dict}")

        # Generate LLM summary *after* analysis
        insights = LogInsights(**insights_dict)  # Create LogInsights object
        insights.summary = process_data_summary(insights, llm_provider)

        return insights  # Return the LogInsights object

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
        level = log_entry.get("level")
        if level:
            level_counts[level] = level_counts.get(level, 0) + 1

        # Extract error messages (check for level = err/ERROR)
        if level and (level.lower() == "error" or level.lower() == "err"):
              error_messages.append(log_entry.get("message", ""))

        # Metric extraction (example)
        response_time = log_entry.get("response_time")
        if response_time is not None:
            try:
                metrics["response_time"].append(float(response_time))
            except ValueError:
                logger.warning(f"Invalid response_time value: {response_time}")

    # Basic Anomaly Detection (Example - High response time)
    if metrics["response_time"]:  # Only if we have response time data
        mean_response_time = statistics.mean(metrics["response_time"])
        # Check if standard deviation can be calculated.
        try:
            stdev_response_time = statistics.stdev(metrics["response_time"])
        except statistics.StatisticsError:
            stdev_response_time = 0
        threshold = mean_response_time + 2 * stdev_response_time  # e.g., 2 standard deviations
        for log_entry in parsed_logs:
            response_time = log_entry.get("response_time")
            if response_time is not None and float(response_time) > threshold:
                anomalies.append(
                    f"High response time detected: {response_time} (threshold: {threshold:.2f})"
                )

    # Calculate average for metrics.
    averaged_metrics = {}
    for key, values in metrics.items():
      if(values):
        averaged_metrics[key] = statistics.mean(values)

    summary = (
        f"Processed {len(parsed_logs)} log entries. "
        f"Severity Counts: {dict(level_counts)}"
    )

    return {
        "level_counts": dict(level_counts),
        "error_messages": error_messages,
        "anomalies": anomalies,
        "metrics": averaged_metrics,
        "summary": "",
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
    summary = log_insights.summary
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

# --- Placeholder Functions for Other Data Types ---

def process_metrics_data(data: str) -> Dict:
    """Placeholder for processing metrics data."""
    logger.warning("Metrics processing not yet implemented.")
    return {"message": "Metrics processing not yet implemented."}

def process_config_data(data: str) -> Dict:
    """Placeholder for processing configuration data."""
    logger.warning("Config processing not yet implemented.")
    return {"message": "Config processing not yet implemented."}

def process_problem_report_data(data: str) -> Dict:
    """Placeholder for processing problem reports (INC, CS, PR tickets)."""
    logger.warning("Problem report processing not yet implemented.")
    return {"message": "Problem report processing not yet implemented."}

def process_text_data(data: str, llm_provider: LLMProvider) -> Dict:
    """Processes generic text data using the LLM."""
    try:
        prompt = settings.text_analysis_prompt.format(data=data) # Use prompt from settings
        result = llm_provider.query(prompt)
        if result:
            return {"summary": result}
        else:
            logger.error("LLM returned an empty response for text data.")
            return {"error": "LLM returned an empty response."}
    except Exception as e:
        logger.error(f"LLM text processing failed: {e}", exc_info=True)
        return {"error": "Error processing text data with LLM."}