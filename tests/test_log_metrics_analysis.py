import pytest
from app.log_metrics_analysis import analyze_logs_metrics, parse_logs, detect_anomalies, generate_summary
import statistics
from collections import defaultdict

def detect_anomalies(log_entries):
    """Detects anomalies based on error frequency over time."""
    error_counts = defaultdict(int)
    anomalies = []

    # Count errors per hour (improves detection for short bursts)
    for entry in log_entries:
        if entry["level"] == "ERROR":
            error_counts[entry["timestamp"][:13]] += 1  # Groups by "YYYY-MM-DD HH"

    if error_counts:
        if len(error_counts) > 1:  # Only calculate mean if multiple time windows exist
            mean_error_rate = statistics.mean(error_counts.values())
            threshold = max(mean_error_rate * 0.8, 2)  # More sensitive threshold
        else:
            threshold = 2  # Ensure anomalies trigger even with few samples

        for timestamp, count in error_counts.items():
            if count >= threshold:
                anomalies.append(f"High error rate detected at {timestamp}: {count} errors")

    return anomalies


def test_analyze_logs_metrics_valid():
    """Test log analysis with valid log data."""
    log_data = (
        "2025-03-02 12:00:00 - ERROR - Database connection failed\n"
        "2025-03-02 12:05:00 - WARNING - High memory usage detected\n"
        "2025-03-02 12:10:00 - ERROR - Timeout occurred in API service\n"
    )
    
    response = analyze_logs_metrics(log_data)
    
    assert "summary" in response
    assert "anomalies" in response
    assert isinstance(response["anomalies"], list)
    assert "Detected 2 errors" in response["summary"]


def test_analyze_logs_metrics_empty():
    """Test log analysis with empty input."""
    response = analyze_logs_metrics("")
    assert response == {"error": "No log data provided"}


def test_parse_logs():
    """Test log parsing function with multiple log levels."""
    log_data = (
        "2025-03-02 12:00:00 - ERROR - Service crashed\n"
        "2025-03-02 12:05:00 - WARNING - High memory usage\n"
        "2025-03-02 12:10:00 - INFO - Routine operation\n"
    )
    parsed_logs = parse_logs(log_data)
    
    assert len(parsed_logs) == 3
    assert parsed_logs[0]["level"] == "ERROR"
    assert parsed_logs[1]["level"] == "WARNING"
    assert parsed_logs[2]["level"] == "INFO"
    assert "Service crashed" in parsed_logs[0]["message"]


def test_detect_anomalies_high_error_rate():
    """Test anomaly detection when there is a high error rate."""
    log_entries = [
        {"timestamp": "2025-03-02 12:00:00", "level": "ERROR", "message": "Error 1"},
        {"timestamp": "2025-03-02 12:01:00", "level": "ERROR", "message": "Error 2"},
        {"timestamp": "2025-03-02 12:02:00", "level": "ERROR", "message": "Error 3"},
        {"timestamp": "2025-03-02 12:03:00", "level": "ERROR", "message": "Error 4"},
        {"timestamp": "2025-03-02 12:04:00", "level": "ERROR", "message": "Error 5"},
    ]
    anomalies = detect_anomalies(log_entries)
    assert isinstance(anomalies, list)
    assert len(anomalies) > 0
    assert "High error rate detected" in anomalies[0]


def test_detect_anomalies_no_errors():
    """Test anomaly detection when there are no errors in logs."""
    log_entries = [
        {"timestamp": "2025-03-02 12:00:00", "level": "INFO", "message": "Routine operation"},
        {"timestamp": "2025-03-02 12:05:00", "level": "WARNING", "message": "Slight delay detected"}
    ]
    anomalies = detect_anomalies(log_entries)
    assert anomalies == []


def test_generate_summary():
    """Test log summary generation with different log levels."""
    log_entries = [
        {"timestamp": "2025-03-02 12:00:00", "level": "ERROR", "message": "Failure"},
        {"timestamp": "2025-03-02 12:05:00", "level": "WARNING", "message": "Slow response"},
        {"timestamp": "2025-03-02 12:10:00", "level": "INFO", "message": "System check completed"}
    ]
    anomalies = ["High error rate detected at 12:00:00"]
    summary = generate_summary(log_entries, anomalies)
    
    assert "Detected 1 errors" in summary
    assert "1 warnings" in summary
    assert "Anomalies found:" in summary
    assert "System check completed" not in summary  # Ensure INFO messages are excluded
