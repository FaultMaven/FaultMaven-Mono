# FaultMaven Core Design: Data Handling & User Interaction

This section outlines the fundamental ways FaultMaven receives, processes, and utilizes data, and how users interact with the system within a stateful session. The design aims to provide timely, relevant insights by combining specialized data processing with context-aware Large Language Model (LLM) reasoning.

## 1. Data Handling & Processing Workflow

FaultMaven is designed to ingest various types of data relevant to SRE/DevOps troubleshooting through multiple input formats. The core principle is to classify incoming data and route it to appropriate specialized processors to extract meaningful insights before making them available for conversational analysis.

### 1.1. Data Submission Formats

Users can submit data to the `/data` endpoint via the UI using:

- **Text Input**: Pasting raw text directly into the UI. The backend receives this as a simple string (`text: Form(...)`).
- **File Upload**: Selecting a local file. The backend receives an `UploadFile` object.
  - *Required Enhancement*: The backend needs logic to inspect `file.content_type` and `file.filename` to handle various formats (e.g., `.log`, `.txt`, `.json`, `.yaml`, potentially `.pdf`, `.docx`). Non-plain-text files require appropriate libraries (e.g., `pypdf2`, `python-docx`) to extract text content before further processing.
- **Browser Context (URL)**: Submitting context from the current browser page (where FaultMaven runs in a sidebar). This is not just a URL string but is expected to be structured data and metadata pushed from the frontend/extension, likely as a JSON payload.
  - *Required Enhancement*: The `/data` endpoint needs modification to accept an optional JSON body parameter representing this structured data. A Pydantic model should define this structure:

    ```python
    # Proposed Model (in app/models.py)
    class BrowserContextData(BaseModel):
        url: Optional[str] = None
        title: Optional[str] = None
        selected_text: Optional[str] = None
        page_content_snippet: Optional[str] = None # e.g., main text content extracted by frontend
        metadata: Optional[Dict[str, Any]] = None # Other relevant info (e.g., page structure)
    ```

The `/data` handler in `app/query_processing.py` must detect which input method was used (Context, File, or Text) to correctly receive and prepare the `data_content` string for classification.

### 1.2. Data Content Types & Classification

- **Purpose**: To understand what the submitted data represents, enabling routing to the correct specialized processing tool/method. Correct classification is key to generating relevant insights.
- **Mechanism**: The `app/data_classifier.py` module's `classify_data` function is responsible for this. It uses a hybrid approach:
  - Fast heuristics (regex, keyword checks) for common, structured formats.
  - Fallback to an LLM (`classifier_llm`) for ambiguous cases.
- **Target Categories** (`DataType` Enum in `app/models.py`): The classifier should output one of these types, chosen for their distinct processing needs:
  - `PROBLEM_STATEMENT`: Incident reports, user problem descriptions, Slack messages, RCAs. *(Processing: LLM Analysis/Summary)*
  - `SYSTEM_LOGS`: Syslog, application logs (text, JSON). *(Processing: Vector Tool + Programmatic Analysis + LLM Summary)*
  - `MONITORING_METRICS`: CSV, Prometheus format, JSON metrics. *(Processing: Metrics Library/Stats Analysis)*
  - `CONFIGURATION_DATA`: YAML, JSON, XML, `.properties`, Terraform files. *(Processing: Parser/Linter/Diff Tool)*
  - `SOURCE_CODE`: Code files (Python, Java, etc.), diffs. *(Processing: Code Analysis Tool / MCP Server?)*
  - `MCP`: Data specifically formatted for the external MCP server. *(Processing: MCP Server API Call)*
  - `TEXT`: Generic unstructured text not fitting other categories. *(Processing: LLM Analysis/Summary)*
  - `UNKNOWN`: Unclassifiable data, potentially binary. *(Processing: None)*
- *Required Updates*: The classifier's heuristics, LLM prompt, and output mapping need to be updated to support these specific `DataType` categories.

### 1.3. Specialized Data Processing

- **Purpose**: To transform raw data into structured insights or concise summaries tailored to the data type, providing richer context than raw snippets alone.
- **Workflow**: After classification, the `/data` endpoint in `app/query_processing.py` routes the data content (and potentially conversation history, see Section 2) to the corresponding asynchronous processing function:
  - `SYSTEM_LOGS` -> `app/log_metrics_analysis.process_logs_data` (Uses Vector, `analyze_logs`, `process_data_summary`) -> Returns `LogInsights` model.
  - `PROBLEM_STATEMENT` / `TEXT` -> `app/log_metrics_analysis.process_text_data` (Uses LLM via `text_analysis_chain`) -> Returns `Dict` with summary.
  - `MCP` -> `app/mcp_processor.process_mcp_data` (Calls external MCP server API) -> Returns `Dict` from server.
  - `SOURCE_CODE` -> `app/code_analyzer.process_source_code` (Placeholder - Could call MCP or other tools) -> Returns `Dict`.
  - `MONITORING_METRICS` -> `app/log_metrics_analysis.process_metrics_data` (Placeholder) -> Returns `Dict`.
  - `CONFIGURATION_DATA` -> `app/log_metrics_analysis.process_config_data` (Placeholder) -> Returns `Dict`.
  - `UNKNOWN` -> No specific processor called.
- **Output**: Each processor returns its findings (e.g., a `LogInsights` object, a dictionary containing a summary or structured data). These results are stored within an `UploadedData` object in the user's session.

## 2. User Interaction Model & Protocol

FaultMaven provides a conversational interface built upon stateful sessions.

### 2.1. Session Context

- **Stateful**: Interactions are tied to a `session_id`. State (conversation history + processed data insights) persists and accumulates throughout the session.
- **Components**: Handled by `app/session_management.py`, using `ConversationBufferMemory` for history and a list of `UploadedData` objects for data context.

### 2.2. User Actions & FaultMaven Responses

Users can interleave two main actions:

#### a) Submitting Data (`POST /data`)

- **Goal**: Add specific data context to the session.
- **Workflow**: As described in Section 1: Receive data (Text/File/Context) -> Retrieve Session/History -> Classify Type -> Call appropriate Context-Aware Processor (passing data and history) -> Store Results -> Return `DataInsightsResponse`.
- **Context-Aware Processing**: When conversation history exists, the processing functions (especially those using LLMs, like `process_data_summary` called by `process_logs_data`, or `process_text_data`) should attempt to analyze the new data in light of the recent conversation topics to provide more relevant immediate insights. If no relevant history exists, they perform a standalone analysis.
- **Response** (`DataInsightsResponse`): Immediately returns:
  - Processing status (Success/Failure).
  - Key insights/summary derived from the submitted data (contextualized where possible).
  - A clarification prompt: Actively asks the user what they want to do next or suggests relevant follow-up actions based on the insights found (e.g., "Processed logs: Found 5 errors. Should I analyze these errors further or correlate them with recent metrics?"). This makes the interaction more guided and considerate.

#### b) Asking Questions (`POST /query`)

- **Goal**: Ask conceptual questions or request analysis/troubleshooting based on the entire session context.
- **Workflow**: Receive Query -> Retrieve Session/History -> Retrieve all stored `UploadedData` (containing processed results) -> Format cumulative context (history + formatted processed data insights via `format_uploaded_data`) -> Call Main LLM Chain (`process_user_query`) -> Return `TroubleshootingResponse`.
- **Context**: Uses the full conversation history and the processed insights/summaries from all data submitted in the session so far. If no data was submitted, context is limited to history + base LLM knowledge. Accessing specific external knowledge (e.g., runbooks) requires future RAG implementation.
- **Response** (`TroubleshootingResponse`): Provides a context-aware answer and actionable steps, synthesized by the main chat LLM based on the comprehensive context provided. May ask clarifying questions if context or query is ambiguous (based on prompt engineering).

### 2.3. Interaction Protocol Summary

- Interactions are session-based and stateful.
- `/data` is for adding specific context: it processes data, stores results, and returns immediate, context-aware insights (where possible) along with a clarifying prompt for next steps.
- `/query` is for conversational reasoning: it uses the cumulative context (history + all processed data insights) to answer questions and provide troubleshooting guidance.
- The quality of context (derived from specialized processing via `/data`) is key to FaultMaven's ability to provide superior assistance compared to generic LLMs.