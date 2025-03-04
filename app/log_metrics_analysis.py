import re
import statistics
from collections import defaultdict
from app.logger import logger


def analyze_logs_metrics(log_data):
    """
    Processes logs and system metrics to extract key patterns and anomalies.
    
    Args:
        log_data (str): Raw logs and metrics data.

    Returns:
        dict: Structured insights including detected errors, anomalies, and trends.
    """
    if not log_data:
        return {"error": "No log data provided"}
    
    structured_logs = parse_logs(log_data)
    anomalies = detect_anomalies(structured_logs)
    summary = generate_summary(structured_logs, anomalies)
    
    return {"summary": summary, "anomalies": anomalies}


def parse_logs(log_data):
    """
    Parses raw log data to extract errors, warnings, and timestamps.
    
    Args:
        log_data (str): Raw logs as a single string.

    Returns:
        list: List of parsed log entries.
    """
    log_entries = []
    log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (ERROR|WARNING|INFO) - (.+)")
    
    for line in log_data.split("\n"):
        match = log_pattern.match(line)
        if match:
            timestamp, level, message = match.groups()
            log_entries.append({"timestamp": timestamp, "level": level, "message": message})
    
    return log_entries


def detect_anomalies(log_entries):
    """
    Detects anomalies based on error frequency and log patterns.
    
    Args:
        log_entries (list): List of parsed log entries.

    Returns:
        list: Detected anomalies (e.g., error spikes, repeated patterns).
    """
    error_counts = defaultdict(int)
    anomalies = []
    
    for entry in log_entries:
        if entry["level"] == "ERROR":
            error_counts[entry["timestamp"][:13]] += 1  # Count errors per hour
    
    if error_counts:
        mean_error_rate = statistics.mean(error_counts.values())
        threshold = mean_error_rate * 2  # Define anomaly threshold as 2x mean
        
        for timestamp, count in error_counts.items():
            if count > threshold:
                anomalies.append(f"High error rate detected at {timestamp}: {count} errors")
    
    return anomalies


def generate_summary(log_entries, anomalies):
    """
    Generates a summary from the log analysis.
    
    Args:
        log_entries (list): List of parsed log entries.
        anomalies (list): Detected anomalies.

    Returns:
        str: Summary of log insights.
    """
    error_count = sum(1 for entry in log_entries if entry["level"] == "ERROR")
    warning_count = sum(1 for entry in log_entries if entry["level"] == "WARNING")
    
    summary = (
        f"Log analysis completed. Detected {error_count} errors and {warning_count} warnings. "
        f"{'Anomalies found: ' + ', '.join(anomalies) if anomalies else 'No anomalies detected.'}"
    )
    
    return summary
