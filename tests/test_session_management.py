# tests/test_session_management.py
"""
Unit tests for the app.session_management module.
"""

import pytest
import time
import uuid
from unittest.mock import MagicMock # Can use this or mocker fixture

# Module to be tested
from app import session_management
# Import necessary components used by the module or for testing
from app.models import UploadedData, DataType, LogInsights # Import necessary models
from langchain.memory import ConversationBufferMemory
from config.settings import settings # Import the 'settings' instance from the 'config.settings' module
import logging

# --- Test Fixtures ---

@pytest.fixture(autouse=True)
def clear_stores_before_each_test(mocker):
    """
    Pytest fixture to automatically clear the in-memory stores before each
    test function runs and mock time.time consistently for most tests.
    """
    # Clear the actual dictionaries used by the module
    session_management.session_memory_store.clear()
    session_management.session_data_store.clear()
    session_management.session_last_activity.clear()
    # Optional: Mock time.time by default if most tests need it,
    # otherwise mock it specifically in tests that require time control.
    # mocker.patch('time.time', return_value=time.time()) # Mock to a fixed start time?
    yield # The test runs here
    # Cleanup after test (optional, as next test will clear)
    session_management.session_memory_store.clear()
    session_management.session_data_store.clear()
    session_management.session_last_activity.clear()

# --- Helper to Create Mock UploadedData ---
def create_mock_uploaded_data(content="test content", type=DataType.TEXT):
    # Make sure LogInsights is defined or imported if needed by Union
    # For simplicity, we might just store Dict or str in tests
    mock_results = {"summary": "Processed summary"}
    return UploadedData(
        original_type='text',
        content_snippet=content[:20],
        classified_type=type,
        filename=None,
        processed_results=mock_results,
        processing_status="Processed"
        # timestamp uses default_factory
    )

# --- Tests for get_or_create_session ---

def test_get_or_create_session_new_session():
    """
    Verify creating a brand new session when session_id is None.
    """
    session_id = session_management.get_or_create_session(None)

    assert isinstance(session_id, str) and len(session_id) == 36
    assert session_id in session_management.session_memory_store
    assert isinstance(session_management.session_memory_store[session_id], ConversationBufferMemory)
    assert session_id in session_management.session_data_store
    assert session_management.session_data_store[session_id] == []
    assert session_id in session_management.session_last_activity
    assert isinstance(session_management.session_last_activity[session_id], float)
    assert session_management.session_last_activity[session_id] == pytest.approx(time.time(), abs=1)

def test_get_or_create_session_existing_valid(mocker):
    """
    Verify retrieving an existing, valid (non-expired) session updates
    its last activity time and returns the same ID.
    """
    # Arrange: Create an initial session at a specific time
    initial_time = time.time()
    mocker.patch('time.time', return_value=initial_time)
    initial_session_id = session_management.get_or_create_session(None)
    # Verify initial activity time
    assert session_management.session_last_activity[initial_session_id] == initial_time

    # Act: Call again shortly after (time elapsed is less than timeout)
    # Use a clear, valid variable name
    time_within_timeout = initial_time + settings.SESSION_TIMEOUT / 2
    mocker.patch('time.time', return_value=time_within_timeout) # Mock time to the later point
    retrieved_session_id = session_management.get_or_create_session(initial_session_id)

    # Assert: Should get the same ID back, and activity time updated
    assert retrieved_session_id == initial_session_id
    # Check that the last activity timestamp was updated to the mocked time
    assert session_management.session_last_activity[initial_session_id] == time_within_timeout
    # Act: Call again shortly after (time elapsed is less than timeout)
    # Use a clear, valid variable name

def test_get_or_create_session_existing_expired(mocker):
    """
    Verify that retrieving an expired session results in cleaning up
    the old session and creating/returning a new one.
    """
    # Arrange: Create an initial session
    initial_time = 1700000000.0 # Use a fixed time for predictability
    mocker.patch('time.time', return_value=initial_time)
    initial_session_id = session_management.get_or_create_session(None)
    assert initial_session_id in session_management.session_memory_store

    # Act: Call again after the timeout has passed
    time_after_expiry = initial_time + settings.SESSION_TIMEOUT + 60 # 60 seconds past timeout
    mocker.patch('time.time', return_value=time_after_expiry)
    new_session_id = session_management.get_or_create_session(initial_session_id)

    # Assert: Should get a NEW ID, old one should be gone, new one exists
    assert isinstance(new_session_id, str) and len(new_session_id) == 36
    assert new_session_id != initial_session_id

    assert initial_session_id not in session_management.session_memory_store
    assert initial_session_id not in session_management.session_data_store
    assert initial_session_id not in session_management.session_last_activity

    assert new_session_id in session_management.session_memory_store
    assert new_session_id in session_management.session_data_store
    assert new_session_id in session_management.session_last_activity
    assert session_management.session_last_activity[new_session_id] == time_after_expiry

def test_get_or_create_session_invalid_id():
    """
    Verify that passing an invalid (non-existent) session ID results
    in creating and returning a new session ID.
    """
    invalid_id = str(uuid.uuid4()) # Generate a random UUID that isn't in stores
    new_session_id = session_management.get_or_create_session(invalid_id)

    assert isinstance(new_session_id, str) and len(new_session_id) == 36
    assert new_session_id != invalid_id
    assert new_session_id in session_management.session_memory_store # New session created

# --- Tests for get_memory_for_session ---

def test_get_memory_for_session_valid():
    """Verify retrieving memory for a valid session ID."""
    session_id = session_management.get_or_create_session(None)
    memory = session_management.get_memory_for_session(session_id)
    assert memory is not None
    assert isinstance(memory, ConversationBufferMemory)
    # Check if it's the same object stored (optional sanity check)
    assert memory is session_management.session_memory_store[session_id]

def test_get_memory_for_session_invalid():
    """Verify retrieving memory for an invalid session ID returns None."""
    invalid_id = str(uuid.uuid4())
    memory = session_management.get_memory_for_session(invalid_id)
    assert memory is None

# --- Tests for get_data_for_session ---

def test_get_data_for_session_empty():
    """Verify retrieving data for a new session returns an empty list."""
    session_id = session_management.get_or_create_session(None)
    data_list = session_management.get_data_for_session(session_id)
    assert data_list == []

def test_get_data_for_session_with_data():
    """Verify retrieving data after adding returns the correct list."""
    session_id = session_management.get_or_create_session(None)
    mock_data1 = create_mock_uploaded_data("data 1")
    mock_data2 = create_mock_uploaded_data("data 2", type=DataType.SYSTEM_LOGS)

    session_management.add_data_to_session(session_id, mock_data1)
    session_management.add_data_to_session(session_id, mock_data2)

    data_list = session_management.get_data_for_session(session_id)
    assert len(data_list) == 2
    assert data_list[0] == mock_data1
    assert data_list[1] == mock_data2

def test_get_data_for_session_invalid():
    """Verify retrieving data for an invalid session ID returns an empty list."""
    invalid_id = str(uuid.uuid4())
    data_list = session_management.get_data_for_session(invalid_id)
    assert data_list == []

# --- Tests for add_data_to_session ---

def test_add_data_to_session_success(mocker):
    """Verify successfully adding data updates the store and activity time."""
    start_time = time.time()
    mocker.patch('time.time', return_value=start_time)
    session_id = session_management.get_or_create_session(None)
    assert session_management.session_last_activity[session_id] == start_time

    # Add data slightly later
    add_time = start_time + 10
    mocker.patch('time.time', return_value=add_time)
    mock_data = create_mock_uploaded_data("new data")
    session_management.add_data_to_session(session_id, mock_data)

    # Assertions
    assert session_id in session_management.session_data_store
    assert len(session_management.session_data_store[session_id]) == 1
    assert session_management.session_data_store[session_id][0] == mock_data
    # Check last activity time was updated
    assert session_management.session_last_activity[session_id] == add_time

def test_add_data_to_session_invalid_session(caplog):
    """
    Verify attempting to add data to an invalid session logs the correct
    error message and doesn't modify stores.
    """
    invalid_id = str(uuid.uuid4())
    mock_data = create_mock_uploaded_data("some data")

    # Use caplog fixture provided by pytest to capture log messages
    # Ensure the level captured is appropriate (ERROR in this case)
    with caplog.at_level(logging.ERROR):
        session_management.add_data_to_session(invalid_id, mock_data)

    # Assertions
    # 1. Check stores were not modified unexpectedly
    assert invalid_id not in session_management.session_data_store
    assert not session_management.session_data_store # Store should be empty

    # 2. Check the CORE error message was logged
    #    Match the actual message logged by logger.error in the function
    expected_log_message_core = f"Attempted to add data to non-existent session: {invalid_id}. Data NOT stored."
    # Check if this core message exists within the full captured log text
    assert expected_log_message_core in caplog.text


# --- Test for _cleanup_expired_sessions ---

def test_cleanup_expired_sessions(mocker):
    """Verify the cleanup function removes expired sessions but leaves active ones."""
    # Arrange: Create two sessions at different times
    time1 = 1700000000.0
    mocker.patch('time.time', return_value=time1)
    session_id_expired = session_management.get_or_create_session(None)

    time2 = time1 + settings.SESSION_TIMEOUT / 2 # Create second session before first expires
    mocker.patch('time.time', return_value=time2)
    session_id_active = session_management.get_or_create_session(None)

    # Ensure both exist initially
    assert session_id_expired in session_management.session_last_activity
    assert session_id_active in session_management.session_last_activity

    # Act: Advance time so only the first session is expired
    time3 = time1 + settings.SESSION_TIMEOUT + 60 # session_id_expired is now expired
    mocker.patch('time.time', return_value=time3)
    session_management._cleanup_expired_sessions() # Call the cleanup function directly

    # Assert: Expired session is gone, active session remains
    assert session_id_expired not in session_management.session_memory_store
    assert session_id_expired not in session_management.session_data_store
    assert session_id_expired not in session_management.session_last_activity

    assert session_id_active in session_management.session_memory_store
    assert session_id_active in session_management.session_data_store
    assert session_id_active in session_management.session_last_activity
    # Active session's last activity time shouldn't change during cleanup
    assert session_management.session_last_activity[session_id_active] == time2