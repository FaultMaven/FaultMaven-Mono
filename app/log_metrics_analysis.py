# app/log_metrics_analysis.py
import re
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any
from app.logger import logger
from app.llm_provider import LLMProvider, LLMParsingError  # Import LLMParsingError
from config.settings import settings  # Import settings
#from fastapi import Depends # No need of 'Depends'


# --- Helper functions

def process_logs_data(logs: str, llm_provider: LLMProvider) -> Dict[str, Any]:  # Removed Depends
    """
    Processes raw logs and metrics, ensuring valid input before analysis.

    Args:
        logs (str): Raw logs or observability data.
        llm_provider (LLMProvider): The LLM provider instance.

    Returns:
        dict: Structured statistics and diagnostic findings.
    """
    if not isinstance(logs, str) or not logs.strip():
        raise ValueError("Invalid or empty log data provided.")

    log_insights = analyze_logs_metrics(logs)
    diagnostic_findings = query_llm_for_insights(log_insights, llm_provider)  # Use llm_provider
    if isinstance(diagnostic_findings, str) and diagnostic_findings.startswith("Error"):
        log_insights["diagnostic_findings"] = "LLM query failed." # Use a default string
    else:
        log_insights["diagnostic_findings"] = diagnostic_findings
    return log_insights

def analyze_logs_metrics(data: str) -> Dict[str, Any]:
    """
    Extracts structured insights from logs and metrics.

    Args:
        data (str): Raw logs and/or metrics data.

    Returns:
        dict: Structured insights including detected errors, anomalies, and log summaries.
    Raises:
        ValueError: If no valid data is provided.
    """
    if not data or not isinstance(data, str):
        raise ValueError("No valid data provided")

    log_entries = parse_logs(data)
    metric_entries = parse_metrics(data)

    # Extract key statistics
    start_time, end_time, duration = extract_log_time_range(log_entries)
    error_count = sum(1 for log in log_entries if log["level"] == "ERROR")
    warning_count = sum(1 for log in log_entries if log["level"] == "WARNING")

    categorized_logs = categorize_logs(log_entries)
    anomalies = detect_anomalies(log_entries, metric_entries)

    summary = (
        f"Log analysis completed. Start time: {start_time}, Duration: {duration}. "
        f"Detected {error_count} errors and {warning_count} warnings."
    )

    return {
        "summary": summary,
        "duration": duration,
        "error_count": error_count,
        "warning_count": warning_count,
        "categorized_logs": {k: len(v) for k, v in categorized_logs.items()},  # Send counts
        "metrics": {k: round(statistics.mean(v), 2) for k, v in metric_entries.items() if v},  # Use mean values
        "anomalies": anomalies,  # Include anomalies
    }

def parse_logs(data: str) -> List[Dict[str, str]]:
    """
    Parses raw log data to extract errors, warnings, and timestamps.

    Args:
        data (str): Raw logs as a single string.

    Returns:
        list: List of parsed log entries.
    """
    log_entries = []
    log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*-\s*(ERROR|WARNING|INFO)\s*-\s*(.+)")

    for line in data.split("\n"):
        match = log_pattern.match(line)
        if match:
            timestamp, level, message = match.groups()
            log_entries.append({"timestamp": timestamp, "level": level, "message": message})

    return log_entries

def extract_log_time_range(log_entries: List[Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Extracts start time, end time, and duration from logs.

    Args:
        log_entries (list): List of parsed log entries.

    Returns:
        tuple: (start_time, end_time, duration)
    Raises:
        ValueError if timestamps cannot be parsed.
    """
    timestamps = [entry["timestamp"] for entry in log_entries if entry.get("timestamp")]

    if not timestamps:
        return "Unknown", "Unknown", "Unknown duration"

    start_time = min(timestamps)
    end_time = max(timestamps)

    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    duration = str(end_dt - start_dt)

    return start_time, end_time, duration

def categorize_logs(log_entries: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Categorizes logs into structured types.

    Args:
        log_entries (list): List of parsed log entries.

    Returns:
        dict: Categorized logs (e.g., "Database Errors", "Network Issues").
    """
    categories = defaultdict(list)

    for entry in log_entries:
        message = entry["message"].lower()

        if "database" in message or "sql" in message:
            categories["Database Errors"].append(entry)
        elif "timeout" in message or "latency" in message:
            categories["Network Issues"].append(entry)
        elif "out of memory" in message or "oom" in message:
            categories["Memory Issues"].append(entry)
        else:
            categories["General Errors"].append(entry)

    return categories

def parse_metrics(data: str) -> Dict[str, List[float]]:
    """
    Extracts numerical metrics from log data (e.g., CPU, memory, response time).

    Args:
        data (str): Raw logs and metrics data.

    Returns:
        dict: Extracted metric values.
    """
    metric_entries = defaultdict(list)
    metric_pattern = re.compile(r"(\w+)\s*=\s*([\d.]+)")

    for line in data.split("\n"):
        matches = metric_pattern.findall(line)
        for key, value in matches:
            key = key.lower().replace(" ", "_")
            metric_entries[key].append(float(value))

    return metric_entries

def detect_anomalies(log_entries: List[Dict[str, str]], metric_entries: Dict[str, List[float]]) -> List[str]:
    """
    Detects anomalies in logs and metrics.

    Args:
        log_entries (list): List of parsed log entries.
        metric_entries (dict): Extracted system metrics.

    Returns:
        list: Detected anomalies (error spikes, metric outliers).
    """
    anomalies = []
    error_counts = defaultdict(int)

    for entry in log_entries:
        if entry["level"] == "ERROR":
            error_counts[entry["timestamp"][:13]] += 1

    if error_counts:
        mean_error_rate = statistics.mean(error_counts.values())
        threshold = mean_error_rate * settings.error_rate_anomaly_threshold_factor

        for timestamp, count in error_counts.items():
            if count > threshold:
                anomalies.append(f"High error rate detected at {timestamp}: {count} errors")

    for metric, values in metric_entries.items():
        if len(values) < settings.min_data_points_for_anomaly_detection:
            continue

        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        threshold = mean_value + (settings.metric_anomaly_threshold_std_dev * std_dev)

        for value in values:
            if value > threshold:
                anomalies.append(f"Anomalous {metric} detected: {value} (expected below {threshold:.2f})")

    return anomalies

def query_llm_for_insights(analysis_results: Dict[str, Any], llm_provider: LLMProvider) -> str: # Removed Depends
    """
    Queries LLM to analyze logs and provide context-aware diagnostic findings.

    Args:
        analysis_results (dict): Extracted log and metric insights.
        llm_provider (LLMProvider): The LLM provider instance

    Returns:
        str: AI-generated diagnostic findings.
    """
    try:
        prompt = settings.troubleshooting_prompt.format(
            user_query="", #query is empty
            log_summary=analysis_results['summary'],
            anomalies=', '.join(analysis_results.get('anomalies', [])) if analysis_results.get('anomalies') else "No anomalies detected",
            categorized_logs = analysis_results.get("categorized_logs", {}),
            metrics = analysis_results.get("metrics", {})
        )
        return llm_provider.query(prompt)

    except LLMParsingError as e:
        logger.error(f"LLM parsing error: {e}", exc_info=True)
        return "Could not process the LLM response."
    except Exception as e:
        logger.error(f"LLM Query Failed: {e}", exc_info=True)
        return "Error retrieving diagnostic findings."