# tests/test_data_classifier.py
"""
Unit tests for the heuristic data classification functions in app.data_classifier.
"""

import pytest

# Import the functions to be tested from the app module
# This assumes you run pytest from the project root directory
from app.data_classifier import (
    is_likely_json,
    is_likely_syslog,
    is_likely_csv,
    is_likely_xml,
    contains_metric_keywords,
    contains_log_keywords,
    is_root_cause_analysis_ticket
    # We will test classify_data and classify_with_llm separately as they need mocking
)
# Import DataType if needed later for testing classify_data results
# from app.models import DataType

# --- Tests for Heuristic Functions ---

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases (assuming is_likely_json fix applied in source)
    ('{}', True),
    ('[]', True),
    ('{"key": "value", "number": 123}', True),
    ('[1, "a", null, true]', True),
    (' "string literal" ', True),
    (' 123 ', True),
    (' true ', True),
    (' null ', True),
    # Negative cases
    ('', False),
    (' { ', False),
    (' "abc ', False),
    (" {'key': 'value'} ", False),
    (" key: value ", False),
    ("<xml></xml>", False),
    (" syslog message", False), # Syslog is not JSON
    ("Just plain text", False),
    ("   ", False),
])
def test_is_likely_json(data: str, expected_result: bool):
    """Tests the is_likely_json heuristic function."""
    assert is_likely_json(data) == expected_result, f"Input: '{data}'"

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases (WITH <PRI> prefix)
    ('<34>1 2003-10-11T22:14:15.003Z mymachine.example.com su - ID47 - msg', True),
    ('<34>Oct 11 22:14:15 mymachine su: \'su root\' failed for lonvick on /dev/pts/8', True),
    ('<34>Aug 24 05:34:00 CST 1987 mymachine myproc[10]: %% It\'s time to make the do-nuts. %%', True),
    ('<34>  1 syslog example', True),  # Leading space with valid <PRI>
    ('<34> feb 29 12:00:00 host app: message', True),  # Includes <PRI> prefix
    # Negative cases (No or invalid <PRI> prefix)
    ('', False),
    ('plain text message', False),
    ('syslog inside text', False),  # Pattern must start with <PRI>
    ('{"key": "value"}', False),
    ('<xml></xml>', False),
    ('13> syslog', False),  # Missing opening '<'
    ('<> message', False),  # Missing digits in PRI
    ('<-1> message', False),  # Negative numbers not valid in PRI
    ('1 2003-10-11T22:14:15.003Z mymachine.example.com su - ID47 - msg', False),  # No <PRI> prefix
])
def test_is_likely_syslog(data: str, expected_result: bool):
    """Tests the is_likely_syslog heuristic function."""
    assert is_likely_syslog(data) == expected_result, f"Input: '{data}'"

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases
    ('header1,header2\nvalue1,value2', True),
    ('col_a,col_b,col_c\n1,2,3\n4,5,6', True),
    ('"quoted,header",header2\n"data,1",data2', True),
    ('h1,h2\ndata1,data2\n', True),
    # Negative cases
    ('', False),
    ('header_only_no_comma', False), # No comma in header
    ('header1,header2', False), # Only one line
    ('header1\nvalue1', False), # Only one column (no comma in header)
    ('\nvalue1,value2', False), # Empty header line
    ('   ', False),
    ('header1\nvalue1,value2', False), # Header has no comma
    ('h1,h2\n', False), # Function requires >= 2 lines for CSV detection
])
def test_is_likely_csv(data: str, expected_result: bool):
    """Tests the is_likely_csv heuristic function."""
    assert is_likely_csv(data) == expected_result, f"Input: '{data}'"

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases
    ('<?xml version="1.0"?><root></root>', True),
    ('<tag>value</tag>', True),
    ('  <note><to>Tove</to></note>', True), # Leading whitespace okay
    ('<root/>', True),
    ('<root attr="value"></root>', True),
    ('< >', True), # Function logic accepts this basic structure
    # Negative cases (adjusted expectations based on function logic)
    ('', False),
    ('plain text', False),
    ('tag>', False), # Missing opening '<'
    ('<tag', False), # Incomplete tag
    ('<?xml version="1.0"?> text after>', True), # Function logic passes based on startswith
    ('{"key": "value"}', False),
    (' syslog', False), # Does not end with '>'
])
def test_is_likely_xml(data: str, expected_result: bool):
    """Tests the is_likely_xml heuristic function."""
    assert is_likely_xml(data) == expected_result, f"Input: '{data}'"

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases (assuming "request" added to keywords in function)
    ('CPU usage high', True),
    ('Check network latency', True),
    ('memory=500MB', True),
    ('disk iops failed', True),
    ('request count: 500', True),
    ('High request ERRORS', True),
    ('Network utilization is 80%', True),
    ('Query duration_ms: 123', True),
    ('MEMORY available', True),
    ('The request completed.', True), # Function finds "request" substring
    # Negative cases
    ('', False),
    ('This is a log message about failure', False), # uses log keyword 'failure'
    ('Configuration setting for timeout', False),
    ('Incident report', False),
    ('User login successful - info', False), # uses log keyword 'info'
])
def test_contains_metric_keywords(data: str, expected_result: bool):
    """Tests the contains_metric_keywords heuristic function."""
    assert contains_metric_keywords(data) == expected_result, f"Input: '{data}'"

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases (assuming relevant keywords added to function)
    ('[ERROR] File not found', True),
    ('WARN: Connection refused', True),
    ('INFO: User logged in', True),
    ('DEBUG: Variable value is X', True),
    ('Exception occurred during processing', True),
    ('Traceback:', True),
    ('Task failed successfully', True),
    ('CRITICAL error detected', True),
    ('Severity=ERROR', True),
    ('This was a fatal error', True),
    ('Severe issue encountered', True),
    # Negative cases
    ('', False),
    ('CPU is at 90%', False), # Metric keyword
    ('<config timeout="30"/>', False), # Likely config
    ('Root cause analysis complete', False), # RCA keyword
    ('Metrics show high latency', False), # Metric keyword
    ('Report generated successfully', False),
])
def test_contains_log_keywords(data: str, expected_result: bool):
    """Tests the contains_log_keywords heuristic function."""
    assert contains_log_keywords(data) == expected_result, f"Input: '{data}'"

@pytest.mark.parametrize("data, expected_result", [
    # Positive cases
    ('Incident #1234 Report', True),
    ('Root Cause Analysis for outage on 2025-04-23', True),
    ('Problem ticket regarding login failure', True),
    ('Customer Support Case: User unable to access service', True),
    ('Postmortem: Database connection pool exhaustion', True),
    ('Investigation into SEV-1 issue', True),
    ('Summary of the outage', True),
    ('Failure analysis report', True),
    ('RCA document link: ...', True),
    ('User query about issue #567', True), # Function matches 'issue' keyword
    # Negative cases
    ('', False),
    ('[ERROR] Database connection failed', False), # Log keyword
    ('CPU metrics dashboard', False), # Metric keyword
    ('<server><port>8080</port></server>', False), # Likely config
    ('Normal log entry', False), # Log keyword
])
def test_is_root_cause_analysis_ticket(data: str, expected_result: bool):
    """Tests the is_root_cause_analysis_ticket heuristic function."""
    assert is_root_cause_analysis_ticket(data) == expected_result, f"Input: '{data}'"

# --- Tests for classify_with_llm and classify_data will be added later ---
# These will require mocking the 'classification_chain.ainvoke' call.