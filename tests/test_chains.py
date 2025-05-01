# tests/test_chains.py
"""
Unit tests for the app.chains module, primarily focusing on the
format_uploaded_data helper function.
"""

# --- Imports ---
import pytest
import time
import json
from typing import List, Dict, Any, Optional, Union
from app.chains import format_uploaded_data, process_user_query
# Import necessary models - Use the CURRENT ones
from app.models import UploadedData, DataType, LogInsights, TroubleshootingResponse
from unittest.mock import AsyncMock
from langchain.memory import ConversationBufferMemory
# RunnableConfig may need specific import if directly asserted on type
# from langchain_core.runnables import RunnableConfig

# --- Timestamps and Constants ---
TS_NOW = time.time()
TS1 = TS_NOW - 3600
TS2 = TS_NOW - 600
TS3 = TS_NOW - 60
TS4 = TS_NOW
DEFAULT_LOGINSIGHTS_FORMATTED = "Log data processed, but no specific programmatic insights extracted."


# --- Tests for format_uploaded_data ---

def test_format_uploaded_data_empty_list():
    """Verify output when the data list is empty."""
    result = format_uploaded_data([])
    assert result == "No data has been uploaded for this session yet."

def test_format_uploaded_data_single_processed_loginsights():
    """Verify formatting for a single item with processed LogInsights."""
    # --- CORRECTED LogInsights Instantiation ---
    insights = LogInsights(
        level_counts={"error": 5, "info": 50},
        anomalies=["High response time detected"],
        metrics={"response_time_ms": 123.45},
        summary="Log processing found 5 errors."
    )
    # --- END CORRECTION ---
    data = [
        UploadedData(
            original_type='file', content_snippet="log line 1...",
            classified_type=DataType.SYSTEM_LOGS, timestamp=TS1,
            filename="server.log", processed_results=insights,
            processing_status="Processed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    assert "--- Data Block 1" in result
    assert "(log" in result # Value of SYSTEM_LOGS is 'log'
    assert "(Filename: server.log)" in result
    assert " at " in result
    assert "Status: Processed) ---" in result
    assert "- Log Levels Found: error: 5, info: 50" in result
    assert "- Derived Metrics: response_time_ms: 123.45" in result
    assert "- Detected Anomalies/Patterns:" in result
    assert "  - High response time detected" in result
    assert "- Processing Summary: Log processing found 5 errors." in result
    assert "Content Snippet:" not in result


def test_format_uploaded_data_single_processed_dict_summary():
    """Verify formatting for a dict summary (e.g., from text processing)."""
    data = [
        UploadedData(
            original_type='text',
            # MODIFIED: Use GENERIC_TEXT instead of TEXT
            classified_type=DataType.GENERIC_TEXT,
            timestamp=TS1,
            processed_results={"summary": "This is a text analysis summary."},
            processing_status="Processed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    # Assertion unchanged because DataType.GENERIC_TEXT.value is "text"
    assert "--- Data Block 1 (text" in result
    assert "Status: Processed) ---" in result
    assert "- Processing Summary: This is a text analysis summary." in result
    assert "Content Snippet:" not in result


# Renamed test slightly for clarity
def test_format_uploaded_data_single_processed_generic_dict():
    """Verify formatting for a generic dict result (using CONFIG as example)."""
    generic_result = {"status": "Active", "param_value": 500}
    data = [
        UploadedData(
            original_type='text',
            # MODIFIED: Use CONFIGURATION_DATA instead of MCP
            classified_type=DataType.CONFIGURATION_DATA,
            timestamp=TS1,
            processed_results=generic_result,
            processing_status="Processed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    # MODIFIED: Check for 'config' which is the value of CONFIGURATION_DATA
    assert "--- Data Block 1 (config" in result
    assert "Status: Processed) ---" in result
    # Assertions for JSON dump formatting remain the same
    assert "Processed Data:" in result
    assert '"status": "Active"' in result
    assert '"param_value": 500' in result


def test_format_uploaded_data_single_processed_string():
    """Verify formatting for a simple string result."""
    data = [
        UploadedData(
            original_type='text', classified_type=DataType.CONFIGURATION_DATA,
            timestamp=TS1, processed_results="Config validation passed.",
            processing_status="Processed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    # Value of CONFIGURATION_DATA is 'config'
    assert "--- Data Block 1 (config" in result
    assert "Status: Processed) ---" in result
    assert "Config validation passed." in result
    assert "Content Snippet:" not in result


def test_format_uploaded_data_single_failed_with_error_message():
    """Verify formatting when processing failed and an error message is stored."""
    error_result = {"error": "Vector process timed out."}
    data = [
        UploadedData(
            original_type='file', content_snippet="ERROR: timeout occurred...",
            classified_type=DataType.SYSTEM_LOGS, timestamp=TS1, # Stays SYSTEM_LOGS
            filename="timeout.log", processed_results=error_result,
            processing_status="Failed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    assert "--- Data Block 1" in result
    assert "(log" in result # Value of SYSTEM_LOGS is 'log'
    assert "(Filename: timeout.log)" in result
    assert " at " in result
    assert "Status: Failed) ---" in result
    assert "Content Snippet:\nERROR: timeout occurred..." in result
    assert "(Processing failed for this data: Vector process timed out.)" in result


def test_format_uploaded_data_single_failed_no_error_message():
    """Verify formatting when processing failed without a specific stored error message."""
    data = [
        UploadedData(
            original_type='file', content_snippet="Some log data...",
            classified_type=DataType.SYSTEM_LOGS, timestamp=TS1, # Stays SYSTEM_LOGS
            filename="fail.log", processed_results=None, # No error dict stored
            processing_status="Failed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    assert "--- Data Block 1" in result
    assert "(log" in result # Value of SYSTEM_LOGS is 'log'
    assert "(Filename: fail.log)" in result
    assert " at " in result
    assert "Status: Failed) ---" in result
    assert "Content Snippet:\nSome log data..." in result
    assert "(Processing failed for this data)" in result
    # Ensure the colon+space isn't present if no specific error message was added
    assert ": " not in result.split("(Processing failed for this data")[-1]


def test_format_uploaded_data_single_no_results_with_snippet():
    """Verify formatting shows snippet when processed but no results returned."""
    data = [
        UploadedData(
            original_type='text', content_snippet="Just some plain text.",
            # MODIFIED: Use GENERIC_TEXT instead of TEXT
            classified_type=DataType.GENERIC_TEXT,
            timestamp=TS1,
            processed_results=None,
            processing_status="Processed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    # Assertion unchanged because DataType.GENERIC_TEXT.value is "text"
    assert "--- Data Block 1 (text" in result
    assert "Status: Processed) ---" in result
    assert "Content Snippet:\nJust some plain text." in result
    assert "Processing Error:" not in result
    assert "Processing Summary:" not in result
    assert "Analysis Summary:" not in result # Assuming summary key is consistent


def test_format_uploaded_data_single_no_results_no_snippet():
    """Verify formatting shows placeholder when no results and no snippet."""
    data = [
        UploadedData(
            original_type='file', content_snippet=None,
            classified_type=DataType.UNKNOWN, timestamp=TS1, # Stays UNKNOWN
            filename="empty.dat", processed_results=None,
            processing_status="Processed"
        )
    ]
    result = format_uploaded_data(data)

    assert "Showing context from 1 data block(s) uploaded:" in result
    assert "--- Data Block 1" in result
    assert "(unknown" in result # Value of UNKNOWN is 'unknown'
    assert "(Filename: empty.dat)" in result
    assert " at " in result
    assert "Status: Processed) ---" in result
    assert "(No content snippet or processed results available for this block - Status: Processed)" in result


def test_format_uploaded_data_multiple_items_limit():
    """Verify that only the last 'max_data_blocks_in_prompt' items are formatted and content matches."""
    max_blocks = 3 # Should match constant in chains.py
    data = [
        # Block 1 (Oldest - Excluded)
        UploadedData(original_type='text',
                     # MODIFIED: Use GENERIC_TEXT
                     classified_type=DataType.GENERIC_TEXT,
                     timestamp=TS1, processing_status="Processed", content_snippet="Block 1 (Oldest)"),
        # Block 2 (Included)
        UploadedData(original_type='file', classified_type=DataType.SYSTEM_LOGS, timestamp=TS2, processing_status="Failed", content_snippet="Block 2 (Failed Snippet)", filename="failed.log"), # Stays SYSTEM_LOGS
        # Block 3 (Included)
        UploadedData(original_type='text',
                     # MODIFIED: Use GENERIC_TEXT
                     classified_type=DataType.GENERIC_TEXT,
                     timestamp=TS3, processing_status="Processed", processed_results={"summary":"Block 3 Summary"}),
        # Block 4 (Included)
        UploadedData(original_type='text',
                     # MODIFIED: Use CONFIGURATION_DATA instead of MCP
                     classified_type=DataType.CONFIGURATION_DATA,
                     timestamp=TS4, processing_status="Processed", processed_results={"status":"Active"}) # Changed MCP result slightly
    ]
    result = format_uploaded_data(data)

    # Check header indicates truncation/limit
    assert f"Showing context from the {max_blocks} most recent data blocks (out of 4 total):" in result

    # Check that Block 1 is NOT present
    assert "Block 1 (Oldest)" not in result

    # --- Check content for Block 2 (Failed) ---
    assert "--- Data Block 2 (log" in result # Stays 'log'
    assert "(Filename: failed.log)" in result
    assert "Status: Failed) ---" in result
    assert "Content Snippet:\nBlock 2 (Failed Snippet)" in result
    assert "(Processing failed for this data)" in result # Generic failure message

    # --- Check content for Block 3 (Dict Summary) ---
    # Assertion unchanged because DataType.GENERIC_TEXT.value is "text"
    assert "--- Data Block 3 (text" in result
    assert "Status: Processed) ---" in result
    assert "- Processing Summary: Block 3 Summary" in result # Correct label check

    # --- Check content for Block 4 (Config Dict) ---
    # MODIFIED: Check for 'config' which is the value of CONFIGURATION_DATA
    assert "--- Data Block 4 (config" in result
    assert "Status: Processed) ---" in result
    # Check for the JSON dump output for generic dicts
    assert "Processed Data:" in result # Check label
    assert '"status": "Active"' in result # Check content


# --- Tests for process_user_query ---

@pytest.mark.asyncio
async def test_process_user_query_success(mocker):
    """
    Verify process_user_query successfully invokes the chain with correct inputs
    and returns the chain's result, using chain-level mocking.
    """
    # Arrange
    test_session_id = "session-123"
    test_query = "What is the status?"
    # --- CORRECTED ConversationBufferMemory Instantiation ---
    test_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # --- END CORRECTION ---
    test_data_list = [
        UploadedData(
            original_type='file',
            classified_type=DataType.SYSTEM_LOGS,
            timestamp=TS1,
            filename="test.log", # Provide optional filename
            processing_status="Processed",
            # Provide results consistent with expected LLM context
            processed_results=LogInsights(summary="Log summary")
        )
    ]
    expected_response = TroubleshootingResponse(
        answer="Everything seems okay based on log summary.",
        action_items=["Monitor service X"]
    )

    # Mock the chain object and configure its ainvoke method
    mock_chain_object = mocker.patch('app.chains.chain', autospec=True)
    mock_chain_object.ainvoke = AsyncMock(return_value=expected_response)

    # Act
    actual_response = await process_user_query(
        session_id=test_session_id,
        query=test_query,
        memory=test_memory,
        data_list=test_data_list
    )

    # Assert
    # 1. Check the result matches
    assert actual_response == expected_response

    # 2. Verify ainvoke was awaited
    mock_chain_object.ainvoke.assert_awaited_once()

    # 3. Verify positional and keyword arguments passed to ainvoke
    call_args, call_kwargs = mock_chain_object.ainvoke.call_args

    # Check positional arguments
    assert len(call_args) == 1
    expected_input_dict = {
        "query": test_query,
        "uploaded_data_list": test_data_list,
        "memory": test_memory,
    }
    assert call_args[0] == expected_input_dict

    # Check keyword arguments
    assert len(call_kwargs) == 1
    assert "config" in call_kwargs
    config_arg = call_kwargs['config']
    # Verify it behaves like a dictionary and contains the expected keys/values
    assert isinstance(config_arg, dict) # Check it's dictionary-like
    assert config_arg.get('configurable', {}).get('session_id') == test_session_id


@pytest.mark.asyncio
async def test_process_user_query_chain_exception(mocker):
    """
    Verify process_user_query correctly re-raises exceptions from chain.ainvoke,
    using chain-level mocking.
    """
    # Arrange
    test_session_id = "session-err"
    test_query = "This will fail"
    # --- CORRECTED ConversationBufferMemory Instantiation ---
    test_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # --- END CORRECTION ---
    test_data_list = []
    test_exception = ValueError("Simulated LLM/Chain Error")

    # --- Mock the ENTIRE chain object ---
    mock_chain_object = mocker.patch('app.chains.chain', autospec=True)
    # --- Configure ainvoke ON THE MOCK CHAIN to raise an error ---
    mock_chain_object.ainvoke = AsyncMock(side_effect=test_exception)

    # Act & Assert: Use pytest.raises to check if the expected exception is raised
    with pytest.raises(ValueError, match="Simulated LLM/Chain Error"):
        await process_user_query(
            session_id=test_session_id,
            query=test_query,
            memory=test_memory,
            data_list=test_data_list
        )

    # Also assert that the mock chain's ainvoke was actually called
    mock_chain_object.ainvoke.assert_awaited_once()