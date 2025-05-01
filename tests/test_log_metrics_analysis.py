# tests/test_log_metrics_analysis.py
"""
Unit tests for the app.log_metrics_analysis module.
Uses mocking for LLM chain calls and subprocesses.
"""

# --- Imports ---
import pytest
import statistics
import logging
from app.logger import logger
from collections import defaultdict
from typing import Dict, Any, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock, patch

import asyncio
import subprocess
import json
import time

# --- Functions/Classes Under Test ---
from app.log_metrics_analysis import (
    analyze_logs,
    process_data_summary,
    process_text_data,
    format_log_data_for_summary, # Helper may be implicitly tested or tested separately
    process_logs_data
)
from config.settings import settings
from app.models import LogInsights, DataType
from langchain_core.messages import BaseMessage # Import for type hints

# --- Test Data Samples ---
TS_NOW = time.time()
TS1 = TS_NOW - 3600
LOG_INFO_1 = {"level": "info", "message": "User logged in", "response_time_ms": 55.0}
LOG_INFO_2 = {"level": "INFO", "message": "Request processed", "response_time_ms": 65.0, "status_code": 200}
LOG_WARN_1 = {"level": "warn", "message": "Cache miss", "response_time_ms": 110.0, "status_code": 200}
LOG_ERR_1 = {"level": "error", "message": "Connection refused", "response_time_ms": 500.0, "status_code": 503}
LOG_ERR_2 = {"level": "ERR", "message": "Null pointer exception", "status_code": 500}
LOG_CRIT_1 = {"level": "critical", "message": "Filesystem full", "status_code": 500}
LOG_NO_LEVEL = {"message": "Generic message without level", "response_time_ms": 70.0}
LOG_HIGH_LATENCY = {"level": "info", "message": "Slow query", "response_time_ms": 3000.0, "status_code": 200}
LOG_INVALID_METRIC = {"level": "info", "message": "Metric invalid", "response_time_ms": "not a number"}

# --- Tests for analyze_logs (Keep all 9 passing tests) ---
def test_analyze_logs_empty_input():
    parsed_logs = []; result = analyze_logs(parsed_logs); assert result == {"level_counts": {},"error_messages": [],"anomalies": [],"metrics": {},"summary": ""}
def test_analyze_logs_level_counts():
    parsed_logs = [LOG_INFO_1, LOG_INFO_2, LOG_WARN_1, LOG_ERR_1, LOG_ERR_2, LOG_CRIT_1, LOG_NO_LEVEL]; result = analyze_logs(parsed_logs); assert result["level_counts"] == {"info": 2, "warn": 1, "error": 1, "err": 1, "critical": 1, "unknown": 1}
def test_analyze_logs_error_messages():
     parsed_logs = [LOG_INFO_1, LOG_WARN_1, LOG_ERR_1, LOG_ERR_2, LOG_CRIT_1]; result = analyze_logs(parsed_logs); assert len(result["error_messages"]) == 3; assert "Connection refused" in result["error_messages"]; assert result["level_counts"].get("error", 0) == 1; assert result["level_counts"].get("err", 0) == 1
def test_analyze_logs_metrics_calculation():
     parsed_logs = [LOG_INFO_1, LOG_INFO_2, LOG_WARN_1, LOG_ERR_1, LOG_ERR_2, LOG_CRIT_1, LOG_NO_LEVEL, LOG_HIGH_LATENCY, LOG_INVALID_METRIC]; result = analyze_logs(parsed_logs); metrics = result["metrics"]; valid_rts = [55.0, 65.0, 110.0, 500.0, 70.0, 3000.0]; expected_avg_rt = statistics.mean(valid_rts); assert metrics["response_time_ms"] == pytest.approx(expected_avg_rt); assert metrics["status_code_distribution"] == {200: 3, 503: 1, 500: 2}
def test_analyze_logs_anomaly_detection():
     parsed_logs = [LOG_INFO_1, LOG_INFO_2, LOG_WARN_1, LOG_ERR_1, LOG_NO_LEVEL, {"level": "info", "message": "Normal query 1", "response_time_ms": 80.0}, {"level": "info", "message": "Normal query 2", "response_time_ms": 90.0}, LOG_HIGH_LATENCY]; result = analyze_logs(parsed_logs); assert len(result["anomalies"]) >= 1; assert any("High response time detected: 3000.00ms" in a for a in result["anomalies"])
def test_analyze_logs_anomaly_detection_insufficient_data():
     parsed_logs = [ LOG_INFO_1, LOG_HIGH_LATENCY ]; result = analyze_logs(parsed_logs); assert len(result["anomalies"]) == 0
def test_analyze_logs_missing_fields():
     parsed_logs = [{"message": "Only message", "response_time_ms": 10.0}, {"level": "info", "response_time_ms": 20.0}, {"level": "error", "message": "Error msg"}, {}]; result = analyze_logs(parsed_logs); assert result["level_counts"] == {"unknown": 2, "info": 1, "error": 1}; assert result["error_messages"] == ["Error msg"]; assert result["metrics"] == {"response_time_ms": pytest.approx(15.0)}
def test_analyze_logs_error_message_limit():
     parsed_logs = [{"level": "error", "message": f"Error message {i}"} for i in range(30)]; result = analyze_logs(parsed_logs); assert len(result["error_messages"]) == 20
def test_analyze_logs_anomaly_limit():
     base_values = [50.0] * 5; anomalous_values = [1000.0] * 20; parsed_logs = [{"level":"info", "message":f"v{v}", "response_time_ms": v} for v in base_values + anomalous_values]; result = analyze_logs(parsed_logs); assert len(result["anomalies"]) <= 10


# === Tests for process_data_summary (Using **Chain Object** Mocking) ===

@pytest.mark.asyncio
async def test_process_data_summary_success(mocker):
    """Test LLM summary generation when valid insights are provided."""
    mock_summary_text = "Generated LLM summary."
    # --- Mock the ENTIRE chain object ---
    mock_chain = mocker.patch('app.log_metrics_analysis.log_summary_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(return_value=mock_summary_text) # Configure ainvoke on mock
    insights = LogInsights(level_counts={"error": 2})
    expected_chain_input_str = format_log_data_for_summary(insights)
    # Assume history is passed, even if None (defaults to [] in function call)
    test_history = None

    result_summary = await process_data_summary(insights, history=test_history)

    assert result_summary == mock_summary_text
    mock_chain.ainvoke.assert_awaited_once_with({
        "log_analysis_data": expected_chain_input_str, "history": [] # Checks history was processed
    })

@pytest.mark.asyncio
async def test_process_data_summary_no_insights(mocker):
    """Test summary returns error msg when LogInsights yields no formatted data but LLM is still called."""
    # Arrange
    # Mock the chain object, setup its ainvoke attribute to return None (AsyncMock default)
    mock_chain = mocker.patch('app.log_metrics_analysis.log_summary_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(return_value=None)
    insights = LogInsights() # Empty insights
    # Calculate the expected default input string from the helper
    expected_chain_input_str = format_log_data_for_summary(insights)
    assert expected_chain_input_str == "Log data processed, but no specific programmatic insights extracted."

    # Act
    result_summary = await process_data_summary(insights)

    # Assert
    # --- CORRECTED ASSERTIONS ---
    # Check the function returns the specific error message for empty LLM response
    assert result_summary == "Error: LLM returned no summary."
    # Verify the chain WAS called with the default formatted string
    mock_chain.ainvoke.assert_awaited_once_with({
        "log_analysis_data": expected_chain_input_str, "history": []
    })

@pytest.mark.asyncio
async def test_process_data_summary_llm_error(mocker):
    """Test summary generation when the mocked LLM chain call fails."""
    test_exception = Exception("Simulated LLM API Error")
    mock_chain = mocker.patch('app.log_metrics_analysis.log_summary_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(side_effect=test_exception) # Configure to raise error
    insights = LogInsights(level_counts={"warn": 1})
    expected_chain_input_str = format_log_data_for_summary(insights)

    result_summary = await process_data_summary(insights, history=None)

    assert result_summary == "Error: Failed to generate summary via LLM." # Check exact error msg
    mock_chain.ainvoke.assert_awaited_once_with({
        "log_analysis_data": expected_chain_input_str, "history": []
    })

@pytest.mark.asyncio
async def test_process_data_summary_llm_empty_response(mocker):
    """Test summary generation when the mocked LLM chain returns empty/whitespace."""
    mock_chain = mocker.patch('app.log_metrics_analysis.log_summary_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(return_value="  ") # Simulate whitespace response
    insights = LogInsights(level_counts={"info": 5})
    expected_chain_input_str = format_log_data_for_summary(insights)

    result_summary = await process_data_summary(insights)

    # Function returns error message because result.strip() is falsy
    assert result_summary == "Error: LLM returned no summary."
    mock_chain.ainvoke.assert_awaited_once_with({
        "log_analysis_data": expected_chain_input_str, "history": []
    })


# === Tests for process_text_data (Using **Chain Object** Mocking) ===

@pytest.mark.asyncio
async def test_process_text_data_success(mocker):
    """Test successful text analysis via LLM."""
    test_data = "This is text."
    mock_summary = "LLM analysis result."
    mock_chain = mocker.patch('app.log_metrics_analysis.text_analysis_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(return_value=mock_summary)

    result = await process_text_data(test_data, history=None)

    assert result == {"summary": mock_summary}
    mock_chain.ainvoke.assert_awaited_once_with({
        "text_data": test_data, "history": []
    })

@pytest.mark.asyncio
async def test_process_text_data_empty_input(mocker):
    """Test text analysis skips LLM call with empty input string."""
    mock_chain = mocker.patch('app.log_metrics_analysis.text_analysis_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock()

    result = await process_text_data("")

    assert result == {"summary": "No text data provided."}
    mock_chain.ainvoke.assert_not_awaited()

@pytest.mark.asyncio
async def test_process_text_data_llm_error(mocker):
    """Test text analysis when the mocked LLM chain call fails."""
    test_data = "Some text here."
    test_exception = Exception("Simulated LLM API Error")
    mock_chain = mocker.patch('app.log_metrics_analysis.text_analysis_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(side_effect=test_exception)

    result = await process_text_data(test_data)

    assert result == {"error": "Error processing text data with LLM."}
    mock_chain.ainvoke.assert_awaited_once_with({
        "text_data": test_data, "history": []
    })

@pytest.mark.asyncio
async def test_process_text_data_llm_empty_response(mocker):
    """Test text analysis when the mocked LLM chain returns empty/whitespace."""
    test_data = "Input text."
    mock_chain = mocker.patch('app.log_metrics_analysis.text_analysis_chain', autospec=True)
    mock_chain.ainvoke = AsyncMock(return_value="  ") # Simulate whitespace response

    result = await process_text_data(test_data)

    # Function returns error dict because result.strip() is falsy
    assert result == {"error": "LLM returned no analysis for the text."}
    mock_chain.ainvoke.assert_awaited_once_with({
        "text_data": test_data, "history": []
    })


# === Tests for process_logs_data ===

# Helper to create a mock subprocess result
def create_mock_process(stdout_str="", stderr_str="", returncode=0):
    """Creates a mock CompletedProcess object for simulating subprocess.run."""
    process_mock = MagicMock(spec=subprocess.CompletedProcess)
    process_mock.stdout = stdout_str.encode('utf-8')
    process_mock.stderr = stderr_str.encode('utf-8')
    process_mock.returncode = returncode
    def check_returncode_mock():
        if process_mock.returncode != 0:
            raise subprocess.CalledProcessError(
                process_mock.returncode, "cmd",
                output=process_mock.stdout, stderr=process_mock.stderr
            )
    process_mock.check_returncode = MagicMock(side_effect=check_returncode_mock)
    return process_mock


@pytest.mark.asyncio
async def test_process_logs_data_success(mocker):
    """Test the successful workflow of process_logs_data, mocking dependencies."""
    # Arrange
    test_input_data = "log line 1\nlog line 2"
    mock_vector_output_jsonl = """
    {"level": "info", "message": "Log 1", "timestamp": "t1"}
    {"level": "error", "message": "Log 2", "timestamp": "t2"}
    """
    mock_analysis_result = { "level_counts": {"info": 1, "error": 1}, "error_messages": ["Log 2"], "anomalies": [], "metrics": {}, "summary": "" }
    mock_summary_result = "Mocked LLM Summary of Logs"

    mock_proc = create_mock_process(stdout_str=mock_vector_output_jsonl, returncode=0)
    mock_to_thread = AsyncMock(return_value=mock_proc)
    mocker.patch('asyncio.to_thread', new=mock_to_thread)

    mock_analyze = mocker.patch('app.log_metrics_analysis.analyze_logs', return_value=mock_analysis_result)
    # Mock process_data_summary - use chain object mocking style just in case direct isn't reliable
    mock_summarize_chain = mocker.patch('app.log_metrics_analysis.log_summary_chain', autospec=True)
    mock_summarize_chain.ainvoke = AsyncMock(return_value=mock_summary_result)
    # Also patch the function itself to simplify checking call args later if needed, though not strictly necessary if chain mock works
    # mock_summarize_func = mocker.patch('app.log_metrics_analysis.process_data_summary', new_callable=AsyncMock, return_value=mock_summary_result)


    # Act - pass optional history as None for this case
    result_insights = await process_logs_data(test_input_data, history=None)

    # Assert
    mock_to_thread.assert_awaited_once()
    # ... check call_args for to_thread ...

    expected_parsed_logs = [{"level": "info", "message": "Log 1", "timestamp": "t1"}, {"level": "error", "message": "Log 2", "timestamp": "t2"}]
    mock_analyze.assert_called_once_with(expected_parsed_logs)

    # Check process_data_summary was called correctly via its chain mock
    mock_summarize_chain.ainvoke.assert_awaited_once()
    call_args, call_kwargs = mock_summarize_chain.ainvoke.call_args
    # Check the dictionary passed to the chain's ainvoke
    assert isinstance(call_args[0].get("log_analysis_data"), str) # Check key exists
    assert call_args[0].get("history") == [] # Check history part

    assert isinstance(result_insights, LogInsights)
    assert result_insights.level_counts == mock_analysis_result["level_counts"]
    assert result_insights.summary == mock_summary_result


@pytest.mark.asyncio
async def test_process_logs_data_vector_calledprocesserror(mocker):
    """Test handling when the vector subprocess returns a non-zero exit code."""
    test_input_data = "bad log data"
    mock_stderr = "Vector config error!"
    simulated_exception = subprocess.CalledProcessError(1, "vector", stderr=mock_stderr.encode('utf-8'))
    mock_to_thread = AsyncMock(side_effect=simulated_exception)
    mocker.patch('asyncio.to_thread', new=mock_to_thread)
    mock_analyze = mocker.patch('app.log_metrics_analysis.analyze_logs')
    mock_summarize = mocker.patch('app.log_metrics_analysis.process_data_summary') # Patch downstream even if not called

    with pytest.raises(ValueError) as excinfo:
        await process_logs_data(test_input_data)
    assert f"Log processing via Vector failed: {mock_stderr}" in str(excinfo.value)
    mock_analyze.assert_not_called()
    mock_summarize.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_logs_data_vector_timeout(mocker):
    """Test handling when the vector subprocess times out."""
    test_input_data = "very large log data"
    mock_timeout_value = 30
    mocker.patch.object(settings, 'VECTOR_TIMEOUT', mock_timeout_value)
    simulated_exception = subprocess.TimeoutExpired(cmd='vector', timeout=mock_timeout_value)
    mock_to_thread = AsyncMock(side_effect=simulated_exception)
    mocker.patch('asyncio.to_thread', new=mock_to_thread)
    mock_analyze = mocker.patch('app.log_metrics_analysis.analyze_logs')
    mock_summarize = mocker.patch('app.log_metrics_analysis.process_data_summary')

    with pytest.raises(ValueError) as excinfo:
        await process_logs_data(test_input_data)
    expected_msg_part = f"Log processing via Vector timed out ({mock_timeout_value}s)."
    assert expected_msg_part in str(excinfo.value)
    mock_analyze.assert_not_called()
    mock_summarize.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_logs_data_vector_filenotfound(mocker):
    """Test handling when the vector command is not found."""
    test_input_data = "some log data"
    simulated_exception = FileNotFoundError("[Errno 2] No such file or directory: 'vector'")
    mock_to_thread = AsyncMock(side_effect=simulated_exception)
    mocker.patch('asyncio.to_thread', new=mock_to_thread)
    mock_analyze = mocker.patch('app.log_metrics_analysis.analyze_logs')
    mock_summarize = mocker.patch('app.log_metrics_analysis.process_data_summary')

    with pytest.raises(RuntimeError, match="Required tool 'vector' not found"):
        await process_logs_data(test_input_data)
    mock_analyze.assert_not_called()
    mock_summarize.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_logs_data_vector_json_parse_error(mocker):
    """Test handling of invalid JSON lines in Vector's output."""
    test_input_data = "mixed data"
    mock_vector_output_jsonl = """
    {"level": "info", "message": "Log 1", "timestamp": "t1"}
    this is not json
    {"level": "warn", "message": "Log 3", "timestamp": "t3"}
    """
    mock_analysis_result = { "level_counts": {"info": 1, "warn": 1}, "error_messages": [], "anomalies": [], "metrics": {}, "summary": ""}
    mock_summary_result = "Mocked Summary (Parsed 2 logs)"

    mock_proc = create_mock_process(stdout_str=mock_vector_output_jsonl, returncode=0)
    mock_to_thread = AsyncMock(return_value=mock_proc)
    mocker.patch('asyncio.to_thread', new=mock_to_thread)
    mock_analyze = mocker.patch('app.log_metrics_analysis.analyze_logs', return_value=mock_analysis_result)
    # Mock chain used by process_data_summary
    mock_summarize_chain = mocker.patch('app.log_metrics_analysis.log_summary_chain', autospec=True)
    mock_summarize_chain.ainvoke = AsyncMock(return_value=mock_summary_result)

    result_insights = await process_logs_data(test_input_data)

    expected_parsed_logs = [{"level": "info", "message": "Log 1", "timestamp": "t1"},{"level": "warn", "message": "Log 3", "timestamp": "t3"}]
    mock_analyze.assert_called_once_with(expected_parsed_logs)
    # Check that the summary chain was called
    mock_summarize_chain.ainvoke.assert_awaited_once()
    assert result_insights.summary == mock_summary_result


@pytest.mark.asyncio
async def test_process_logs_data_vector_empty_output(mocker):
    """Test handling when Vector runs successfully but produces no parsable output."""
    test_input_data = "some data"
    mock_vector_output_jsonl = "\n \n"
    mock_analyze = mocker.patch('app.log_metrics_analysis.analyze_logs')
    mock_summarize = mocker.patch('app.log_metrics_analysis.process_data_summary') # Patch downstream

    mock_proc = create_mock_process(stdout_str=mock_vector_output_jsonl, returncode=0)
    mock_to_thread = AsyncMock(return_value=mock_proc)
    mocker.patch('asyncio.to_thread', new=mock_to_thread)

    result_insights = await process_logs_data(test_input_data)

    mock_analyze.assert_not_called()
    mock_summarize.assert_not_awaited() # Use not_awaited for async function mocks
    assert isinstance(result_insights, LogInsights)
    assert result_insights.summary == "Log processing yielded no structured entries."