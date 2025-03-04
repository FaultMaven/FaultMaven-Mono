"""
query_processing.py - Query Processing & API Server
This module acts as the entry point for the FaultMaven system, handling API requests
and routing them to the appropriate backend modules. It does **not** perform troubleshooting
or log analysis directly but ensures that each request is properly classified and routed.
## Responsibilities:
1️⃣ **Classify User Requests** - Determines whether a request is **"query-only"**, **"data-only"**, or **"combined"**.
2️⃣ **Validate & Normalize Input** - Ensures at least one valid field (`query` or `logs`) is provided.
  - Normalizes observability data (logs, metrics) before processing.
3️⃣ **Route Requests to Backend Modules** - Queries → **AI Troubleshooting Module** - Logs → **Log Analysis Module** - Combined Queries & Logs → **Both**
4️⃣ **Handle User Feedback** - Captures and forwards feedback to **Continuous Learning Module**.
  - Ensures structured feedback processing.
This module ensures efficient query processing, structured insights, and seamless request routing.
"""
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from app.logger import logger
from app.log_metrics_analysis import analyze_logs_metrics
from app.ai_troubleshooting import troubleshoot_issue
from app.continuous_learning import update_session_learning
from app.data_manager import normalize_data
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI App
app = FastAPI()

# Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend Files
app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")

### **🔹 Input Validation Models**
class QueryRequest(BaseModel):
    """Defines the structure for incoming query requests."""
    query: Optional[str] = Field(default=None, description="User's troubleshooting query.")
    logs: Optional[str] = Field(default=None, description="Raw logs or observability data.")
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields

class FeedbackRequest(BaseModel):
    """Defines the structure for user feedback submissions."""
    query: str = Field(..., min_length=1, description="The query associated with the feedback.")
    feedback: str = Field(..., min_length=1, description="User feedback on the query response.")
    model_config = ConfigDict(extra="forbid")  # Rejects unexpected fields

### **🔹 Helper Functions**
def process_logs(logs: str) -> Dict[str, Any]:
    """Normalizes and analyzes logs."""
    normalized_data = normalize_data(logs)
    if isinstance(normalized_data, str):
        log_text = normalized_data
    elif isinstance(normalized_data, dict):
        log_text = normalized_data.get("normalized_data", "")
    else:
        raise HTTPException(status_code=400, detail="Invalid log format.")
    return analyze_logs_metrics(log_text)

def process_query(query: str, log_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Processes a query with optional log insights."""
    return troubleshoot_issue({"query": query, "log_insights": log_insights})

### **🔹 API Endpoints**
@app.post("/query")
async def handle_query(request: QueryRequest = Body(default={})) -> Dict[str, Any]:
    """
    Handles user queries and routes logs for analysis if needed.
    **Cases:**
    - ✅ **Query-Only:** Routes to AI Troubleshooting.
    - ✅ **Data-Only:** Routes logs to Log Analysis.
    - ✅ **Combined Query & Logs:** Sends logs for analysis & passes results to AI Troubleshooting.
    """
    if not request.query and not request.logs:
        return {"response": "How may I help you?"}

    try:
        # **Case 1: Logs Only**
        if request.logs and not request.query:
            log_insights = process_logs(request.logs)
            return {"response": log_insights}

        # **Case 2: Query Only**
        if request.query and not request.logs:
            response = process_query(request.query)
            logger.info(f"Query Processed: {request.query} -> {response}")
            return {"response": response}

        # **Case 3: Query + Logs**
        log_insights = process_logs(request.logs)
        response = process_query(request.query, log_insights)
        logger.info(f"Query & Logs Processed: {request.query} -> {response}")
        return {"response": response}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.post("/feedback")
async def handle_feedback(feedback: FeedbackRequest) -> Dict[str, str]:
    """
    Handles user feedback and updates the learning module.
    """
    try:
        feedback_dict = feedback.model_dump()
        update_session_learning(feedback_dict)
        return {"status": "Feedback received"}
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")