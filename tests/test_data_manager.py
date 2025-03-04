import pytest
from app.data_manager import save_analysis  # Import function instead of class

def test_save_analysis():
    sample_data = {"error": "Service crashed", "timestamp": "2024-02-25T12:00:00Z"}
    result = save_analysis(sample_data)
    
    assert isinstance(result, dict)  # Ensure it returns a dictionary
    assert "message" in result  # Ensure response contains expected key
    assert result["message"] == "Data storage not implemented yet"
