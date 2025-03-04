import pytest
from app.continuous_learning import update_session_learning

### 🛠 TEST CASES ###
def test_update_session_learning_valid():
    """Test updating session learning with valid feedback."""
    feedback = {"query": "Service failure", "feedback": "Resolved by restarting"}
    response = update_session_learning(feedback)
    assert isinstance(response, dict)
    assert response.get("status") == "Feedback processed"

def test_update_session_learning_empty():
    """Test updating session learning with empty feedback."""
    response = update_session_learning({})
    assert isinstance(response, dict)
    assert response.get("status") == "Feedback processed"

def test_update_session_learning_invalid():
    """Test updating session learning with an invalid data type."""
    response = update_session_learning("invalid feedback format")
    assert isinstance(response, dict)
    assert response.get("status") == "Feedback processed"  # Ensures function is resilient

### ✅ Run tests manually if executed directly
if __name__ == "__main__":
    pytest.main()
