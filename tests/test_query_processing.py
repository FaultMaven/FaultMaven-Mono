# tests/test_query_processing.py
"""
API tests for the FastAPI application endpoints defined in app.query_processing.
Uses FastAPI's TestClient and mocks underlying service functions.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock # For mocking async functions later

# Import the FastAPI app instance FROM app.query_processing
from app.query_processing import app
# Import Pydantic models needed FROM app.models
from app.models import (
    DataInsightsResponse, # Use this for /data responses
    TroubleshootingResponse,
    FeedbackRequest,
    DataType,
    LogInsights # Import if needed for creating mock results
    # QueryRequest will be tested implicitly via /query tests
)

# --- Test Client Fixture ---
@pytest.fixture(scope="module")
def client():
    """Provides a FastAPI TestClient instance."""
    # Using context manager handles startup/shutdown events if defined in app
    with TestClient(app) as test_client:
        yield test_client

# === Basic Endpoint Tests ===

def test_read_root(client: TestClient):
    """Test the root GET endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    # --- CORRECTED ASSERTION ---
    # Verify the message matches the one actually returned by app/query_processing.py
    assert response.json() == {"message": "FaultMaven API is running."}

def test_handle_feedback_placeholder(client: TestClient):
    """Test the placeholder /feedback endpoint returns the correct static response."""
    # Prepare valid request data using the Pydantic model
    feedback_data = FeedbackRequest(
        query="Why did it crash last night?",
        feedback="The analysis of the logs was spot on, thanks!"
    ).model_dump() # Use model_dump() for Pydantic V2+

    # Make the POST request
    response = client.post("/feedback", json=feedback_data)

    # Assert the expected placeholder response
    assert response.status_code == 200
    assert response.json() == {"status": "Feedback endpoint not currently active."}

# === Tests for POST /data ===

# TODO: Add tests for POST /data endpoint
# Example test structure for successful text upload:
# @pytest.mark.asyncio
# async def test_handle_data_success_text(client: TestClient, mocker):
#     mock_session = "session-data-text"
#     # Mock the return value of the classifier
#     mock_classify_result = DataClassification(data_type=DataType.TEXT, confidence=0.9, key_features=["Keywords"], suggested_tool="...")
#     # Mock the return value of the text processor
#     mock_text_result = {"summary": "Mock text summary"}
#     # Mock the function that adds data to session (doesn't need return value)
#     mock_add_data = mocker.patch("app.query_processing.add_data_to_session")
#
#     # Patch the functions called by the endpoint handler
#     mocker.patch("app.query_processing.get_or_create_session", return_value=mock_session)
#     mocker.patch("app.query_processing.classify_data", new_callable=AsyncMock, return_value=mock_classify_result)
#     mocker.patch("app.query_processing.process_text_data", new_callable=AsyncMock, return_value=mock_text_result)
#     # Mock other processors if they could be called (or ensure they aren't)
#     mocker.patch("app.query_processing.process_logs_data", new_callable=AsyncMock) # Example
#
#     # Simulate sending form data
#     response = client.post("/data", data={"text": "This is test text"})
#
#     # Assertions
#     assert response.status_code == 200
#     resp_json = response.json()
#     assert resp_json["session_id"] == mock_session
#     assert resp_json["classified_type"] == DataType.TEXT.value
#     assert "Insights provided" in resp_json["message"] # Or similar based on endpoint logic
#     assert resp_json["insights"] == mock_text_result
#     # Check add_data_to_session was called once
#     mock_add_data.assert_called_once()
#     # Optionally: inspect the UploadedData object passed to add_data_to_session
#     # args, _ = mock_add_data.call_args ... assert args[1].processed_results == mock_text_result ...


# === Tests for POST /query ===

# TODO: Add tests for POST /query endpoint
# Example test structure:
# @pytest.mark.asyncio
# async def test_handle_query_success(client: TestClient, mocker):
#     mock_session = "session-query-1"
#     # Mock memory object if needed, or just its methods if called directly
#     mock_memory = MagicMock(spec=ConversationBufferMemory)
#     # Mock the data retrieved for the session
#     mock_data_list = [UploadedData( # Use actual model
#          classified_type=DataType.SYSTEM_LOGS,
#          processing_status="Processed",
#          processed_results=LogInsights(summary="Mock log summary for query")
#     )]
#     # Mock the expected response from the core AI logic
#     mock_ai_response = TroubleshootingResponse(answer="AI answer based on log summary", action_items=None)
#
#     # Patch the functions called by the endpoint handler
#     mocker.patch("app.query_processing.get_or_create_session", return_value=mock_session)
#     mocker.patch("app.query_processing.get_memory_for_session", return_value=mock_memory)
#     mocker.patch("app.query_processing.get_data_for_session", return_value=mock_data_list)
#     mock_process_query = mocker.patch("app.query_processing.process_user_query", new_callable=AsyncMock, return_value=mock_ai_response)
#
#     # Make the request
#     response = client.post("/query", json={"query": "Analyze the logs"}, headers={"X-Session-ID": mock_session})
#
#     # Assertions
#     assert response.status_code == 200
#     # Check response body against the Pydantic model's dictionary representation
#     assert response.json() == mock_ai_response.model_dump()
#     assert response.headers.get("X-Session-ID") == mock_session
#     # Check process_user_query was called correctly
#     mock_process_query.assert_awaited_once_with(
#         session_id=mock_session,
#         query="Analyze the logs",
#         memory=mock_memory,
#         data_list=mock_data_list
#     )