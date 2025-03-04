import pytest
from unittest.mock import patch, MagicMock
from app.ai_troubleshooting import (
    process_query,
    process_query_with_logs,
    generate_troubleshooting_prompt,
    parse_llm_response,
)

### **Test Data**
SAMPLE_QUERY = "Why is the disk full?"
SAMPLE_LOGS = {"summary": "Disk usage is at 95%", "anomalies": ["High disk usage"]}
SAMPLE_LLM_RESPONSE = [
    {"generated_text": "- **Root Cause:** Disk is full.\n- **Next Steps:**\n1. Clear temporary files.\n2. Archive old logs.\n3. Increase disk space."}
]
SAMPLE_LLM_RESPONSE_JSON = '{"likely_cause": "Disk is full", "next_steps": ["Clear temporary files", "Archive old logs", "Increase disk space"]}'

### **Mocked Dependencies**
@pytest.fixture
def mock_llm_provider():
    with patch("app.ai_troubleshooting.LLMProvider") as mock_llm:
        yield mock_llm

### **Test Cases**
def test_process_query(mock_llm_provider):
    """Test the `process_query` function with a valid LLM response."""
    mock_llm_provider.return_value.query.return_value = SAMPLE_LLM_RESPONSE

    result = process_query(SAMPLE_QUERY)
    assert result == "Disk is full."

def test_process_query_invalid_response(mock_llm_provider):
    """Test the `process_query` function with an invalid LLM response."""
    mock_llm_provider.return_value.query.return_value = "Invalid response"

    result = process_query(SAMPLE_QUERY)
    assert result == "Error: Unexpected LLM response format."

def test_process_query_failure(mock_llm_provider):
    """Test the `process_query` function when the LLM query fails."""
    mock_llm_provider.return_value.query.side_effect = Exception("LLM failed")

    result = process_query(SAMPLE_QUERY)
    assert "Error: LLM query failed" in result

def test_process_query_with_logs(mock_llm_provider):
    """Test the `process_query_with_logs` function with a valid LLM response."""
    mock_llm_provider.return_value.query.return_value = SAMPLE_LLM_RESPONSE

    result = process_query_with_logs(SAMPLE_QUERY, SAMPLE_LOGS)
    assert result == {
        "likely_cause": "Disk is full.",
        "next_steps": ["Clear temporary files.", "Archive old logs.", "Increase disk space."],
    }

def test_process_query_with_logs_failure(mock_llm_provider):
    """Test the `process_query_with_logs` function when the LLM query fails."""
    mock_llm_provider.return_value.query.side_effect = Exception("LLM failed")

    result = process_query_with_logs(SAMPLE_QUERY, SAMPLE_LOGS)
    assert "Error: AI troubleshooting failed" in result["error"]

def test_generate_troubleshooting_prompt():
    """Test the `generate_troubleshooting_prompt` function."""
    prompt = generate_troubleshooting_prompt(SAMPLE_LOGS)
    assert "Disk usage is at 95%" in prompt
    assert "High disk usage" in prompt
    assert "**Response Format (STRICT):**" in prompt

def test_parse_llm_response_regex():
    """Test the `parse_llm_response` function with a regex-parsable response."""
    response_text = "- **Root Cause:** Disk is full.\n- **Next Steps:**\n1. Clear temporary files.\n2. Archive old logs.\n3. Increase disk space."
    result = parse_llm_response([{"generated_text": response_text}])
    assert result == {
        "likely_cause": "Disk is full.",
        "next_steps": ["Clear temporary files.", "Archive old logs.", "Increase disk space."],
    }

def test_parse_llm_response_json():
    """Test the `parse_llm_response` function with a JSON response."""
    result = parse_llm_response(SAMPLE_LLM_RESPONSE_JSON)
    assert result == {
        "likely_cause": "Disk is full",
        "next_steps": ["Clear temporary files", "Archive old logs", "Increase disk space"],
    }

def test_parse_llm_response_invalid():
    """Test the `parse_llm_response` function with an invalid response."""
    result = parse_llm_response("Invalid response")
    assert result == {
        "likely_cause": "Unknown",
        "next_steps": ["No specific next steps provided."],
    }

def test_parse_llm_response_empty():
    """Test the `parse_llm_response` function with an empty response."""
    result = parse_llm_response("")
    assert result == {
        "likely_cause": "Unknown",
        "next_steps": ["No specific next steps provided."],
    }