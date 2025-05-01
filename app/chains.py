# app/chains.py
# --- LangChain Core Imports ---
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain.memory import ConversationBufferMemory # For type hinting only

# --- Standard Library Imports ---
from typing import List, Dict, Any, Optional, Union
import time
import json
import warnings # To potentially suppress warnings if needed later

# --- Application Specific Imports ---
from app.llm_provider import llm
from app.models import TroubleshootingResponse, UploadedData, LogInsights, DataType
from app.logger import logger # Ensure logger is imported

# === Setup Core Chain Components ===

# --- 1. Output Parser ---
output_parser = PydanticOutputParser(pydantic_object=TroubleshootingResponse)

# --- 2. Prompt Template ---
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are FaultMaven, an AI assistant specialized in troubleshooting complex system issues for SREs and DevOps engineers.
Your goal is to provide accurate analysis and actionable advice based *only* on the provided context.
Analyze the user's query, the ongoing conversation history, and any provided system data summaries (logs, metrics, config snippets, etc.).
Provide a clear, concise analysis ('answer') of the potential problem or answer the user's question based on the context.
Suggest specific, actionable next steps ('action_items') ONLY if they are directly relevant, supported by the data, and helpful for diagnosis or resolution. Do NOT suggest generic troubleshooting steps unless specifically asked.
If the provided context is insufficient to provide a confident answer or safe action, clearly state what information is missing and ask a clarifying question. Do not guess or hallucinate commands or system details.
Think step-by-step before formulating the final response.
Format your final response strictly as JSON with the following keys:
{format_instructions}
""",
        ),
        MessagesPlaceholder(variable_name="chat_history"), # Use updated memory key
        (
            "human",
            "Relevant Data Context Provided:\n"
            "```\n"
            "{uploaded_data}\n"
            "```\n\n"
            "User Query: {query}"
        ),
    ]
).partial(format_instructions=output_parser.get_format_instructions())


# --- 3. Helper Functions for Context Formatting ---

# Define helper BEFORE it's called by format_uploaded_data
def format_log_data_for_summary(log_insights: LogInsights) -> str:
    """
    Formats the LogInsights object into a readable string for the LLM prompt.
    """
    parts = []
    if log_insights.level_counts:
        levels = ", ".join(f"{k}: {v}" for k, v in log_insights.level_counts.items())
        parts.append(f"- Log Levels Found: {levels}")
    if log_insights.metrics:
        metrics = ", ".join(f"{k}: {v:.2f}" for k, v in log_insights.metrics.items())
        parts.append(f"- Derived Metrics: {metrics}")
    if log_insights.anomalies:
        # Use the label consistent with previous successful test runs
        parts.append("- Detected Anomalies/Patterns:")
        parts.extend([f"  - {a}" for a in log_insights.anomalies[:5]])
        if len(log_insights.anomalies) > 5: parts.append("  - ... (more anomalies found)")
    if log_insights.summary and log_insights.summary != "Error generating data summary via LLM.":
        # Use the label consistent with previous successful test runs
        parts.append(f"- Processing Summary: {log_insights.summary}")
    if log_insights.error_messages:
        parts.append("- Sample Error Messages:")
        parts.extend([f"  - {e[:150]}{'...' if len(e) > 150 else ''}" for e in log_insights.error_messages[:3]])
        if len(log_insights.error_messages) > 3: parts.append("  - ... (more errors found)")

    return "\n".join(parts) if parts else "Log data processed, but no specific programmatic insights extracted."

# --- Function with DEBUG Logging ---
def format_uploaded_data(data_list: List[UploadedData]) -> str:
    """
    Formats the list of stored UploadedData objects (prioritizing processed results)
    into a single string block for the LLM prompt context. [WITH DEBUG LOGS]
    """
    logger.debug(f"Formatting {len(data_list)} data blocks.") # DEBUG Start
    if not data_list:
        return "No data has been uploaded for this session yet."

    formatted_parts = []
    max_data_blocks_in_prompt = 3
    start_index = max(0, len(data_list) - max_data_blocks_in_prompt)

    for i, d in enumerate(data_list[start_index:]):
        block_index = start_index + i + 1
        logger.debug(f"Block {block_index}: Status='{d.processing_status}', HasResults={d.processed_results is not None}, HasSnippet={d.content_snippet is not None}") # DEBUG Status

        filename_part = f" (Filename: {d.filename})" if d.filename else ""
        try:
            time_str = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(d.timestamp))
        except Exception as e:
            logger.warning(f"Timestamp formatting error: {e}") # Log timestamp errors
            time_str = "Timestamp N/A"
        block_header = (
            f"--- Data Block {block_index} "
            f"({d.classified_type.value}{filename_part} at {time_str}, "
            f"Status: {d.processing_status}) ---"
        )

        block_content = ""
        # Processed status with results takes priority
        if d.processing_status == "Processed" and d.processed_results:
            results = d.processed_results
            logger.debug(f"Block {block_index}: Status Processed with results. Type: {type(results)}") # DEBUG
            if isinstance(results, LogInsights):
                block_content = format_log_data_for_summary(results) # Call helper
            elif isinstance(results, dict):
                if 'summary' in results:
                    block_content = f"- Processing Summary: {results['summary']}" # Use consistent label
                elif 'error' in results:
                     # This case should ideally not happen if status is "Processed"
                     logger.warning(f"Block {block_index}: Status 'Processed' but results contain 'error' key.")
                     block_content = f"Processing Error: {results['error']}"
                else: # Fallback for other dictionaries (e.g., MCP)
                    try:
                        block_content = "Processed Data:\n" + json.dumps(results, indent=2, ensure_ascii=False)[:1000] + ("..." if len(json.dumps(results))>1000 else "")
                    except TypeError:
                        block_content = f"Processed Data (non-serializable): {str(results)[:1000]}..."
            elif isinstance(results, str):
                block_content = results # Display simple string result
            else:
                block_content = f"Processed Data (Unknown Format): {str(results)[:1000]}..."

        # Fallback to snippet if failed, still processing, or processed without specific results
        elif d.content_snippet:
             block_content = f"Content Snippet:\n{d.content_snippet}"
             logger.debug(f"Block {block_index}: Using snippet. Status='{d.processing_status}'") # DEBUG
             if d.processing_status == "Failed":
                 logger.debug(f"Block {block_index}: Status is Failed. Checking processed_results: {d.processed_results!r}") # DEBUG
                 error_msg = ""
                 # --- THIS IS THE CRITICAL LOGIC ---
                 is_dict = isinstance(d.processed_results, dict)
                 has_error_key = 'error' in d.processed_results if is_dict else False
                 logger.debug(f"Block {block_index}: Is Dict? {is_dict}, Has 'error' key? {has_error_key}") # DEBUG
                 if is_dict and has_error_key:
                     error_value = d.processed_results['error']
                     error_msg = f": {error_value}" # Append the error value
                     logger.debug(f"Block {block_index}: Extracted error_msg='{error_msg}'") # DEBUG
                 else:
                      logger.debug(f"Block {block_index}: No specific error message found in processed_results dict.") # DEBUG
                 block_content += f"\n(Processing failed for this data{error_msg})" # Append generated message
                 logger.debug(f"Block {block_index}: Appended failure notice. Final block_content end: '...{block_content.splitlines()[-1]}'") # DEBUG
                 # ---------------------------------
             elif d.processing_status == "Processing":
                 block_content += "\n(Processing is still in progress for this data)"
        else:
             # Case where there's no snippet and no results/failed status
             block_content = f"(No content snippet or processed results available for this block - Status: {d.processing_status})"
             logger.debug(f"Block {block_index}: No snippet, no results. Status='{d.processing_status}'") # DEBUG

        formatted_parts.append(f"{block_header}\n{block_content}")

    # --- Construct Final Context String ---
    num_shown = len(formatted_parts)
    num_total = len(data_list)
    if num_shown < num_total:
         header = f"Showing context from the {num_shown} most recent data blocks (out of {num_total} total):\n"
    elif num_shown > 0:
         header = f"Showing context from {num_shown} data block(s) uploaded:\n"
    else:
         header = ""

    return header + "\n\n".join(formatted_parts)


# --- 4. Define the Core LangChain Chain (using LCEL) ---
chain = (
    RunnablePassthrough.assign(
        # Use 'chat_history' as the key to match MessagesPlaceholder variable_name
        chat_history=RunnableLambda(lambda x: x["memory"].load_memory_variables({})["chat_history"]),
        uploaded_data=RunnableLambda(lambda x: format_uploaded_data(x["uploaded_data_list"]))
    )
    | prompt_template
    | llm
    | output_parser
)

# --- Main Service Function for Query Processing ---
async def process_user_query(
    session_id: str,
    query: str,
    memory: ConversationBufferMemory,
    data_list: List[UploadedData]
) -> TroubleshootingResponse:
    # (Keep implementation as is - looks correct)
    logger.info(f"Processing query for session_id: {session_id}")
    logger.debug(f"Query: '{query[:100]}...', Data Blocks: {len(data_list)}, History Length: {len(memory.chat_memory.messages)}")

    chain_input = {
        "query": query,
        "uploaded_data_list": data_list,
        "memory": memory,
    }
    config = RunnableConfig(configurable={"session_id": session_id})

    try:
        start_time = time.time()
        ai_response: TroubleshootingResponse = await chain.ainvoke(chain_input, config=config)
        end_time = time.time()
        logger.info(f"Successfully generated response for session_id: {session_id} in {end_time - start_time:.2f}s")
        # ... (debug logging of response) ...
        return ai_response
    except Exception as e:
        logger.exception(f"Error invoking LangChain chain for session {session_id}: {e}")
        raise