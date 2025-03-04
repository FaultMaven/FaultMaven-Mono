import pytest
from fastapi.testclient import TestClient
from app.query_processing import app, QueryRequest, FeedbackRequest, process_logs
from unittest.mock import patch, MagicMock

# Initialize FastAPI TestClient
client = TestClient(app)

### **Test Data**
SAMPLE_LOGS = "2023-10-01 ERROR: Disk full"
SAMPLE_QUERY = "Why is the disk full?"
SAMPLE_FEEDBACK = {"query": SAMPLE_QUERY, "feedback": "The response was helpful."}

### **Mocked Dependencies**
@pytest.fixture
def mock_dependencies():
    with patch("app.query_processing.normalize_data") as mock_normalize_data, \
         patch("app.query_processing.analyze_logs_metrics") as mock_analyze_logs, \
         patch("app.query_processing.process_query") as mock_process_query, \
         patch("app.query_processing.process_query_with_logs") as mock_process_query_with_logs, \
         patch("app.query_processing.update_session_learning") as mock_update_learning:
        yield {
            "normalize_data": mock_normalize_data,
            "analyze_logs": mock_analyze_logs,
            "process_query": mock_process_query,
            "process_query_with_logs": mock_process_query_with_logs,
            "update_learning": mock_update_learning,
        }

### **Test Cases**
def test_process_logs():
    """Test the `process_logs` helper function."""
    with patch("app.query_processing.normalize_data", return_value="normalized_logs"), \
         patch("app.query_processing.analyze_logs_metrics", return_value={"insight": "disk_full"}):
        result = process_logs(SAMPLE_LOGS)
        assert result == {"insight": "disk_full"}

def test_handle_query_no_input():
    """Test the `/query` endpoint with no input."""
    response = client.post("/query", json={})
    assert response.status_code == 200
    assert response.json() == {"response": "How may I help you?"}

def test_handle_query_logs_only(mock_dependencies):
    """Test the `/query` endpoint with logs only."""
    mock_dependencies["normalize_data"].return_value = "normalized_logs"
    mock_dependencies["analyze_logs"].return_value = {"insight": "disk_full"}

    response = client.post("/query", json={"logs": SAMPLE_LOGS})
    assert response.status_code == 200
    assert response.json() == {"response": {"insight": "disk_full"}}

def test_handle_query_query_only(mock_dependencies):
    """Test the `/query` endpoint with query only."""
    mock_dependencies["process_query"].return_value = {"response": "Disk is full."}

    response = client.post("/query", json={"query": SAMPLE_QUERY})
    assert response.status_code == 200
    assert response.json() == {"response": {"response": "Disk is full."}}

def test_handle_query_combined(mock_dependencies):
    """Test the `/query` endpoint with both query and logs."""
    mock_dependencies["normalize_data"].return_value = "normalized_logs"
    mock_dependencies["analyze_logs"].return_value = {"insight": "disk_full"}
    mock_dependencies["process_query_with_logs"].return_value = {"response": "Disk is full due to logs."}

    response = client.post("/query", json={"query": SAMPLE_QUERY, "logs": SAMPLE_LOGS})
    assert response.status_code == 200
    assert response.json() == {"response": {"response": "Disk is full due to logs."}}

def test_handle_query_invalid_logs(mock_dependencies):
    """Test the `/query` endpoint with invalid logs."""
    mock_dependencies["normalize_data"].return_value = None  # Simulate invalid logs

    response = client.post("/query", json={"logs": "invalid_logs"})
    assert response.status_code == 400
    assert "Invalid log format" in response.json()["detail"]

def test_handle_feedback(mock_dependencies):
    """Test the `/feedback` endpoint."""
    response = client.post("/feedback", json=SAMPLE_FEEDBACK)
    assert response.status_code == 200
    assert response.json() == {"status": "Feedback received"}
    mock_dependencies["update_learning"].assert_called_once_with(SAMPLE_FEEDBACK)

def test_handle_feedback_invalid_input():
    """Test the `/feedback` endpoint with invalid input."""
    response = client.post("/feedback", json={"query": "", "feedback": ""})
    assert response.status_code == 422  # Pydantic validation error

def test_handle_query_internal_error(mock_dependencies):
    """Test the `/query` endpoint with an internal error."""
    mock_dependencies["process_query"].side_effect = Exception("Internal error")

    response = client.post("/query", json={"query": SAMPLE_QUERY})
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]

def test_handle_feedback_internal_error(mock_dependencies):
    """Test the `/feedback` endpoint with an internal error."""
    mock_dependencies["update_learning"].side_effect = Exception("Internal error")

    response = client.post("/feedback", json=SAMPLE_FEEDBACK)
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]