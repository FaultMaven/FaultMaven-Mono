# app/query_processing.py

import time
import uuid
import json
import asyncio # Ensure asyncio is imported
from fastapi import (
    FastAPI, Body, HTTPException, Header, UploadFile, File, Form, Response
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List, Any, Union

from app.logger import logger
from config.settings import settings

# --- Import Centralized Models ---
from app.models import (
    QueryRequest,
    FeedbackRequest,
    TroubleshootingResponse,
    DataInsightsResponse,
    UploadedData,
    DataType,
    LogInsights,
    BrowserContextData
)

# --- Import Session Management & Data Classifier ---
from app.session_management import (
    get_or_create_session,
    get_memory_for_session,
    get_data_for_session,
    add_data_to_session,
)
from app.data_classifier import classify_data

# --- Import Data Processors ---
from app.log_metrics_analysis import (
    process_logs_data,
    process_text_data,
    process_metrics_data,
    process_config_data,
)
from app.code_analyzer import process_source_code

# --- Agent/Tool Imports ---
from app.tools import tools_list
from app.llm_provider import llm
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- FastAPI App Setup ---
app = FastAPI(
    title="FaultMaven API",
    description="API for the AI-powered troubleshooting assistant FaultMaven.",
    version="0.2.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Files Mount ---
try:
    app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")
    logger.info("Mounted static frontend directory at /static.")
except RuntimeError:
    logger.warning("Frontend directory not found at project root. Skipping static file mount.")
except Exception as e:
     logger.error(f"Error mounting static directory: {e}")


# === AGENT SETUP ===
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are FaultMaven, an expert SRE assistant. Your goal is to help users troubleshoot issues "
        "by intelligently using the available tools based on their query, the conversation history, and the current session_id ({session_id}). "
        "Think step-by-step. Analyze the query to determine the best tool(s). "
        "Prioritize internal tools (LogSearch, MetricQuery, KnowledgeBaseSearch, ConfigLookup, IncidentHistory) "
        "for system-specific information. Use WebSearchTool ONLY for recent external information, public service statuses, CVEs, or general knowledge. "
        "Use GeneralChatTool as a fallback for summarization or general conversation based *only* on existing context (history and uploaded data summaries). "
        "Provide concise and accurate answers based on tool outputs."
    )),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"), # User query
    MessagesPlaceholder(variable_name="agent_scratchpad"), # Agent working memory
])

agent_executor = None # Initialize as None
try:
    # Ensure the LLM supports the chosen agent type (e.g., OpenAI models for OpenAI Tools agent)
    agent = create_openai_tools_agent(llm, tools_list, agent_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_list,
        verbose=settings.AGENT_VERBOSE, # Control verbosity via settings
        handle_parsing_errors=True, # More robust parsing
        max_iterations=settings.AGENT_MAX_ITERATIONS, # Limit loops via settings
    )
    logger.info("Agent Executor created successfully.")
except Exception as e:
     logger.error(f"Failed to create agent executor on startup: {e}", exc_info=True)
     # agent_executor remains None, handle this in the endpoint
# === END AGENT SETUP ===


# --- API Endpoints ---

@app.post(
    "/data",
    response_model=DataInsightsResponse,
    summary="Upload, Process Data, and Get Contextual Insights",
    description="Uploads data (text, file, or browser context), classifies it, "
                "triggers specialized processing using conversation history context "
                "(if available), stores results, and returns initial insights "
                "with a prompt for next steps."
)
# --- COMPLETE and CORRECT /data Signature ---
async def handle_data(
    response: Response, # Used to set the session ID header
    x_session_id: Optional[str] = Header(None, description="Existing session ID, if available."),
    file: Optional[UploadFile] = File(None, description="File containing data (e.g., logs, config)."),
    text: Optional[str] = Form(None, description="Raw text data pasted by user."),
    context: Optional[BrowserContextData] = Body(None, description="Structured data captured from browser context.")
) -> DataInsightsResponse:
    """
    Handles data submission with context-aware processing.
    """
    # (Implementation of /data remains the same as the fully correct version)
    start_time = time.time()
    logger.info(f"Received /data request. Provided Session ID: {x_session_id}")
    session_id = get_or_create_session(x_session_id)
    response.headers["X-Session-ID"] = session_id
    logger.info(f"Using Session ID: {session_id}")
    session_memory = get_memory_for_session(session_id)
    history_messages = session_memory.chat_memory.messages if session_memory else []
    logger.debug(f"Retrieved {len(history_messages)} history messages for context.")

    original_type: str = ""
    data_content: str = ""
    filename: Optional[str] = None
    source_description: str = "Unknown"

    # 2. Determine Input Source and Extract Content
    input_sources_provided = sum(1 for item in [file, text, context] if item is not None)
    if input_sources_provided == 0:
         raise HTTPException(status_code=400, detail="No data provided. Please submit file, text, or context.")
    if input_sources_provided > 1:
         raise HTTPException(status_code=400, detail="Ambiguous input. Please provide only one of: file, text, or context.")

    try:
        if context:
            original_type = "browser_context"
            data_content = context.selected_text or context.page_content_snippet or json.dumps(context.model_dump())
            source_description = f"Context from URL: {context.url or 'Unknown'}"
        elif file:
            original_type = "file"
            filename = file.filename
            source_description = f"Filename: {filename or 'Unknown'}"
            contents = await file.read()
            try:
                data_content = contents.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Invalid file encoding. Only UTF-8 text parseable currently.")
            finally:
                await file.close()
        elif text:
            original_type = "text"
            source_description = "Pasted Text"
            data_content = text

        if not data_content.strip():
             raise HTTPException(status_code=400, detail="Data content is empty after extraction.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Error reading/preparing data for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading submitted data: {e}")

    # 3. Classify Data
    try:
        classification_result = await classify_data(data_content)
        classified_type = classification_result.data_type
    except Exception as e:
        logger.exception(f"Error during data classification for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to classify data: {e}")

    # 4. Process Data (Context-Aware) & Prepare Results
    content_snippet = data_content[:1500]
    uploaded_data_entry = UploadedData(
        original_type=original_type,
        content_snippet=content_snippet,
        classified_type=classified_type,
        filename=filename,
        processing_status="Processing"
    )
    processed_results_payload: Optional[Union[LogInsights, Dict[str, Any], str]] = None
    user_message = ""
    clarification_prompt = "What would you like to do with this data next?"

    try:
        # Route to specific processor, passing data content AND history_messages
        if classified_type == DataType.SYSTEM_LOGS:
            insights = await process_logs_data(data_content, history=history_messages)
            processed_results_payload = insights
            clarification_prompt = "Log analysis complete. Ask about specific errors, anomalies, or time ranges?"
        elif classified_type == DataType.ISSUE_DESCRIPTION:
            analysis_dict = await process_text_data(data_content, history=history_messages)
            processed_results_payload = analysis_dict
            clarification_prompt = "Problem statement summarized. Upload relevant logs or metrics?"
        elif classified_type == DataType.GENERIC_TEXT:
            analysis_dict = await process_text_data(data_content, history=history_messages)
            processed_results_payload = analysis_dict
            clarification_prompt = "Text analysis complete. What specific questions do you have?"
        elif classified_type == DataType.MONITORING_METRICS:
            metrics_dict = await asyncio.to_thread(process_metrics_data, data_content, history=history_messages)
            processed_results_payload = metrics_dict
            clarification_prompt = "Metrics processed (placeholder). Ask about trends or correlations?"
        elif classified_type == DataType.CONFIGURATION_DATA:
            config_dict = await asyncio.to_thread(process_config_data, data_content, history=history_messages)
            processed_results_payload = config_dict
            clarification_prompt = "Config processed (placeholder). Ask about specific parameters?"
        elif classified_type == DataType.SOURCE_CODE:
            code_dict = await process_source_code(data_content, history=history_messages)
            processed_results_payload = code_dict
            clarification_prompt = "Code processed (placeholder analysis). Ask about functions or structure?"
        else: # UNKNOWN
            uploaded_data_entry.processing_status = "NoProcessingNeeded"
            processed_results_payload = f"Data classified as {classified_type.value}. No specific analysis applied."
            clarification_prompt = "What would you like to ask about this data?"

        if uploaded_data_entry.processing_status == "Processing":
            uploaded_data_entry.processed_results = processed_results_payload
            uploaded_data_entry.processing_status = "Processed"
            user_message = f"Successfully processed {original_type} data ({filename or source_description}). Insights provided."

    except Exception as processing_exc:
        logger.error(f"Processing failed for type {classified_type.value} (session {session_id}): {processing_exc}", exc_info=True)
        uploaded_data_entry.processing_status = "Failed"
        error_message = f"Processing failed: {processing_exc}"
        uploaded_data_entry.processed_results = {"error": error_message}
        processed_results_payload = {"error": error_message}
        user_message = f"Received {original_type} data (classified as {classified_type.value}), but processing failed."
        clarification_prompt = "Processing failed. Try different data or ask a general question?"

    # 5. Store Results in Session
    try:
        add_data_to_session(session_id, uploaded_data_entry)
    except Exception as e:
        logger.exception(f"CRITICAL: Failed to store processed data in session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Data processed but failed to save session state.")

    # 6. Return Insights Response
    if not user_message:
        if uploaded_data_entry.processing_status == "Failed":
             user_message = (
                 f"Data submission processed, but analysis failed for "
                 f"{filename or original_type}."
             )
        elif uploaded_data_entry.processing_status == "NoProcessingNeeded":
             user_message = (
                 f"Received {original_type} data ({filename or source_description}). "
                 f"Ready for questions."
             )
        else:  # Processed
             user_message = (
                 f"Successfully processed {original_type} data "
                 f"({filename or source_description}). Insights provided."
             )

    processing_duration = time.time() - start_time
    logger.info(f"Completed /data request for session {session_id} in {processing_duration:.2f}s")

    return DataInsightsResponse(
        message=user_message,
        classified_type=classified_type.value,
        session_id=session_id,
        insights=processed_results_payload,
        next_prompt=clarification_prompt
    )


# --- /query Endpoint (Agentic version) ---
@app.post(
    "/query",
    response_model=TroubleshootingResponse,
    summary="Ask Troubleshooting Question (Agentic)", # Updated summary
    description="Processes a user query by intelligently routing it to appropriate tools (logs, metrics, KB, web search, etc.) or answering based on context." # Updated description
)
# --- COMPLETE and CORRECT /query Signature ---
async def handle_query(
    response: Response, # To set session ID header
    request: QueryRequest, # Contains the user's query string
    x_session_id: Optional[str] = Header(None, description="Session ID for the conversation context."),
) -> TroubleshootingResponse:
# --- END CORRECTION ---
    """
    Handles user queries using an agent to determine the best way to answer,
    potentially using tools to interact with various data sources.
    """
    # (Implementation of /query remains the same agentic version)
    start_time = time.time()
    logger.info(f"Received agentic /query request. Provided Session ID: {x_session_id}")
    session_id = get_or_create_session(x_session_id)
    response.headers["X-Session-ID"] = session_id
    logger.info(f"Using Session ID: {session_id}")

    if agent_executor is None:
         logger.error("Agent Executor is not initialized. Cannot process query.")
         raise HTTPException(status_code=500, detail="Agent subsystem is not available.")

    session_memory = get_memory_for_session(session_id)
    if session_memory is None:
        logger.error(f"Session {session_id} memory invalid or missing after get_or_create_session.")
        raise HTTPException(
            status_code=400,
            detail="Session expired or invalid. Please upload data or start a new conversation."
        )

    history_messages = session_memory.chat_memory.messages if session_memory.chat_memory else []
    logger.debug(f"Retrieved {len(history_messages)} history messages for agent context.")

    agent_input = {
        "input": request.query,
        "chat_history": history_messages,
        "session_id": session_id
    }
    config = {"configurable": {"session_id": session_id}}

    try:
        logger.debug(f"Invoking agent executor for session {session_id}...")
        agent_response = await agent_executor.ainvoke(agent_input, config=config)
        final_answer = agent_response.get("output", "Error: Agent did not produce a final answer.")

        logger.info(f"Agent execution successful for session {session_id}. Output length: {len(final_answer)}")
        logger.debug(f"Agent final output snippet: {final_answer[:200]}...")

        session_memory.save_context({"input": request.query}, {"output": final_answer})
        logger.debug(f"Manually saved final query and agent answer to session {session_id} memory.")

        processing_duration = time.time() - start_time
        logger.info(f"Completed agentic /query request for session {session_id} in {processing_duration:.2f}s")

        return TroubleshootingResponse(answer=final_answer, action_items=None)

    except Exception as e:
        logger.exception(f"Agent execution failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your query with the agent: {e}")


# --- /feedback endpoint ---
@app.post(
    "/feedback",
    response_model=Dict[str, str],
    summary="Submit Feedback (Not Implemented)",
    description="Endpoint for submitting feedback on responses (currently inactive)."
)
async def handle_feedback(feedback_request: FeedbackRequest) -> Dict[str, str]:
     logger.warning("Feedback endpoint called but is not fully implemented.")
     return {"status": "Feedback endpoint not currently active."}


# --- / endpoint ---
@app.get(
    "/",
    include_in_schema=False # Hide from OpenAPI docs
)
async def root():
     return {"message": "FaultMaven API is running."}