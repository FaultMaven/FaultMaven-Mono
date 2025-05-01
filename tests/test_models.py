# tests/test_models.py
"""
Unit tests for Pydantic models defined in app.models.
Focuses on testing custom validators.
"""

import pytest
from pydantic import ValidationError
from app.models import DataInsightsResponse, LogInsights

# Import models and constants to be tested
from app.models import (
    QueryRequest,
    TroubleshootingResponse, # <-- Add this
    DataInsightsResponse,    # <-- Add this
    MAX_QUERY_LENGTH,
    QUERY_REGEX
    # Import other models if you add tests for them
)

# --- Tests for QueryRequest Validator ---

@pytest.mark.parametrize("valid_query", [
    "check service status",
    "What are the errors between 10:00 and 11:00?",
    "Show logs for pod xyz-123",
    "Why did request abc-987 fail?",
    "12345",
    "simple-query?!",
    "a" * MAX_QUERY_LENGTH, # Test maximum length
])
def test_query_request_valid(valid_query: str):
    """Tests that QueryRequest passes validation for valid queries."""
    try:
        qr = QueryRequest(query=valid_query)
        # Check if the value is stored correctly (optional)
        assert qr.query == valid_query
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly for valid query '{valid_query}': {e}")

@pytest.mark.parametrize("invalid_query, expected_error_substring", [
    # Test case for empty string (fails custom length check first)
    ("", f"Query length must be between 1 and {MAX_QUERY_LENGTH}"),
    # Test case for string exceeding max length (fails built-in Pydantic check first)
    ("a" * (MAX_QUERY_LENGTH + 1), f"String should have at most {MAX_QUERY_LENGTH} characters"),
])
def test_query_request_invalid_length(invalid_query: str, expected_error_substring: str):
    """
    Tests that QueryRequest fails validation for queries with invalid length,
    checking for the appropriate error message (custom or Pydantic built-in).
    """
    with pytest.raises(ValidationError) as excinfo:
        QueryRequest(query=invalid_query)
    # Check that the expected substring (either custom or Pydantic's) is in the error
    assert expected_error_substring in str(excinfo.value)

@pytest.mark.parametrize("invalid_query", [
    "what is <script>alert('x')</script> doing?", # Invalid characters: < > /
    "show logs for pod 🚀", # Invalid character: emoji
    "select * from users;", # Invalid character: *
    "你好世界", # Invalid characters: non-ASCII (based on current regex)
])
def test_query_request_invalid_chars(invalid_query: str):
    """
    Tests that QueryRequest fails validation for queries with characters
    not matching QUERY_REGEX (assuming the validator was fixed to raise ValueError).
    """
    with pytest.raises(ValidationError) as excinfo:
        QueryRequest(query=invalid_query)
    # Check that the error message mentions invalid characters
    assert "Query contains invalid characters" in str(excinfo.value)


# --- Optional: Basic Instantiation Tests for other models ---
# These just confirm the models can be created without errors,
# implicitly testing default values and basic type hints.

def test_troubleshooting_response_instantiation():
    """Test basic creation of TroubleshootingResponse."""
    resp = TroubleshootingResponse(answer="It looks okay.", action_items=["Check logs", "Restart pod"])
    assert resp.answer == "It looks okay."
    assert resp.action_items == ["Check logs", "Restart pod"]
    resp_no_actions = TroubleshootingResponse(answer="All clear.")
    assert resp_no_actions.answer == "All clear."
    assert resp_no_actions.action_items is None

def test_data_insights_response_instantiation():
    """Test basic creation of DataInsightsResponse, including Pydantic coercion."""
    # --- Test case 1: Inputting a dict that matches LogInsights ---
    input_insight_dict = {"summary": "Found 10 errors"}
    resp1 = DataInsightsResponse(
        message="Processed",
        classified_type="log",
        session_id="xyz",
        insights=input_insight_dict
    )
    assert resp1.message == "Processed"
    # Assert against the expected Pydantic model instance
    expected_log_insight = LogInsights(summary="Found 10 errors")
    assert resp1.insights == expected_log_insight
    assert isinstance(resp1.insights, LogInsights)
    assert resp1.insights.summary == "Found 10 errors"
    assert resp1.insights.level_counts == {} # Check defaults

    # --- Test case 2: Inputting a simple dictionary ---
    input_simple_dict = {"mcp_result": "value", "status": 200}
    resp2 = DataInsightsResponse(
        message="MCP Done",
        classified_type="mcp",
        session_id="abc",
        insights=input_simple_dict
    )
    assert resp2.message == "MCP Done"
    # --- CORRECTED ASSERTIONS for Test Case 2 ---
    # Pydantic coerces the dict into the first compatible Union type (LogInsights)
    # Assert that the result IS a LogInsights object (with default values)
    assert isinstance(resp2.insights, LogInsights)
    # Assert it matches a default LogInsights object
    expected_default_insight = LogInsights() # Creates default values for LogInsights
    assert resp2.insights == expected_default_insight
    # Optionally check specific default values
    assert resp2.insights.summary == ""
    assert resp2.insights.level_counts == {}
    # The original input dict is NOT preserved due to coercion
    # assert resp2.insights == input_simple_dict # This would fail

    # --- Test case 3: Inputting a string ---
    input_string = "Processing complete, no specific insights."
    resp3 = DataInsightsResponse(
        message="Done",
        classified_type="text",
        session_id="def",
        insights=input_string
    )
    assert resp3.message == "Done"
    assert isinstance(resp3.insights, str)
    assert resp3.insights == input_string

    # --- Test case 4: Inputting None ---
    resp4 = DataInsightsResponse(
        message="Pending",
        classified_type="unknown",
        session_id="ghi"
        # insights defaults to None
    )
    assert resp4.message == "Pending"
    assert resp4.insights is None

    # Example using LogInsights (ensure LogInsights is importable if used)
    # from app.models import LogInsights # Would need this import too
    # insights_obj = LogInsights(summary="Test Summary")
    # resp_log = DataInsightsResponse(
    #     message="Processed Logs", classified_type="log", session_id="abc", insights=insights_obj
    # )
    # assert resp_log.insights == insights_obj

# Add similar basic instantiation tests for other complex models if desired
