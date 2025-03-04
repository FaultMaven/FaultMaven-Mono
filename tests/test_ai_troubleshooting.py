import pytest
from unittest.mock import patch
from app.ai_troubleshooting import troubleshoot_issue, generate_troubleshooting_prompt, parse_llm_response

@pytest.mark.parametrize(
    "analysis_results, expected_substring",
    [
        ({"summary": "High CPU load", "anomalies": ["CPU usage > 90%"]}, "High CPU load"),
        ({"summary": "Network timeout", "anomalies": ["Latency spikes detected"]}, "Network timeout"),
        ({}, "No detailed summary available"),
    ]
)
def test_generate_troubleshooting_prompt(analysis_results, expected_substring):
    """Test prompt generation based on log insights."""
    prompt = generate_troubleshooting_prompt(analysis_results)
    assert expected_substring in prompt
    assert "**Root Cause:**" in prompt
    assert "**Next Steps:**" in prompt

@patch("app.llm_provider.LLMProvider.query")
def test_troubleshoot_issue_success(mock_query):
    """Test troubleshooting function when LLM returns valid data."""
    mock_query.return_value = [{"generated_text": "Root Cause: High CPU usage. Next Steps:\n1. Optimize queries.\n2. Scale system."}]
    analysis_results = {"summary": "High CPU load", "anomalies": ["CPU usage > 90%"]}
    response = troubleshoot_issue(analysis_results)
    assert "likely_cause" in response
    assert "next_steps" in response
    assert response["likely_cause"] == "High CPU usage"
    assert response["next_steps"] == ["Optimize queries.", "Scale system."]

@patch("app.llm_provider.LLMProvider.query", side_effect=Exception("LLM API failure"))
def test_troubleshoot_issue_failure(mock_query):
    """Test handling of LLM failures in troubleshooting."""
    analysis_results = {"summary": "Disk full error", "anomalies": ["Low disk space warning"]}
    response = troubleshoot_issue(analysis_results)
    assert "error" in response
    assert "AI troubleshooting failed" in response["error"]
    assert "LLM API failure" in response["details"]

def test_troubleshoot_issue_no_analysis_results():
    """Test troubleshoot_issue with no analysis results."""
    response = troubleshoot_issue(None)
    assert "error" in response
    assert "Invalid or missing analysis data provided" in response["error"]

def test_troubleshoot_issue_invalid_analysis_results():
    """Test troubleshoot_issue with invalid analysis results."""
    response = troubleshoot_issue("not a dict")
    assert "error" in response
    assert "Invalid or missing analysis data provided" in response["error"]

@pytest.mark.parametrize(
    "llm_response, expected_cause, expected_steps",
    [
        (
            "Likely root cause: Memory leak detected. Next Steps:\n"
            "1. Restart application.\n"
            "2. Check memory profiling.",
            "Memory leak detected",
            ["Restart application.", "Check memory profiling."]
        ),
        (
            "Root Cause: High CPU usage. Next Steps:\n"
            "1. Optimize queries.\n"
            "2. Scale system.",
            "High CPU usage",
            ["Optimize queries.", "Scale system."]
        ),
        (
            "Error detected. Next Steps:\n"
            "1. Investigate logs.\n"
            "2. Monitor CPU load.",
            "Unknown",
            ["Investigate logs.", "Monitor CPU load."]
        ),
        ("Root Cause: Test Case", "Test Case", []),
        ([], "Unknown", ["No specific next steps provided."]),
        ("Invalid response format", "Unknown", ["No specific next steps provided."]) #corrected line
    ]
)
def test_parse_llm_response(llm_response, expected_cause, expected_steps):
    """Test response parsing from LLM output."""
    if isinstance(llm_response, str):
        response = llm_response
    else:
        response = [{"generated_text": llm_response}]
    parsed_response = parse_llm_response(response)
    assert parsed_response["likely_cause"] == expected_cause
    assert parsed_response["next_steps"] == expected_steps
