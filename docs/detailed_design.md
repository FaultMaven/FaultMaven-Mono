# FaultMaven Detailed Design Document

## 1. Introduction

### Purpose
This document provides an in-depth technical design for FaultMaven, detailing the implementation of each module, data structures, API specifications, processing workflows, error handling strategies, security measures, and testing strategies.

### Scope
FaultMaven is an AI-powered troubleshooting assistant that processes observability data and provides real-time, context-aware insights. This document covers:

- **Unified API & Query Handler**
- **Data Normalization Module**
- **Log & Metrics Analysis Module**
- **AI Troubleshooting Module**
- **Continuous Learning Module**
- **Observability & Monitoring Layer**
- **Security & CI/CD Strategy**

### Intended Audience
This document is intended for software engineers, architects, and developers involved in the implementation and maintenance of FaultMaven.

---

## 2. System Overview

### High-Level Architecture
FaultMaven consists of a **monolithic process** that handles all API requests from the web browser, processes observability data, and returns actionable troubleshooting insights. The key components are:

1. **Adaptive Query Handler** – Determines request type and routes it accordingly.
2. **Data Normalization Module** – Converts logs, metrics, and traces into a standardized format.
3. **Log & Metrics Analysis Module** – Extracts patterns and detects anomalies.
4. **AI Troubleshooting Module** – Generates troubleshooting recommendations using an LLM.
5. **Continuous Learning Module** – Adjusts recommendations based on user feedback.
6. **Observability & Monitoring Layer** – Logs API requests, tracks AI responses, and monitors system health.

### Technology Stack
- **Backend:** FastAPI (Python)
- **AI Processing:** OpenAI GPT-4 / PyLandicAI
- **Log Processing:** Elasticsearch, OpenSearch
- **Database:** PostgreSQL & Pinecone (Vector DB)
- **Monitoring & Tracing:** Prometheus, OpenTelemetry
- **Security:** OAuth2 Authentication, AES-256 Encryption
- **Deployment:** Docker, Kubernetes

---

## 3. User Interaction Flow

### Overview
FaultMaven’s troubleshooting workflow consists of six stages:

1. **User submits a troubleshooting request** (query-only, data-only, or both).
2. **API receives the request** and forwards it to the **Adaptive Query Handler**.
3. **Data Processing Modules analyze input** (logs, metrics, traces).
4. **AI Troubleshooting Module synthesizes results** and generates recommendations.
5. **User receives a structured response** with actionable insights.
6. **User feedback is collected** to refine recommendations (Continuous Learning Module).

### Sequence Diagram
```mermaid
sequenceDiagram
    participant User
    participant Web_UI
    participant API_Server
    participant Query_Handler
    participant Log_Metrics_Analysis
    participant AI_Troubleshooter
    participant Continuous_Learning

    User ->> Web_UI: Submit troubleshooting query (with or without data)
    Web_UI ->> API_Server: Send API request (query + logs/metrics)
    API_Server ->> Query_Handler: Process request type
    Query_Handler ->> Log_Metrics_Analysis: Analyze logs & metrics
    Query_Handler ->> AI_Troubleshooter: Generate troubleshooting insights
    AI_Troubleshooter ->> Continuous_Learning: Store user feedback & session learning
    AI_Troubleshooter ->> API_Server: Return recommendations
    API_Server ->> Web_UI: Display insights & next steps
    Web_UI ->> User: Show troubleshooting response
```

### Detailed Breakdown

#### **1. User Request Submission**
- User enters a troubleshooting query through the **FaultMaven web interface**.
- The user may optionally provide logs, monitoring data, or traces.

#### **2. API Processing**
- The **Unified API Server** receives the request.
- The **Adaptive Query Handler** determines whether the request is:
  - **Query-only** (text-based query with no logs/metrics).
  - **Data-only** (logs or metrics but no query).
  - **Query + Data** (both provided).

#### **3. Data Processing & Analysis**
- If observability data is provided, the **Log & Metrics Analysis Module** extracts patterns, anomalies, and correlations.

#### **4. AI Troubleshooting Module Execution**
- The AI model (GPT-4 via **PyLandicAI**) generates **context-aware troubleshooting guidance**.
- If **similar past issues exist**, relevant insights are retrieved from the **Vector Database**.

#### **5. Response Delivery**
- The system generates a **structured response** with:
  - **Suggested next steps** for troubleshooting.
  - **Contextual insights** from past cases.
  - **Potential root causes** based on log and metrics analysis.

#### **6. User Feedback & Continuous Learning**
- The **Continuous Learning Module** collects **user feedback** (accept/reject recommendations).
- This feedback is used **within the same session** to refine responses dynamically.

---

## 4. API Design & Endpoints

### 4.1 Unified API & Query Handler
Handles all requests from the web client.

- **Endpoint:** `/api/query`
- **Request Example (JSON)**
  ```json
  {
      "user_id": "user_001",
      "query": "Why is my server CPU usage spiking?",
      "logs": ["Error: CPU threshold exceeded at 90%"],
      "metrics": {"cpu_usage": 92, "memory_usage": 78}
  }
  ```
- **Response Example**
  ```json
  {
      "recommendations": [
          "Check active processes using top or htop.",
          "Investigate recent deployments for performance regressions."
      ]
  }
  ```

---

## 5. Component Design & Processing Logic

### 5.1 Adaptive Query Handler
- **Determines request type (query-only, data-only, or combined).**
- **Routes request to the appropriate processing module.**

### 5.2 Data Normalization Module
- **Converts all incoming data into a standardized format.**

### 5.3 Log & Metrics Analysis Module
- **Uses statistical and ML-based methods to detect anomalies.**

### 5.4 AI Troubleshooting Module
- **Retrieves context from the vector database.**
- **Uses an LLM (GPT-4 via PyLandicAI) to generate recommendations.**

### 5.5 Continuous Learning Module
- **Implements session-based learning using real-time feedback.**

---

## 6. Security & Access Control

### 6.1 Authentication & Authorization
- **OAuth2-based API Authentication** for secure user access.
- **Role-Based Access Control (RBAC)** to restrict access levels.

### 6.2 Data Encryption
- **AES-256 encryption** for stored log data.
- **TLS 1.2+ encryption** for API communication.

### 6.3 Logging & Auditing
- Secure audit logs to track **user actions and system events**.

---

## 7. CI/CD Pipeline & Testing Strategy

### 7.1 Automated Testing
- **Unit tests** for individual AI agents.
- **Integration tests** for API endpoints.
- **End-to-end tests** using **Postman or Pytest**.

### 7.2 CI/CD Workflow
- **GitHub Actions** for automated builds and deployments.
- **Kubernetes-managed containerized deployments**.

---

## 8. Future Enhancements

- **Multimodal Input Support:** Screenshots and configuration files.
- **LLM Fine-Tuning:** Training on real-world logs.
- **On-Prem Deployments:** Cloud and self-hosted options.

---

## 9. Conclusion

This document provides the detailed technical specifications for FaultMaven’s architecture and processing logic. It ensures that every user request is processed efficiently in real time via a unified backend, with intelligent, adaptive troubleshooting and session-based continuous learning.


# 
#
#
# ---------


update 3/8/2025

Note: This is an addition to the existing detailed design document. It clearly defines the expected behavior and interaction model of FaultMaven. It highlights the importance of session management and contextual prompting in achieving the desired conversational troubleshooting experience. It also clearly separates the responsibilities of the client and server, making the design more understandable.

## Communication Protocol and Core Design Principles

This section outlines the communication protocol between the user (via the browser extension) and the FaultMaven backend, as well as the core design principles that guide the application's behavior.

### User-FaultMaven Communication Protocol

FaultMaven is designed to facilitate a context-aware, conversational troubleshooting experience.  The following rules govern the interaction between the user and the system:

1.  **Domain Focus:** FaultMaven is specialized for Site Reliability Engineering (SRE), DevOps, system administration, cloud computing, and related technical troubleshooting tasks.  It is designed to provide assistance within this domain. While general questions *can* be asked, they are treated as context-setting for subsequent, more specific troubleshooting queries. FaultMaven may politely decline to answer questions that are clearly outside of its domain of expertise.

2.  **Alternating Data and Queries:** The user interacts with FaultMaven by submitting either *data* (logs, metrics, web page content) or *queries*. There are no restrictions on the order or timing of these submissions.  The user can:
    *   Submit data first, then ask questions about it.
    *   Ask a general question first, then provide data for more specific analysis.
    *   Submit multiple sets of data and ask questions related to any or all of them within the same conversation.
    *   Ask a series of related questions without re-submitting data.

3.  **Data Submission and Immediate Feedback:** When data is submitted to the `/data` endpoint, FaultMaven:
    *   Processes the data (parsing, analysis, anomaly detection).
    *   Stores the *processed results* (and a reference to the raw data, if needed) in the user's session.
    *   Returns an *immediate* summary of the analysis to the user (e.g., "Log analysis complete. Detected 4 errors and 2 warnings."). This provides quick feedback *before* the user formulates a specific query.

4.  **Contextual Query Handling:** When a query is submitted to the `/query` endpoint, FaultMaven:
    *   Retrieves the user's session, including the conversation history and *all* previously submitted data.
    *   If data is present in the session, the query is treated as a *troubleshooting* query.  FaultMaven uses the `troubleshooting_prompt` and includes the *entire* accumulated, processed data from the session as context for the LLM.
    *   If *no* data is present in the session, the query is treated as a *general* question. FaultMaven uses the `general_query_prompt`.
    *   The conversation history is *always* included in the prompt, allowing the LLM to maintain context.

5.  **Session Management:**
    *   FaultMaven uses server-side session management to maintain context across multiple interactions.
    *   A unique `session_id` (UUID) is used to identify each conversation.
    *   The client (browser extension) is responsible for storing the `session_id` and sending it with each request in the `X-Session-ID` HTTP header.
    *   The server stores session data (conversation history, processed data) associated with each `session_id`.
    *   Sessions have a timeout period (currently 30 minutes of inactivity), after which the session data is deleted.
    *   The client can explicitly start a new conversation, clearing the `session_id` and effectively resetting the context.

6.  **LLM Interaction:**

    *   FaultMaven acts as an intermediary between the user and the LLM.
    *   FaultMaven is designed to be LLM-agnostic, supporting multiple LLM providers through an abstraction layer (`LLMProvider`).
    *    The LLM is always called with a prompt that includes:
        *   The current user query.
        *   The formatted conversation history (if any).
        *   Relevant processed data (if any).
    *   FaultMaven expects a raw string response.

### Core Design Principles

1. **Transparency:** FaultMaven aims to be a "smart assistant," *enhancing* the user's interaction with the LLM, not replacing it. The raw LLM responses are made available.
2. **Context is King:** Maintaining conversation context is paramount.  The session management system and contextual prompting are designed to ensure the LLM has access to all relevant information.
3. **Data-Driven Troubleshooting:** FaultMaven's primary value comes from its ability to process and analyze system data (logs, metrics), providing context that a general-purpose LLM lacks.
4. **Flexibility:** The system is designed to be flexible and extensible, supporting multiple data types, LLM providers, and future enhancements (like LLM chaining).
5. **User Control:** The user is in control of the conversation. They can submit data or queries at any time, and they can start new conversations when needed.
6. **Stateless LLM, Stateful Faultmaven:** FaultMaven leverages *stateless* LLM API calls, while providing a *stateful* conversational experience through its own session management.
7. **Security**: All data submitted by users are considered sensitive.

# 
#
#
# ---------


update 3/12/2025

## Data Processing and Analysis

FaultMaven employs a hybrid approach to data processing, combining traditional parsing and analysis with the contextual understanding of Large Language Models (LLMs). This section details the data processing pipeline, from ingestion to LLM interaction, and outlines future enhancements.

### Current Approach: Hybrid Pre-processing and LLM Interaction

The current data processing workflow consists of the following steps:

1.  **Data Ingestion:** FaultMaven accepts user-provided data through the browser extension via three methods:
    *   **Text Input:** Raw text data (e.g., log snippets) pasted directly into a text area.
    *   **File Upload:** Log files in common formats (e.g., `.txt`, `.log`, `.json`, `.csv`).  Uploaded files are read and their content treated as text.
    *   **URL Input:** A URL pointing to a web page containing relevant information (e.g., an error page, monitoring dashboard). The content of the page is fetched and the relevant text extracted.

2.  **Data Type Identification:** The `/data` endpoint in `app/query_processing.py` identifies the data type based on user selection (for text/file/URL) and, for files, uses the `content-type` header for validation.

3.  **Initial Parsing and Transformation (Preprocessing):**
    *   **Text and File Data:**  The content is treated as a single string.  Basic encoding validation (UTF-8) is performed for files.
    *   **URL Data:** The content is fetched using the `aiohttp` library (asynchronously).  The `BeautifulSoup4` library is used to parse the HTML and extract the main text content, removing `<script>` and `<style>` tags to avoid analyzing irrelevant code.
    *   At this stage, *all* data types are represented as strings.

4.  **Log Processing (Fluentd - Subprocess):**
    *   **Execution:**  FaultMaven utilizes the open-source log processor **Fluentd**, running it as a *subprocess* within the FastAPI application.  This avoids external service dependencies.  The data string is piped to Fluentd's standard input.
    *   **Configuration (`fluent.conf`):** A Fluentd configuration file (`app/fluent.conf`) defines the parsing rules. This configuration:
        *   Uses the `stdin` input plugin.
        *   Employs the `parser` filter with the `@type multiline` option to handle log entries that span multiple lines.
        *   Uses the `format_firstline` and `format1` directives within the `parser` filter to define regular expressions for:
            *   Identifying the start of a new log entry (typically based on a timestamp pattern).
            *   Extracting key fields (timestamp, log level, message) from each log entry using named capture groups.  *This is a crucial step, and the regular expressions must be carefully crafted and maintained to match the expected log formats.*
        *   Outputs the parsed log entries to `stdout` in JSON format.
    *   **Error Handling:** Errors from the Fluentd subprocess are captured, logged, and result in an appropriate HTTP error response to the user.
    *   **Output:**  Fluentd's output (a stream of JSON objects, each representing a parsed log entry) is captured by the Python code.

5.  **Preliminary Analysis (`log_metrics_analysis.py`):**
    *   The `process_logs_data` function in `app/log_metrics_analysis.py` receives the parsed log entries (the JSON output from Fluentd) as a list of dictionaries.
    *   It performs initial data analysis *without* directly interacting with an LLM. This step includes:
        *   **Aggregation:** Counting log messages by log level (INFO, WARNING, ERROR, etc.).
        *   **Extraction:**  Extracting all error messages.
        *   **Basic Anomaly Detection:**  Implementing basic anomaly detection (e.g., detecting spikes in error rates).  This could be extended to include more sophisticated statistical methods.
        *   **Metric Extraction:** (If metrics are present in the logs and parsed by Fluentd) Extracting numerical metric values (e.g., CPU usage, memory usage, response time) and calculating basic statistics (e.g., average, minimum, maximum).
    *   The function returns a dictionary (`log_insights`) containing the structured analysis results.

6.  **LLM-Powered Summary Generation (`ai_troubleshooting.py`):**
    *   The `process_data_summary` function in `app/ai_troubleshooting.py` is called *after* `process_logs_data`.
    *   It takes the `log_insights` dictionary as input.
    *    It uses function `format_log_data_for_summary` to format `log_insights` data into string.
    *   It constructs a prompt for the LLM using the `log_summary_prompt` template (defined in `config/settings.py`).  This prompt instructs the LLM to generate a concise, human-readable summary of the log analysis findings.
    *   It calls the LLM (via the `llm_provider`) to generate the summary.
    *   It returns the LLM-generated summary string.

7.  **Session Storage:**
    *   The *raw* data content, the structured `log_insights` from `process_logs_data`, *and* the LLM-generated summary (`llm_summary`) are all stored within the user's session data.  This allows subsequent queries within the same session to access both the raw data, the structured analysis, *and* the LLM's interpretation of the data. All submitted data within a session is stored.
    *   Session data is stored in an in-memory dictionary (`sessions`) keyed by a unique `session_id` (UUID). This dictionary is managed using FastAPI's dependency injection system for thread safety and testability.
    *   Session data includes:
        *   `history`: A list of dictionaries, each representing a turn in the conversation (user query, LLM response).
        *   `data`: A *list* of dictionaries. Each element in the list stores information from *one* data submission within the session.  Each data object contains:
            *   `type`: The data type ("text", "file", or "url").
            *   `content`: The raw data content (string).
            *   `summary`: The structured `log_insights` dictionary from `process_logs_data`.
            *   `llm_summary`: The LLM-generated summary string.
        *   `last_activity`: A timestamp of the last user interaction, used for session timeout.

8.  **Query Handling with Context (`query_processing.py`):**
    *   The `handle_query` function in `query_processing.py` retrieves the session data.
    *   If the session contains previously submitted data (`session["data"]` is not empty), the `process_query_with_logs` function in `app/ai_troubleshooting.py` is called. This function:
        *   Formats all accumulated data summaries using `format_data_summary` in `app/ai_troubleshooting.py`, which iterates over data stored and create a combined string.
        *   Constructs a prompt using the `troubleshooting_prompt` template, including the user's query, the formatted data summary, and the conversation history.
        *   Calls the LLM.
        *   Formats LLM's output using `format_llm_response` in `app/ai_troubleshooting.py`.
    *   If the session contains *no* previously submitted data, the `process_query` function is called, using the `general_query_prompt`.

9. **Server response**:

  * The `/data` endpoint returns a `DataResponse`.
  * The `/query` endpoint returns a `QueryResponse`.

## Future Enhancements

This section details potential future improvements and additions to FaultMaven, building upon the core functionality.

1.  **Persistent Session Storage (Redis):**

    *   **Motivation:** The in-memory session storage is not persistent. Switching to Redis will provide persistent sessions across server restarts.
    *   **Implementation:** Replace the `sessions` dictionary with a Redis client. Serialize session data as JSON for storage in Redis. Implement session timeout using Redis's built-in expiration capabilities.

2.  **Advanced Log Parsing:**

    *   **Customizable Parsing Rules:** Allow users to define custom parsing rules for their specific log formats, potentially through a user interface.  This would involve providing a way for users to specify regular expressions or other parsing logic.
    *   **Log Format Detection:** Implement automatic log format detection, reducing the need for manual configuration. This could involve heuristics or machine learning techniques.
    *   **Log Aggregation Tools:** Explore integration with more advanced log aggregation tools like Loki, providing a more scalable solution for very large log volumes.

3.  **Enhanced Anomaly Detection:**

    *   **Sophisticated Algorithms:** Implement more advanced anomaly detection algorithms, going beyond simple thresholding.  This could include:
        *   Time series analysis techniques (e.g., moving averages, exponential smoothing).
        *   Machine learning models (e.g., clustering, anomaly detection algorithms).
    *   **Dynamic Thresholds:**  Adapt anomaly detection thresholds dynamically based on historical data patterns.
    *   **User-Defined Anomalies:** Allow users to define custom anomaly detection rules based on their specific needs and knowledge.

4.  **Expanded Metric Support:**

    *   **Wider Range of Metrics:** Handle a broader range of metrics beyond basic averages. Include percentiles, histograms, and other statistical measures.
    *   **Visualization:** Integrate basic metric visualization capabilities directly into the FaultMaven sidebar (e.g., simple time-series charts).

5.  **LLM Chaining:**

    *   **Multi-Step Reasoning:** Implement LLM chaining to break down complex troubleshooting tasks into smaller, more manageable steps. This involves making multiple sequential calls to LLMs, using the output of one call as input to the next.
    *   **Example Chain:**  A potential chain could involve: (1) Summarizing the logs, (2) Identifying potential root causes based on the summary, (3) Suggesting solutions based on the identified root cause, (4) Generating diagnostic commands.
    *   **Chain Definition:** Develop a mechanism for users to define and customize their own LLM chains (e.g., through a configuration file or a UI).

6.  **Knowledge Base Integration:**

    *   **Common Errors and Solutions:** Create a knowledge base of common errors and solutions, potentially integrating with external resources (e.g., Stack Overflow, documentation).
    *   **Proactive Suggestions:** Use the knowledge base to provide proactive suggestions to the user, even before they explicitly ask a question.
    *   **Augment LLM Responses:** Use the knowledge base to supplement and validate the LLM's responses.

7.  **Automated Remediation (Advanced):**

    *   **Suggestion:** Suggest specific commands or scripts that the user can run to fix the problem.
    *   **Execution (with User Confirmation):**  With *explicit* user confirmation and appropriate safeguards, potentially allow FaultMaven to *execute* remediation actions.  This requires very careful security considerations.

8.  **User Interface Enhancements:**

    *   **Improved Conversation Display:** Enhance the visual presentation of the conversation history.
    *   **Copy to Clipboard:** Add buttons to copy queries, responses, or entire conversations.
    *   **Data Source Selection:** Improve the UI for selecting the data source (text, file, URL).
    *   **Syntax Highlighting:** Add syntax highlighting for log data displayed in the sidebar.
     * **Collapsible sections:** Organize the data.

9.  **Collaboration Features:**

    *   **Shared Sessions:**  Allow multiple users to collaborate on the same troubleshooting session.
    *   **Commenting/Annotation:** Allow users to add comments and annotations to the conversation history.

10. **Specialized AI Model (Long-Term):**

    *   **Fine-tuning:** Fine-tune a pre-trained LLM on a large corpus of SRE/DevOps related data (logs, documentation, troubleshooting guides). This would improve the accuracy and relevance of the LLM's responses for troubleshooting tasks.
    *   **Custom Model Training:** Train a smaller, specialized model from scratch specifically for troubleshooting. This could be more efficient than using a large, general-purpose LLM.

11. **Feedback and Continuous Learning:**

    *   **User Feedback:** Collect user feedback on the usefulness of FaultMaven's responses.
    *   **Reinforcement Learning:**  Use reinforcement learning techniques to improve the LLM's performance over time based on user feedback.

12. **Integration with Other Tools:**

    *   **Monitoring Systems:** Integrate with monitoring systems (Prometheus, Grafana, etc.) to automatically pull in relevant metrics and logs.
    *   **CI/CD Pipelines:** Integrate with CI/CD pipelines to automatically collect data and trigger troubleshooting workflows.
    * **Ticketing System:**

This enhanced section provides a more structured and detailed roadmap for FaultMaven's future development, aligning with the core principles and addressing potential challenges.  It covers both immediate improvements and long-term goals. The focus remains on building a practical, user-friendly tool that leverages the power of LLMs for efficient troubleshooting, while acknowledging the limitations and complexities of such a system.



---
---
---
4/23/2025
# FaultMaven System Design

## 1. Introduction

FaultMaven is an AI-powered troubleshooting assistant designed for Site Reliability Engineers (SREs) and DevOps professionals. It aims to accelerate issue diagnosis and resolution by analyzing system data (logs, metrics, configuration, text) and providing contextual insights and actionable recommendations through a conversational interface.

This document outlines the internal architecture of the FaultMaven backend application, built primarily using Python with FastAPI and LangChain.

**Key Technologies:**

- **Backend Framework:** FastAPI  
- **Core AI/LLM Orchestration:** LangChain  
- **LLM Providers:** OpenAI API, Hugging Face Endpoints, Local ONNX Runtime (via custom wrapper), Ollama (potential)  
- **Data Structures:** Pydantic  
- **Specialized Tools:** Vector (for log parsing via subprocess)  
- **Configuration:** Pydantic-Settings (`.env` file)  

## 2. Core Design Principles & Development Focus

Based on the understanding that FaultMaven's ultimate capability is a combination of the underlying Language Model (LLM) chosen (P1) and the application's ability to provide relevant context and manage state (P2), the following principles guide the development effort:

### 2.1. Focus on Context, Processing, and Prompting
**Principle:** The primary engineering focus should be on building robust and intelligent mechanisms for session context management, specialized data processing, and sophisticated prompt engineering.  
**Rationale:** FaultMaven's unique value proposition and its ability to outperform generic LLMs stems directly from its capacity to augment a capable LLM with relevant, timely, and processed domain-specific context (P2).  
- **Specialized Data Processing:** (e.g., using vector for logs, analyzing metrics, processing MCP data) creates structured insights and summaries that provide far more signal than raw data alone.  
- **Context Management:** (conversation history, storage/retrieval of processed data results) ensures the LLM has the necessary information readily available (P2).  
- **Prompt Engineering:** Guides the LLM to effectively utilize this rich context, reason about SRE/DevOps problems, adhere to desired output structures (like TroubleshootingResponse), and potentially ask clarifying questions.  
While the underlying LLM's capability sets a performance ceiling (P1), the application framework surrounding it is where unique value and differentiation are engineered. The goal is to build a system that effectively leverages a sufficiently capable LLM.  
**Implementation:** This focus is reflected in modules like `app/session_management`, `app/data_classifier`, `app/log_metrics_analysis`, `app/mcp_processor`, and critically within `app/chains` where prompts, context formatting (`format_uploaded_data`), and core LLM orchestration (`process_user_query`) reside.

### 2.2. LLM Agnosticism and Flexibility
**Principle:** The architecture must support switching between different underlying LLM models and providers (e.g., OpenAI API, Hugging Face, local models via Ollama or custom wrappers) with minimal friction, ideally through configuration changes.  
**Rationale:** The LLM landscape is dynamic. Different models offer varying performance, cost, features, and deployment options (P1). To ensure FaultMaven remains adaptable and practical across different environments (cloud, on-premise, air-gapped) and budgets, it must not be tightly coupled to a single LLM provider or model.  
**Implementation:**  
- `config/settings.py`: Allowing selection of `chat_provider` and `classifier_provider`.  
- `app/llm_provider.py`: Abstracting the instantiation logic using the `_get_llm_instance` helper, which returns standardized LangChain objects (`BaseChatModel` or `LLM`) based on the configured provider.  
- **LangChain:** The framework itself provides standardized interfaces for interacting with different LLMs.

### 2.3. Leverage Modern, Effective Frameworks
**Principle:** Development should maximize the capabilities of chosen core frameworks: FastAPI, Pydantic, and LangChain.  
**Rationale:** Building robust, scalable, and maintainable AI applications requires leveraging well-designed foundations.  
- **FastAPI:** Provides a high-performance, async-native API layer well-suited for I/O-bound operations like external API calls (LLMs, MCP) and potentially streaming responses.  
- **Pydantic:** Ensures data validation and clear data structures throughout the application, crucial for reliable interactions between components and APIs.  
- **LangChain:** Offers essential abstractions and building blocks for LLM applications, including model integrations (supporting Principle 2), memory management (supporting P2), prompt templating, output parsing, and advanced features like Agents and Tool use (supporting Principle 4).  
Staying aligned with these active and growing ecosystems accelerates development and allows FaultMaven to benefit from new features and community support.  
**Implementation:** These frameworks form the backbone of the application structure (`query_processing`, `models`, `chains`, `llm_provider`, `session_management`).

### 2.4. Extensibility via Tool Integration
**Principle:** The design must be open and flexible, allowing straightforward integration of new specialized data processing tools or external data sources, with a view towards potential dynamic tool selection by the AI in the future.  
**Rationale:** FaultMaven's effectiveness as a specialized assistant hinges on its ability to go beyond generic text processing and interact with or analyze domain-specific data using appropriate methods (P2). This could involve parsing specific log formats (vector), querying monitoring systems (e.g., Prometheus via an API call), interacting with custom protocols (MCP), or retrieving information from internal knowledge bases (RAG). Designing for extensibility ensures FaultMaven can adapt to new tools and data sources over time. The concept of dynamic tool use via AI agents represents a significant pathway to enhanced capability.  
**Implementation:** The modular structure supports adding new processing modules (like `app/log_metrics_analysis.py`, `app/mcp_processor.py`). LangChain's "Tool" and "Agent" abstractions provide a clear framework for implementing dynamic tool usage in later development phases.

## 3. Architecture Overview

FaultMaven currently operates as a **monolithic application** with a modular design to facilitate future scaling and potential transition to microservices. The core is a FastAPI application that exposes HTTP endpoints for user interaction.

The application separates concerns into distinct Python modules within the `app` package:

- **API Layer:** Handles incoming HTTP requests, request validation, and orchestrates calls to underlying services/logic.  
- **Core Logic (Chains):** Encapsulates the main LangChain logic for processing user queries, managing prompts, interacting with the primary LLM, and parsing responses.  
- **LLM Abstraction:** Provides configured instances of LangChain LLM objects for different providers and different tasks.  
- **Session Management:** Manages user session state, including conversation history and uploaded/processed data (currently in memory).  
- **Data Handling:** Classifies and preprocesses uploaded data using heuristics, LLMs, or subprocess tools like Vector.  
- **Shared Models:** Pydantic models and Enums for request/response and internal data.  
- **Configuration & Utilities:** Pydantic-based config and application-wide logging.  

### Core Interaction Flows

1. **Data Submission (`/data`)**  
   Upload → Classify → Analyze → Summarize → Store

2. **Querying (`/query`)**  
   User query → Fetch session context → Prompt → Generate answer → Return response

## 4. System Diagram (Component Interactions)

```mermaid
graph TD
    %% User Interaction Section
    subgraph User_Interaction
        User -- HTTP Request --> FMApi
        User -- Data Files --> FMApi
    end

    %% External Services Section
    subgraph External_Services
        CloudLLM[Cloud LLMs: OpenAI, HF]
        LocalPhi3[Local Phi-3 Server: phi3_server.py]
        Vector[Vector Tool: subprocess]
        MCPServer[MCP Server: HTTP]
    end

    %% FaultMaven App Section
    subgraph FaultMaven_App
        FMApi["app/query_processing.py\nFastAPI App / Endpoints"] -- Uses --> SessionMgmt
        FMApi -- Calls --> Classifier
        FMApi -- Calls --> Processors
        FMApi -- Calls --> Chains

        Classifier["app/data_classifier.py\nHeuristics + LLM Classifier"] -- Uses --> LLMProvider[classifier_llm]
        Classifier -- Uses --> Models

        Processors["app/log_metrics_analysis.py\napp/mcp_processor.py\n..."] -- Calls --> Vector
        Processors -- Calls --> MCPServer
        Processors -- Uses --> LLMProvider[llm for summary]
        Processors -- Uses --> Models

        Chains["app/chains.py\nCore Query Logic / Chain"] -- Uses --> LLMProvider[llm]
        Chains -- Uses --> SessionMgmt[Memory]
        Chains -- Uses --> Models

        LLMProvider["app/llm_provider.py\nLLM Instances / Wrappers"] -- Calls --> CloudLLM
        LLMProvider -- Calls --> LocalPhi3

        SessionMgmt["app/session_management.py\nMemory + Data Store"] -- Manages --> InMemoryStores["In-Memory Dicts:\nHistory + Processed Data"]
        SessionMgmt -- Uses --> Models

        Models["app/models.py\nPydantic Models / Enums"]

        Config["config/settings.py\nConfiguration"]
        Logger["app/logger.py\nLogging"]

        FMApi -- Uses --> Config
        FMApi -- Uses --> Logger
        Chains -- Uses --> Logger
        SessionMgmt -- Uses --> Config
        SessionMgmt -- Uses --> Logger
        LLMProvider -- Uses --> Config
        LLMProvider -- Uses --> Logger
        Classifier -- Uses --> Logger
        Processors -- Uses --> Config
        Processors -- Uses --> Logger
    end

    %% Node Styling
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style CloudLLM fill:#ccf,stroke:#333,stroke-width:1px
    style LocalPhi3 fill:#ccf,stroke:#333,stroke-width:1px
    style Vector fill:#ccf,stroke:#333,stroke-width:1px
    style MCPServer fill:#ccf,stroke:#333,stroke-width:1px
    style InMemoryStores fill:#ff9,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
```

## 5. Module Descriptions

Each module's responsibilities and key dependencies:

- **app/query_processing.py**: Handles HTTP endpoints. Calls `session_management`, `data_classifier`, and `chains`.  
- **app/chains.py**: Builds LangChain prompts using memory and session context.  
- **app/llm_provider.py**: Configures LangChain `llm` and `classifier_llm` instances.  
- **app/session_management.py**: Tracks conversation history and uploaded content.  
- **app/data_classifier.py**: Applies heuristics or LLMs to identify data types.  
- **app/log_metrics_analysis.py**: Uses external tools (e.g., Vector) to analyze logs.  
- **app/mcp_processor.py** *(planned)*: Sends data to an external MCP server and returns results.  
- **app/models.py**: Central repository of Pydantic models and enums.  
- **config/settings.py**: Loads environment config using Pydantic.  
- **app/logger.py**: Central logging configuration.  
- **app/main.py**: Entrypoint for Uvicorn server execution.  

## 6. Interaction Flows

### 6.1 Data Submission (POST `/data`)

1. User sends a file or text.
2. Server classifies data type using `data_classifier.classify_data()`.
3. Based on the type:
   - Logs → `log_metrics_analysis.process_logs_data()`
   - RCA → `mcp_processor.process_mcp_data()`
   - Text → `log_metrics_analysis.process_text_data()`
4. `UploadedData` created and stored in session.
5. Response returned to user with summary.

### 6.2 Querying (POST `/query`)

1. User sends a query with session ID.
2. Session memory and processed data are loaded.
3. LangChain chain is invoked with context.
4. Answer and suggestions returned to the user.

## 7. Configuration

- Uses `.env` file and environment variables.
- Managed via `config/settings.py`.
- Includes settings for:
  - LLM providers (OpenAI, Ollama)
  - API keys
  - Timeout and thresholds

## 8. Future Considerations

- Migrate from in-memory to Redis or DB for state persistence.
- Break into microservices (SessionService, ChainService, etc.).
- Add LangChain agents for more interactive automation.
- Improve error handling and external call resilience.
- Add observability: metrics, logs, structured traces.

## 9. Conclusion

FaultMaven uses a modular FastAPI and LangChain architecture to analyze system data and support DevOps workflows. Its in-memory stateful design is sufficient for prototyping but is structured to evolve into scalable microservices. The AI assistant integrates classification, analysis, memory, and LLM prompt composition to provide highly contextual answers for incident resolution.


---
---
---
4/25/2025
## Data Submission Formats (Text, File, URL)

### Requirement:
The backend (`/data` endpoint) needs to handle data submitted in three distinct ways from the UI.

### Analysis & Design Impact:

#### 1. **Text (Form data):**
- **Implementation:** Matches the current implementation (`text: Optional[str] = Form(None)`).
- **Backend Behavior:** The backend receives a simple string.  
- **Status:** Covered.

#### 2. **File (UploadFile):**
- **Implementation:** Matches the current implementation (`file: Optional[UploadFile] = File(None)`).
- **Backend Behavior:** The backend receives a file object.  
- **Improvement Needed:**  
  - Currently, the code assumes the file is UTF-8 text (`contents.decode("utf-8")`).
  - To handle various file types (PDF, Word, potentially images later?), the `/data` endpoint logic needs to be enhanced:
    - Inspect `file.content_type` or `file.filename` extension.
    - Use appropriate libraries (`pypdf2`, `python-docx`, etc.) to extract relevant text content or structured data.
    - Temporarily save the raw file if needed.

#### 3. **URL (Browser Context - New Requirement):**
- **Implementation:** A new requirement significantly different from the other formats.
- **Backend Behavior:** This is "dynamically delivered as structured data and metadata."
  - Likely involves a browser extension or client-side script packaging context (DOM elements, metadata, selected text) as a JSON object and sending it.
- **Design Implications:**  
  - Handle the structured JSON data in the `/data` endpoint.
  - Ensure seamless classification/processing integration using this context.

---

## Data Content Types & Processing

### Requirement:
Classify content into specific categories (Problem Statements, Logs, Metrics, Configs, Source Code) to enable correct processing and contextual understanding.

### Refined Data Types and Processing:
Based on your input (problem statements, logs, metrics, configs, source code, potential MCP data) and the goal of routing to specific processing:

#### **DataType.PROBLEM_STATEMENT** *(Replaces ROOT_CAUSE_ANALYSIS)*  
**Input Examples:**  
Slack messages, incident tickets/reports, user descriptions of issues, RCA documents.  

**Processing Goal:**  
Extract key entities, summarize the issue, identify stated impact or actions already taken.  

**Method:**  
Primarily LLM-based analysis. Use `process_text_data` (or a new dedicated `process_problem_statement` function using a tailored LLM chain) in `app/log_metrics_analysis.py`.  

**Result Stored:**  
Dictionary with summary, extracted entities, etc.  
Example: `{"summary": "...", "entities": [...]}`  

---

#### **DataType.SYSTEM_LOGS** *(Was log)*  
**Input Examples:**  
Syslog, application logs (JSON, plain text).  

**Processing Goal:**  
Parse structure, count severities, extract errors/anomalies, calculate basic metrics, generate LLM summary.  

**Method:**  
External tool (vector) + programmatic analysis + LLM summary. Use `process_logs_data` in `app/log_metrics_analysis.py`.  

**Result Stored:**  
LogInsights Pydantic model.  

---

#### **DataType.MONITORING_METRICS** *(Was metric)*  
**Input Examples:**  
CSV files, Prometheus exposition format text, JSON metrics.  

**Processing Goal:**  
Parse metrics, calculate key statistics (avg, min, max, rate), potentially identify statistical outliers or trends.  

**Method:**  
Placeholder `process_metrics_data` in `app/log_metrics_analysis.py`. Would likely use libraries like pandas or specific parsers depending on format. Could involve basic statistical analysis or anomaly detection algorithms.  

**Result Stored:**  
Dictionary with statistics.  
Example: `{"avg_latency": 150.5, "error_rate": 0.05}`  

---

#### **DataType.CONFIGURATION_DATA** *(Was config)*  
**Input Examples:**  
YAML, JSON, XML, `.properties`, Terraform files.  

**Processing Goal:**  
Validate syntax, extract key parameters, potentially compare against known good configurations or check for security issues.  

**Method:**  
Placeholder `process_config_data` in `app/log_metrics_analysis.py`. Would use appropriate parsers (PyYAML, json, xml.etree.ElementTree) and potentially linters or comparison logic.  

**Result Stored:**  
Dictionary with extracted info or validation results.  
Example: `{"valid_syntax": true, "key_params": {...}}`  

---

#### **DataType.SOURCE_CODE** *(New)*  
**Input Examples:**  
Python, Java, Go files, shell scripts, potentially diffs or pull requests.  

**Processing Goal:**  
Identify language, summarize functions/classes, potentially lint or identify code smells, or interact with a specialized tool like your MCP server if it analyzes code.  

**Method:**  
Requires a new placeholder `process_source_code` (e.g., in a new `app/code_analyzer.py`). This could call the MCP server API, use basic regex, use libraries like tree-sitter for parsing, or use an LLM for summarization.  

**Result Stored:**  
Dictionary with analysis results.  
Example: `{"language": "python", "summary": "Contains 3 functions...", "mcp_result": {...}}`  

---

#### **DataType.MCP** *(Kept, for data specifically meant for MCP if not source code)*  
**Input Examples:**  
Data formatted specifically for your MCP tool/server that isn't classified as source code.  

**Processing Goal:**  
Get processed results directly from the MCP server.  

**Method:**  
Use `process_mcp_data` in `app/mcp_processor.py` to call the MCP server API.  

**Result Stored:**  
Dictionary containing the response from the MCP server.  

---

#### **DataType.TEXT** *(Generic Fallback)*  
**Input Examples:**  
Plain text that doesn't fit other categories.  

**Processing Goal:**  
Provide a general summary or topic extraction.  

**Method:**  
Use `process_text_data` (LLM-based) in `app/log_metrics_analysis.py`.  

**Result Stored:**  
Dictionary with summary.  
Example: `{"summary": "..."}`  

---

#### **DataType.UNKNOWN**  
**Input Examples:**  
Binary files (if not parsed), unclassifiable text.  

**Processing Goal:**  
None.  

**Method:**  
No processing function called by `/data` endpoint.  

**Result Stored:**  
None or maybe `{"error": "Cannot process unknown data type"}`  

---

### Summary & Next Steps

This refined list of `DataType` values seems appropriate for routing data to different processing methods. The names are clearer (`PROBLEM_STATEMENT`, `SYSTEM_LOGS`, etc.) and we've added `SOURCE_CODE`.

**Next Steps:**
1. Update the `DataType` Enum in `app/models.py`.  
2. Update the classifier (`app/data_classifier.py`) to recognize and output these types.  
3. Ensure the `/data` endpoint in `app/query_processing.py` has the corresponding `elif classified_type == DataType.X:` blocks to call the correct processing function (implementing placeholders like `process_source_code` as needed).



## Data processing by Faultmaven

FaultMaven will deliver accurate, on-demand problem diagnosis while evolving over time to offer rich, knowledge-backed solutions—adapting to both immediate needs and long-term troubleshooting guidance. The dynamic problem diagnosis feature will be the primary offering at launch, while the knowledge base will be added later as the platform gains traction. Both features involve intensive data processing, but there are fundamental differences between them.

### 1. Real-Time Problem Diagnosis (Dynamic Data Processing)

- **Data Source & Timing:**  
  Data is submitted directly from the frontend. Examples include logs, error messages, or detailed descriptions that users provide during troubleshooting.
  
- **Purpose & Workflow:**  
  The system processes this unstructured data on the fly to extract critical details that inform the problem context. This enriched, dynamic input is then passed to the LLM, which interprets it to diagnose the issue in near real time.
  
- **LLM Role:**  
  The LLM acts on the enriched query by analyzing the immediate problem scenario, thereby generating rapid and actionable insights.
  
- **Impact:**  
  Enables quick, on-demand diagnosis essential for resolving immediate troubleshooting issues.

### 2. Knowledge-Backed Solutions (Preprocessed Knowledge Base)

- **Data Source & Timing:**  
  Data is collected from backend sources, processed, and curated in advance. The preprocessed set includes documented procedures, guidelines, and other relevant knowledge assets.
  
- **Purpose & Workflow:**  
  This pre-curated data forms a structured knowledge database. When a troubleshooting query is made, the system retrieves the relevant curated context and the LLM uses it to assemble a comprehensive, knowledge-backed solution.
  
- **LLM Role:**  
  The LLM synthesizes the retrieved, validated data to construct a coherent and informed answer that aligns with established guidelines.
  
- **Impact:**  
  Provides solutions that are not only accurate but also grounded in a repository of validated information, supporting long-term troubleshooting strategies.

### Comparative Analysis

- **Timing of Data Processing:**  
  - **Dynamic Diagnosis:** Data is processed in real time as it becomes available from the user.
  - **Knowledge Base Solutions:** Data is processed in advance, indexed, and stored for efficient retrieval when needed.

- **Role of Data in the Query:**  
  - **Dynamic Scenario:** The data is an integral part of the question, requiring the LLM to interpret and diagnose issues from raw, unstructured inputs.
  - **Preprocessed Scenario:** The data forms the foundation of the answer, guiding the LLM to synthesize a response using established knowledge.

- **System Design Implications:**  
  - **Real-Time Problem Diagnosis:** Demands robust real-time parsing, extraction, and summarization mechanisms to handle on-the-fly data.
  - **Knowledge-Backed Solutions:** Relies on backend preprocessing, indexing, and retrieval strategies to ensure the quality and consistency of the knowledge base.

### Implementation Differences

- **Timing:**  
  - *On-Demand:* Data for real-time problem diagnosis is processed immediately as it is submitted.  
  - *Pre-Built:* Data for the knowledge-based solution is preprocessed and compiled in advance.

- **Storage Period:**  
  - *Short-Term & Transient:* For dynamic inputs, data is temporarily cached to support immediate analysis and then discarded.  
  - *Long-Term & Persistent:* For the knowledge base, data is stored persistently in a database to support ongoing troubleshooting efforts.

- **Storage Media:**  
  - *Cache:* Used to hold dynamic, real-time data for quick access during immediate problem diagnosis.  
  - *Database:* Utilized for storing preprocessed, curated information that forms the foundation for long-term solutions.

- **Processing Tools:**  
  - *Specialized Tools:* For dynamic data, various processing tools (e.g., log processing tools, real-time stream analyzers) handle unstructured inputs.  
  - *Batch & Popular Tools:* For the knowledge base, standard batch-processing tools and data pipelines are employed to index and process large volumes of structured documents.

- **Data Sourcing:**  
  - *Frontend:* Dynamic data is sourced directly from user inputs, such as file uploads or form submissions.  
  - *Backend:* Preprocessed data is acquired from external sources via URLs or direct file uploads through backend systems.

- **Data Uploading:**  
  - *Single Submission:* Real-time diagnosis typically involves uploading a single page or file to be processed immediately.  
  - *Batch Job:* The knowledge base is built through batch jobs that process multiple files or data streams over time.


### Conclusion

FaultMaven’s dual approach is designed to balance agility with precision. Initially, the focus will be on dynamic, real-time problem diagnosis—leveraging live data processing to quickly interpret and resolve issues. Over time, as FaultMaven gains traction, it will evolve to incorporate a comprehensive, preprocessed knowledge base that supports the formulation of rich, informed solutions. Although both features rely on sophisticated data processing, they differ fundamentally in when data is processed, how it is used by the LLM, and the overall design strategy they require.
