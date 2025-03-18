"""
query_processing.py - Query Processing & API Server

Handles API requests, session management, data processing, and routing
to appropriate backend modules.
"""

from fastapi import FastAPI, Body, HTTPException, Depends, Header, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field, field_validator, constr
from typing import Optional, Dict, Any, List
from app.logger import logger
from app.log_metrics_analysis import process_logs_data, LogInsights, process_data
from app.ai_troubleshooting import process_query, process_query_with_logs
from app.continuous_learning import update_session_learning  # Assuming this exists
from app.llm_provider import LLMProvider, LLMParsingError  # Keep for potential error handling
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
import re
import uuid
import time
import aiohttp
from bs4 import BeautifulSoup
from app.session_management import get_session_data, create_session, save_session_data
from app.data_classifier import classify_data, DataType  # Import data classifier

# Constants for input validation
MAX_QUERY_LENGTH = 10000
MAX_FEEDBACK_LENGTH = 2000
QUERY_REGEX = r"^[a-zA-Z0-9\s.,;:'\"?!-]+$"
MAX_HISTORY_LENGTH = 20  # Maximum conversation turns to store

# --- Pydantic Models ---

class QueryRequest(BaseModel):
    """Defines the structure for incoming query requests (query-only)."""
    query: str = Field(..., description="User's troubleshooting query.")  # Query is now required.

    @field_validator("query")
    def check_query(cls, v):
        if not re.match(QUERY_REGEX, v):
            raise ValueError("Query contains invalid characters.")
        if not 1 <= len(v) <= MAX_QUERY_LENGTH:  # Enforce length constraints
            raise ValueError("Query length is out of bounds")
        return v

class QueryResponse(BaseModel):
    """Defines the structure for API query responses."""
    response: str
    type: str  # "query-only", "data-summary", "combined", "empty", "error"
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None # Add a message field

class DataResponse(BaseModel):
    """Defines the structure for data upload responses."""
    summary: str
    type: str # "data-summary"
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None # Add a message field


class FeedbackRequest(BaseModel):
    """Defines the structure for user feedback submissions."""
    query: str = Field(..., description="The query associated with the feedback.")

    @field_validator("query")
    def validate_query(cls, v):
        v = v.strip()
        if not (1 <= len(v) <= MAX_FEEDBACK_LENGTH):
            raise ValueError("Query length is out of bounds.")
        return v
    feedback: constr(strip_whitespace=True, min_length=1, max_length=MAX_FEEDBACK_LENGTH) = Field(..., description="User feedback on the query response.")



# --- FastAPI App Setup ---

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development; restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend") # To serve frontend files

# --- Dependency for Session Management ---
def get_sessions() -> Dict[str, Dict[str, Any]]:
    """Dependency function to provide the sessions dictionary."""
    if not hasattr(get_sessions, "sessions"):
        get_sessions.sessions: Dict[str, Dict[str, Any]] = {}  # Initialize if it doesn't exist
    return get_sessions.sessions

def get_llm_provider():
    """Dependency function to provide an instance of LLMProvider."""
    return LLMProvider()

# --- API Endpoints ---

@app.post("/data", response_model=DataResponse)
async def handle_data(
    response: Response,
    x_session_id: Optional[str] = Header(None),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    sessions: Dict[str, Dict[str, Any]] = Depends(get_sessions),  # Inject sessions!
    file: Optional[UploadFile] = File(None),  # For file uploads
    text: Optional[str] = Form(None),  # For text input as form data
) -> JSONResponse:
    """Handles data upload (text, file, or URL)."""

    session_id = x_session_id or create_session(sessions) # Pass sessions
    session = get_session_data(session_id, sessions) # Pass sessions

    if x_session_id and not session:  # Session ID provided but invalid
        response.status_code = 400  # Bad Request
        return JSONResponse(content=DataResponse(summary="", type="error", message="Session expired or invalid. Please start a new conversation.").dict(), headers={"X-Session-ID": session_id})


    if not session: #Create if session is not valid
        session = sessions[session_id] = {"history": [], "data": [], "last_activity": time.time()}

    headers = {"X-Session-ID": session_id}

    # --- Data Type Mapping (User-Friendly) ---
    data_type_mapping = {
        DataType.SYSTEM_LOGS: "logs",
        DataType.MONITORING_METRICS: "metrics",
        DataType.CONFIGURATION_DATA: "configuration data",
        DataType.ROOT_CAUSE_ANALYSIS: "root cause analysis data",
        DataType.TEXT: "text",
        DataType.UNKNOWN: "unknown data type",
    }

    try:
        if file:
            data_type = "file"
            logger.debug(f"File received: {file.filename}")
            contents = await file.read()  # Read file contents as bytes
            try:
                data_content = contents.decode("utf-8")  # Decode as UTF-8
            except UnicodeDecodeError:
                await file.close() #Close it before throw exception
                raise HTTPException(status_code=400, detail="Invalid file encoding.  Must be UTF-8.")
            finally:
                await file.close()
        elif text:
            data_type = "text"
            data_content = text
            logger.debug(f"Text data received: {data_content[:100]}...") # Log a snippet of the content
        else:
            # Should never happen because of Pydantic validation, but good practice
            logger.error("No data provided in request.")
            raise HTTPException(status_code=400, detail="No data provided.")

        logger.debug(f"Data type: {data_type}, Data content length: {len(data_content)}") # Log data type and content length

        # --- CLASSIFY THE DATA ---
        data_classification = classify_data(data_content, llm_provider)
        logger.info(f"Data classified as: {data_classification.data_type}")

        # --- Store the RAW data and the CLASSIFICATION ---
        session["data"].append(
            {
                "type": data_type,   # Store the *original* type (text/file)
                "content": data_content,
                "summary": None,    # No summary yet at this point
                'llm_summary': "",   # No LLM summary yet
                "data_type": data_classification.data_type,  # Store the *classified* type.
                "timestamp": time.time()
            }
        )
        session["last_activity"] = time.time()

        # --- Construct the prompting message (USER-FRIENDLY) ---
        # Get user-friendly type.  Use .get() with default for safety.
        display_type = data_type_mapping.get(data_classification.data_type, "data")
        message = (
            f"Data received ({display_type}).  What would you like me to do with it? (e.g., summarize, analyze, troubleshoot)"
        )
        response_data = DataResponse(summary="", type="data-received", message=message, data=None) #No summary
        return JSONResponse(content=response_data.dict(), headers=headers) #Return result

    except ValueError as e:
        logger.error(f"Data Processing Error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:   #pylint: disable=broad-exception-caught
        logger.exception(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@app.post("/query", response_class=HTMLResponse)
async def handle_query(
    response: Response,
    request: QueryRequest = Body(...),
    x_session_id: Optional[str] = Header(None),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    sessions: Dict[str, Dict[str, Any]] = Depends(get_sessions)  # Inject sessions!
) -> str: #Return HTML string
    """Handles user queries, with session management, returns HTML response."""
    logger.info(f"Received request: {request.dict()}")

    session_id = x_session_id or create_session(sessions) #Pass sessions
    session = get_session_data(session_id, sessions) #Pass sessions
    headers = {"X-Session-ID": session_id}

    if x_session_id and not session:  # Session ID provided but invalid
        response.status_code = 400  # Bad Request
        # --- CORRECTLY RETURN HTML FOR ERRORS ---
        return  f"<div class='conversation-item error-response'><p><strong>Error:</strong> Session expired or invalid. Please start a new conversation.</p></div>" # Return formatted HTML

    if not session: #Create if session is not valid
        session = sessions[session_id] = {"history": [], "data": [], "last_activity": time.time()}

    context = session.get("history", [])
    session_data = session.get("data")  # all data.

    try:
        if session_data:
            # If there's data, prepare the combined prompt using all available log insights.

            response_text = process_query_with_logs(request.query, session_data, llm_provider, context)
            response_type = "combined"
        else:
             response_text = process_query(request.query, llm_provider, context)  # Pass context
             response_type = "query-only"

        # Truncate history if it's too long
        if len(session["history"]) >= MAX_HISTORY_LENGTH:
            truncated_message = "Conversation history has been truncated to the most recent interactions due to length limits. For best results, please start a new conversation if you're addressing a new issue."
            session["history"] = session["history"][-(MAX_HISTORY_LENGTH - 2):] #Keep recent ones
            session["history"].insert(0,{"role": "assistant", "content": truncated_message}) #Inform user
        else:
            truncated_message = None # Set to None if not truncated

        session["history"].append({"role": "user", "content": request.query, "timestamp": time.time()}) # Store the raw text query
        session["history"].append({"role": "assistant", "content": response_text, "timestamp": time.time()}) # store the raw text.
        session["last_activity"] = time.time() # Update last activity time
        save_session_data(session_id, session, sessions) # Pass SESSIONS here

        # Include a message if history was truncated, prepended to the response
        if truncated_message:
            response_text = f"<p>{truncated_message}</p>" + response_text

        response.headers.update(headers) # Update headers
        return response_text

    except LLMParsingError as e:
      logger.error(f"LLM parsing error: {e}", exc_info=True)
      raise HTTPException(status_code=502, detail="Error processing LLM response.")
    except ValueError as ve:
        logger.error(f"Value Error: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except KeyError as ke:
        logger.error(f"Key Error: {ke}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Unexpected Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")
    
    
@app.post("/feedback", response_model=Dict[str, str])  # Keep simple response for feedback
async def handle_feedback(feedback_request: FeedbackRequest) -> Dict[str, str]:
    """Handles user feedback and updates the learning module."""
    try:
        update_session_learning(feedback_request.dict())
        logger.info("Feedback received: %s", feedback_request.dict())
        return {"status": "Feedback received"}  # Consistent response
    except ValueError as ve:
        logger.error(f"Feedback Value Error: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")