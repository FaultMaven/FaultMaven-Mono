from fastapi import FastAPI
from pydantic import BaseModel

from app.logger import logger
from app.adaptive_query_handler import process_query
from app.log_metrics_analysis import analyze_logs_metrics
from app.ai_troubleshooting import troubleshoot_issue
from app.continuous_learning import update_session_learning
from app.data_manager import normalize_data

app = FastAPI()

# Define the expected JSON request format
class QueryRequest(BaseModel):
    query: str
    logs: str = None  # Optional logs/metrics

@app.post("/query")
async def handle_query(request: QueryRequest):
    # Normalize input data if logs/metrics are provided
    normalized_data = normalize_data(request.logs) if request.logs else None
    
    # Process query to determine troubleshooting needs
    processed_query = process_query(request.query, normalized_data)
    
    # If logs need analysis, run log & metrics analysis before troubleshooting
    if processed_query['needs_log_analysis']:
        log_insights = analyze_logs_metrics(normalized_data)
        response = troubleshoot_issue(log_insights)
    else:
        response = troubleshoot_issue(processed_query)
    
    logger.info(f"Query handled: {request.query} -> {response}")
    return {"response": response}

@app.post("/feedback")
async def handle_feedback(feedback: dict):
    update_session_learning(feedback)
    return {"status": "Feedback received"}

