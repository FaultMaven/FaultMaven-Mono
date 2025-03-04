import pytest
from fastapi.testclient import TestClient
from app.query_processing import app
from unittest.mock import patch

client = TestClient(app)

def test_empty_request():
    response = client.post("/query", json={})
    assert response.status_code == 200
    assert response.json() == {"response": "How may I help you?"}

def test_logs_only():
    with patch("app.query_processing.process_logs") as mock_process_logs:
        mock_process_logs.return_value = {"log_analysis": "test_log_insights"}
        response = client.post("/query", json={"logs": "test_logs"})
        assert response.status_code == 200
        assert response.json() == {"response": {"log_analysis": "test_log_insights"}}
        mock_process_logs.assert_called_once_with("test_logs")

def test_query_only():
    with patch("app.query_processing.process_query") as mock_process_query:
        mock_process_query.return_value = {"query_response": "test_query_response"}
        response = client.post("/query", json={"query": "test_query"})
        assert response.status_code == 200
        assert response.json() == {"response": {"query_response": "test_query_response"}}
        mock_process_query.assert_called_once_with("test_query")

def test_query_and_logs():
    with patch("app.query_processing.process_logs") as mock_process_logs, \
         patch("app.query_processing.process_query") as mock_process_query:
        mock_process_logs.return_value = {"log_analysis": "test_log_insights"}
        mock_process_query.return_value = {"combined_response": "test_combined_response"}
        response = client.post("/query", json={"query": "test_query", "logs": "test_logs"})
        assert response.status_code == 200
        assert response.json() == {"response": {"combined_response": "test_combined_response"}}
        mock_process_logs.assert_called_once_with("test_logs")
        mock_process_query.assert_called_once_with("test_query", {"log_analysis": "test_log_insights"})

def test_feedback_success():
    with patch("app.query_processing.update_session_learning") as mock_update_session_learning:
        response = client.post("/feedback", json={"query": "test_query", "feedback": "test_feedback"})
        assert response.status_code == 200
        assert response.json() == {"status": "Feedback received"}
        mock_update_session_learning.assert_called_once_with({"query": "test_query", "feedback": "test_feedback"})

def test_invalid_log_format():
    with patch("app.query_processing.normalize_data") as mock_normalize_data:
        mock_normalize_data.return_value = 123  # Simulate invalid log format
        response = client.post("/query", json={"logs": "invalid_logs"})
        assert response.status_code == 400  # Expect 400, since we fix the handler
        assert response.json() == {"detail": "Invalid log format."}  # Check the detail

def test_internal_server_error_query():
    with patch("app.query_processing.process_query") as mock_process_query:
        mock_process_query.side_effect = Exception("Test exception")
        response = client.post("/query", json={"query": "test_query"})
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error."}

def test_internal_server_error_feedback():
    with patch("app.query_processing.update_session_learning") as mock_update_session_learning:
        mock_update_session_learning.side_effect = Exception("Test exception")
        response = client.post("/feedback", json={"query": "test_query", "feedback": "test_feedback"})
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error."}

def test_reject_extra_fields_query_request():
    response = client.post("/query", json={"query": "test_query", "extra": "field"})
    assert response.status_code == 422

def test_reject_extra_fields_feedback_request():
    response = client.post("/feedback", json={"query": "test_query", "feedback": "test_feedback", "extra": "field"})
    assert response.status_code == 422
