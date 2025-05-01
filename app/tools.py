# app/tools.py

import asyncio
from typing import Type, Optional, List, Dict, Any # Make sure Dict, Any are imported
from pydantic import BaseModel, Field
from langchain.tools import BaseTool, Tool # Import BaseTool and Tool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults # Example Tool

# Imports needed for GeneralChatTool and settings
from app.chains import process_user_query # Corrected path if needed
from app.session_management import get_memory_for_session, get_data_for_session
from app.logger import logger
from config.settings import settings

# --- Tool Input Schemas ---
# (Definitions remain the same)
class LogSearchInput(BaseModel):
    query: str = Field(description="Keywords or filters for searching logs.")
    time_range: Optional[str] = Field(None, description="Optional time range (e.g., '1h', '30m', '2025-04-28T10:00:00Z/2025-04-28T11:00:00Z'). Defaults to a recent short interval if not specified.")
    service_filter: Optional[str] = Field(None, description="Optional service name to filter logs by.")

class MetricQueryInput(BaseModel):
    metric_name: str = Field(description="The name of the metric to query (e.g., 'cpu_usage', 'request_latency_ms').")
    time_range: Optional[str] = Field(None, description="Optional time range (e.g., '1h', '30m'). Defaults to recent if not specified.")
    labels_filter: Optional[Dict[str, str]] = Field(None, description="Optional dictionary of labels to filter metrics by (e.g., {'service': 'auth-api', 'instance': 'pod-xyz'}).")

class KBSearchInput(BaseModel):
    search_query: str = Field(description="The natural language query to search the knowledge base (runbooks, documentation) for.")

class ConfigLookupInput(BaseModel):
    config_name: str = Field(description="Name or path of the configuration file/parameter to look up.")
    service_context: Optional[str] = Field(None, description="Optional service name context for the configuration.")
    history_depth: Optional[int] = Field(1, description="Number of historical versions to potentially retrieve (if available). Defaults to 1 (current).")

class IncidentHistoryInput(BaseModel):
    search_query: str = Field(description="Keywords or incident ID to search for in the incident history database.")
    status_filter: Optional[str] = Field(None, description="Optional status to filter incidents by (e.g., 'resolved', 'open').")

class GeneralChatToolInput(BaseModel):
    query: str = Field(description="The user's query to be answered based on general knowledge and conversation context.")
    session_id: str = Field(description="The current user session ID.")


# --- Tool Definitions (with Type Annotations) ---

class LogSearchTool(BaseTool):
    name: str = "LogSearchTool" # Added : str
    description: str = ("Useful for searching system logs based on keywords, time range, and service filters. " # Added : str
                   "Provides relevant log snippets or summaries.")
    args_schema: Type[BaseModel] = LogSearchInput

    def _run(
        self, query: str, time_range: Optional[str] = None, service_filter: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"SYNC Tool: LogSearchTool called (Query: {query}, Time: {time_range}, Service: {service_filter}) - Placeholder")
        return "[LogSearchTool Placeholder: Log search not fully implemented.]"

    async def _arun(
        self, query: str, time_range: Optional[str] = None, service_filter: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"ASYNC Tool: LogSearchTool called (Query: {query}, Time: {time_range}, Service: {service_filter}) - Placeholder")
        await asyncio.sleep(0.1)
        return "[LogSearchTool Placeholder: Log search not fully implemented.]"

class MetricQueryTool(BaseTool):
    name: str = "MetricQueryTool" # Added : str
    description: str = ("Useful for querying monitoring metrics like CPU usage, latency, error rates, etc. " # Added : str
                   "Specify metric name, optional time range, and optional label filters.")
    args_schema: Type[BaseModel] = MetricQueryInput

    def _run(
        self, metric_name: str, time_range: Optional[str] = None, labels_filter: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"SYNC Tool: MetricQueryTool called (Metric: {metric_name}, Time: {time_range}, Labels: {labels_filter}) - Placeholder")
        return f"[MetricQueryTool Placeholder: Metric query not implemented.]"

    async def _arun(
        self, metric_name: str, time_range: Optional[str] = None, labels_filter: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"ASYNC Tool: MetricQueryTool called (Metric: {metric_name}, Time: {time_range}, Labels: {labels_filter}) - Placeholder")
        await asyncio.sleep(0.1)
        return f"[MetricQueryTool Placeholder: Metric query not implemented.]"

class KnowledgeBaseSearchTool(BaseTool):
    name: str = "KnowledgeBaseSearchTool" # Added : str
    description: str = ("Useful for searching internal knowledge base articles, runbooks, and documentation " # Added : str
                   "for troubleshooting procedures, guides, or explanations. Input is a natural language query.")
    args_schema: Type[BaseModel] = KBSearchInput

    def _run(self, search_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        logger.info(f"SYNC Tool: KnowledgeBaseSearchTool called (Query: {search_query}) - Placeholder")
        return f"[KnowledgeBaseSearchTool Placeholder: KB search not implemented.]"

    async def _arun(self, search_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        logger.info(f"ASYNC Tool: KnowledgeBaseSearchTool called (Query: {search_query}) - Placeholder")
        await asyncio.sleep(0.1)
        return f"[KnowledgeBaseSearchTool Placeholder: KB search not implemented.]"

class ConfigurationLookupTool(BaseTool):
    name: str = "ConfigurationLookupTool" # Added : str
    description: str = ("Useful for looking up current or historical configuration parameters or files " # Added : str
                   "for specific services.")
    args_schema: Type[BaseModel] = ConfigLookupInput

    def _run(
        self, config_name: str, service_context: Optional[str] = None, history_depth: Optional[int] = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"SYNC Tool: ConfigurationLookupTool called (Config: {config_name}, Service: {service_context}, Depth: {history_depth}) - Placeholder")
        return f"[ConfigurationLookupTool Placeholder: Config lookup not implemented.]"

    async def _arun(
        self, config_name: str, service_context: Optional[str] = None, history_depth: Optional[int] = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"ASYNC Tool: ConfigurationLookupTool called (Config: {config_name}, Service: {service_context}, Depth: {history_depth}) - Placeholder")
        await asyncio.sleep(0.1)
        return f"[ConfigurationLookupTool Placeholder: Config lookup not implemented.]"

class IncidentHistoryTool(BaseTool):
    name: str = "IncidentHistoryTool" # Added : str
    description: str = ("Useful for searching past incidents by keywords or ID to find similar issues, " # Added : str
                   "resolutions, or patterns.")
    args_schema: Type[BaseModel] = IncidentHistoryInput

    def _run(
        self, search_query: str, status_filter: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"SYNC Tool: IncidentHistoryTool called (Query: {search_query}, Status: {status_filter}) - Placeholder")
        return f"[IncidentHistoryTool Placeholder: Incident search not implemented.]"

    async def _arun(
        self, search_query: str, status_filter: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        logger.info(f"ASYNC Tool: IncidentHistoryTool called (Query: {search_query}, Status: {status_filter}) - Placeholder")
        await asyncio.sleep(0.1)
        return f"[IncidentHistoryTool Placeholder: Incident search not implemented.]"


# --- Web Search Tool Implementation ---
try:
    if settings.tavily_api_key:
        logger.info("Tavily API Key found, initializing WebSearchTool.")
        web_search_tool_instance = TavilySearchResults(max_results=3)
        # Using Tool factory function; name/description are args, not class attributes here
        WebSearchTool = Tool(
            name="WebSearchTool",
            func=web_search_tool_instance.invoke,
            coroutine=web_search_tool_instance.ainvoke,
            description=(
                "Use this tool ONLY for queries requiring real-time web search for external information, "
                "public service statuses, recent events, software versions, CVE details, or general knowledge "
                "not present in internal systems or documentation. Input should be a clear search query string."
            ),
        )
    else:
        logger.warning("TAVILY_API_KEY not found. WebSearchTool will be a placeholder.")
        class WebSearchToolPlaceholder(BaseTool):
            name: str = "WebSearchTool" # Added : str annotation
            description: str = "Web search tool (placeholder - API key missing)." # Added : str annotation
            # Added query parameter to match BaseTool structure expectation
            def _run(self, query: str, run_manager=None) -> str: return "[WebSearchTool Placeholder - API Key Missing]"
            async def _arun(self, query: str, run_manager=None) -> str: return "[WebSearchTool Placeholder - API Key Missing]"
        WebSearchTool = WebSearchToolPlaceholder()

except ImportError:
    logger.warning("Tavily libraries not found (`langchain-community`, `tavily-python`). WebSearchTool will be a placeholder.")
    class WebSearchToolPlaceholder(BaseTool): # Define placeholder class again here
        name: str = "WebSearchTool" # Added : str annotation
        description: str = "Web search tool (placeholder - libraries not installed)." # Added : str annotation
         # Added query parameter to match BaseTool structure expectation
        def _run(self, query: str, run_manager=None) -> str: return "[WebSearchTool Placeholder - Libraries Missing]"
        async def _arun(self, query: str, run_manager=None) -> str: return "[WebSearchTool Placeholder - Libraries Missing]"
    WebSearchTool = WebSearchToolPlaceholder() # Assign instance


# --- General Chat Tool (Fallback) ---
class GeneralChatTool(BaseTool):
    name: str = "GeneralChatTool"
    description: str = ("Use this tool as a fallback for general conversation, summarization requests, "
                   "or questions that can be answered based *only* on the conversation history "
                   "and previously uploaded data summaries. Do not use for specific data lookups "
                   "or external information gathering.")
    args_schema: Type[BaseModel] = GeneralChatToolInput

    def _run(
        self,
        query: str,
        session_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
    # --- END CORRECTION ---
        """Use the tool synchronously (Not Recommended)."""
        # As discussed, running the async logic reliably from sync is complex.
        # It's often better to indicate sync is not supported or raise an error.
        logger.warning("Synchronous execution of GeneralChatTool is not fully supported and may fail.")
        # Returning an error message is safer than complex asyncio.run logic here.
        return "Error: Synchronous execution not supported for GeneralChatTool. Use asynchronous invoke."

    async def _arun(
        self,
        query: str,
        session_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        # (Keep the corrected implementation of _arun from previous fix)
        logger.info(f"ASYNC Tool: GeneralChatTool called (Session: {session_id}, Query: {query[:50]}...)")
        try:
            memory = get_memory_for_session(session_id)
            if memory is None:
                logger.error(f"GeneralChatTool: Invalid session ID '{session_id}' provided.")
                return "Error: Invalid session context for general chat."

            data_list = get_data_for_session(session_id)

            # Ensure process_user_query is imported correctly if used here
            from app.chains import process_user_query # Or ensure top-level import

            response = await process_user_query(
                session_id=session_id,
                query=query,
                memory=memory,
                data_list=data_list
            )
            return response.answer
        except Exception as e:
            logger.error(f"Error during GeneralChatTool execution for session {session_id}: {e}", exc_info=True)
            return f"Error processing general chat query: {e}"
        

# --- Exportable List of Tools ---
tools_list = [
    LogSearchTool(),
    MetricQueryTool(),
    KnowledgeBaseSearchTool(),
    ConfigurationLookupTool(),
    IncidentHistoryTool(),
    WebSearchTool, # Use the instance created above (real or placeholder)
    GeneralChatTool(),
]