"""
query_processing.py - Query Processing & API Server

Handles API requests, session management, data processing, and routing
to appropriate backend modules.
"""

from fastapi import FastAPI, Body, HTTPException, Depends, Header, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, model_validator, constr
from typing import Optional, Dict, Any, List, Union
from app.logger import logger
from app.log_metrics_analysis import process_logs_data, LogInsights
from app.ai_troubleshooting import process_query, process_query_with_logs #Removed process_data_summary
from app.continuous_learning import update_session_learning  # Assuming this exists
from app.llm_provider import LLMProvider, LLMParsingError  # Keep for potential error handling
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
import re
import uuid
import requests  # For fetching web pages
from bs4 import BeautifulSoup  # For HTML parsing
import time
import aiohttp
from app.session_management import get_session_data, create_session

# Constants for input validation
MAX_QUERY_LENGTH = 10000
MAX_FEEDBACK_LENGTH = 2000
QUERY_REGEX = r"^[a-zA-Z0-9\s.,;:'\"?!-]+$"
MAX_HISTORY_LENGTH = 20  # Maximum conversation turns to store

# --- In-memory session storage (for development) ---
# sessions = {}  # {session_id: {"history": [...], "data": [ { "type": "text", "content": "...", "summary": "..."}]}
SESSION_TIMEOUT = settings.SESSION_TIMEOUT #Read from settings


# --- Pydantic Models ---

class QueryRequest(BaseModel):
    """Defines the structure for incoming query requests (query-only)."""
    query: str = Field(..., description="User's troubleshooting query.") # Query is now required.

    @field_validator("query")
    def check_query(cls, v):
        if not re.match(QUERY_REGEX, v):
            raise ValueError("Query contains invalid characters.")
        if not 1 <= len(v) <= MAX_QUERY_LENGTH: # Enforce length constraints
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
    url: Optional[str] = Form(None),  # For URL input as form data
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
        elif url:
            data_type = "url"
            logger.debug(f"URL received: {url}")
            data_content = await fetch_data_from_url(url)
            if data_content is None: #fetch_data_from_url returns None on error.
              raise HTTPException(status_code=400, detail = "Failed to fetch URL content.")
        else:
            # Should never happen because of Pydantic validation, but good practice
            logger.error("No data provided in request.")
            raise HTTPException(status_code=400, detail="No data provided.")

        logger.debug(f"Data type: {data_type}, Data content length: {len(data_content)}") # Log data type and content length

        log_insights = process_logs_data(data_content, llm_provider)
        # Generate LLM-powered summary *and* store the structured insights
        llm_summary = log_insights.summary # Access directly from returned value!
        session["data"].append({"type": data_type, "content": data_content, "summary": log_insights.dict(), 'llm_summary': llm_summary}) # Store LLM summary and make insights to be dict
        session["last_activity"] = time.time()

        response_data = DataResponse(summary=llm_summary, type="data-summary", data=log_insights.dict(), message = "Data is received and stored.") # Return data
        return JSONResponse(content=response_data.dict(), headers=headers) #Return result

    except ValueError as e:
        logger.error(f"Data Processing Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:   #pylint: disable=broad-exception-caught
        logger.exception(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

async def fetch_data_from_url(url: str) -> Optional[str]:
    """Fetches and extracts text content from a URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()  # Raise HTTP errors
                soup = BeautifulSoup(await response.text(), 'html.parser')
                for script in soup(["script", "style"]):  # Remove scripts and styles
                    script.extract()
                return soup.get_text(separator=' ', strip=True)
    except aiohttp.ClientError as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

@app.post("/query", response_model=QueryResponse)
async def handle_query(
    response: Response,
    request: QueryRequest = Body(...),
    x_session_id: Optional[str] = Header(None),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    sessions: Dict[str, Dict[str, Any]] = Depends(get_sessions)  # Inject sessions!
) -> JSONResponse:
    """Handles user queries, with session management."""
    logger.info(f"Received request: {request.dict()}")

    session_id = x_session_id or create_session(sessions) #Pass sessions
    session = get_session_data(session_id, sessions) #Pass sessions
    headers = {"X-Session-ID": session_id}

    if x_session_id and not session:  # Session ID provided but invalid
        response.status_code = 400  # Bad Request
        return JSONResponse(content=QueryResponse(response="", type="error", message="Session expired or invalid. Please start a new conversation.").dict(), headers=headers)

    if not session: #Create if session is not valid
        session = sessions[session_id] = {"history": [], "data": [], "last_activity": time.time()}

    context = session.get("history", [])
    session_data = session.get("data")  # all data.

    try:
        if session_data:
            # If there's data, prepare the combined prompt using all available log insights.
            log_insights_list = [LogInsights(**data_item['summary']) for data_item in session_data]
            response = process_query_with_logs(request.query, log_insights_list, llm_provider, context) #Pass all data.
            response_type = "combined"
        else:
             response = process_query(request.query, llm_provider, context)  # Pass context
             response_type = "query-only"

        # Truncate history if it's too long
        if len(session["history"]) >= MAX_HISTORY_LENGTH:
            truncated_message = "Conversation history has been truncated to the most recent interactions due to length limits. For best results, please start a new conversation if you're addressing a new issue."
            session["history"] = session["history"][-(MAX_HISTORY_LENGTH - 2):] #Keep recent ones
            session["history"].insert(0,{"role": "assistant", "content": truncated_message}) #Inform user

        session["history"].append({"role": "user", "content": request.query})
        session["history"].append({"role": "assistant", "content": response})
        session["last_activity"] = time.time() # Update last activity time

        # Include a message if history was truncated
        response_message = truncated_message if 'truncated_message' in locals() else None
        response_data =  QueryResponse(response=response, type=response_type, message=response_message)
        return JSONResponse(content=response_data.dict(), headers = headers) #Return result

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
async def handle_feedback(feedback: FeedbackRequest) -> Dict[str, str]:
    """Handles user feedback and updates the learning module."""
    try:
        feedback_dict = feedback.dict()
        update_session_learning(feedback_dict)
        logger.info(f"Feedback received: {feedback_dict}")
        return {"status": "Feedback received"}  # Consistent response
    except ValueError as ve:
        logger.error(f"Feedback Value Error: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")