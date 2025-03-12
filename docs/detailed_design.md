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

