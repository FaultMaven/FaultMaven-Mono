# FaultMaven System Architecture

## 1. Overview

FaultMaven is an AI-powered troubleshooting assistant designed exclusively for Engineers, SREs, and DevOps professionals. Users access FaultMaven solely via a web browser. The system processes observability data—including logs, metrics, traces, configuration files, and source code snippets—uploaded as part of a single API call. FaultMaven provides real-time, adaptive troubleshooting guidance and leverages stateful context for intelligent recommendations, all while preserving user privacy by not storing raw user data long term.

## 2. Design Goals

FaultMaven is engineered with the following core principles in mind:

- **Browser-Centric Access:**  
  All interactions occur through a web browser, with all data provided via a single API call containing both query text and any uploaded data.

- **Flexibility & Adaptability:**  
  The system processes data from various sources and formats without enforcing strict external integrations. Data is normalized and processed on the fly.

- **Real-Time & Historical Analysis:**  
  Troubleshooting is performed on demand, using the same AI-driven approach whether the issue is currently impacting production or is being analyzed retrospectively.

- **Modularity & Extensibility:**  
  While currently implemented as a monolithic process (to simplify development and deployment), the system is designed modularly so that components can later be split into separate services if needed.

- **Scalability & Performance:**  
  Containerization and orchestration (using Docker and Kubernetes) ensure that FaultMaven can handle high data volumes with low latency.

- **Security & Compliance:**  
  Secure data transmission, encryption, role-based access control (RBAC), and audit logging are integral to the design.

- **Ephemeral Continuous Learning:**  
  The system leverages lightweight, session-based learning to adjust recommendations on the fly without retaining long-term user data.

## 3. High-Level Architecture

All user interactions occur through a web browser. The Unified API Server (monolithic backend) processes the API request, which includes both the user’s query and any attached data. The request is then handled by several internal modules responsible for adaptive query handling, data normalization, log analysis, AI-driven troubleshooting, and continuous learning. Stateful context is provided by external databases.

Below is the enhanced Mermaid diagram with indicative icons:

![System Architecture](diagrams/system_architecture.png)


# 4. Detailed Module Descriptions

## 4.1 Adaptive Query Handler

**Function:**  
Receives every API call from the web browser and analyzes the incoming request to determine its type (query-only, data-only, or combined).

**Responsibilities:**  
- Parsing the query text using NLP techniques.  
- Detecting and extracting any attached observability data.  
- Routing the request internally to the appropriate modules for further processing.

**Implementation Hints:**  
- Leverage libraries like Hugging Face Transformers or spaCy for intent recognition.

**Deployment:**  
- Runs as part of the Unified API Server within the same process.

---

## 4.2 Data Normalization Module

**Function:**  
Preprocesses and normalizes any data attached to the request.

**Responsibilities:**  
- Parsing logs, metrics, and other data formats.  
- Cleaning and converting raw data into a standardized format for analysis.

**Implementation Hints:**  
- Utilize standard parsing libraries and custom scripts to handle various data formats.

**Deployment:**  
- Embedded within the Unified API Server for seamless integration.

---

## 4.3 Log & Metrics Analysis Module

**Function:**  
Processes the normalized observability data to extract key patterns, trends, anomalies, and correlations.

**Responsibilities:**  
- Analyzing structured and unstructured data using statistical and machine learning methods.  
- Summarizing insights for further troubleshooting.

**Implementation Hints:**  
- Incorporate anomaly detection algorithms (e.g., Isolation Forest, One-Class SVM) and use tools like Elasticsearch for log processing if needed.

**Deployment:**  
- A dedicated module within the Unified API Server that communicates with the AI Troubleshooting Module via in-process calls.

---

## 4.4 AI Troubleshooting Module

**Function:**  
Generates actionable, context-aware troubleshooting recommendations.

**Responsibilities:**  
- Synthesizing input from the Adaptive Query Handler and insights from the Log & Metrics Analysis Module.  
- Utilizing an LLM (e.g., GPT-3/4 or an open-source alternative) to produce natural language guidance.  
- Retrieving additional context from stateful storage (Vector and Relational Databases).

**Implementation Hints:**  
- Use prompt engineering techniques with pre-trained LLMs, and integrate historical context stored in the databases.

**Deployment:**  
- Runs as part of the Unified API Server, interfacing with external databases for stateful context.

---

## 4.5 Continuous Learning Module

**Function:**  
Implements ephemeral, session-based learning to refine AI recommendations during active troubleshooting.

**Responsibilities:**  
- Collecting immediate user feedback and incident outcomes from the current session.  
- Adjusting recommendation parameters (e.g., confidence scores, ranking of suggested steps) based on this feedback.  
- Operating without storing long-term user data.

**Implementation Hints:**  
- Employ lightweight online learning or heuristic-based adjustments.

**Deployment:**  
- Integrated within the Unified API Server to allow real-time feedback loops with the AI Troubleshooting Module.

---

# 5. Data Flow Overview

1. **User Interaction:**  
   The user submits a troubleshooting query along with any associated data through the Web UI/Browser Extension.
2. **API Request Handling:**  
   The Unified API Server receives the API call, where the Adaptive Query Handler parses the request.
3. **Data Normalization:**  
   The Data Normalization Module preprocesses the attached data to ensure it is in a standardized format.
4. **Data Analysis:**  
   The normalized data is routed to the Log & Metrics Analysis Module, which extracts insights and detects anomalies.
5. **Troubleshooting Recommendations:**  
   The Adaptive Query Handler consolidates the query context and analysis output, then passes it to the AI Troubleshooting Module. This module generates actionable troubleshooting guidance using both immediate data and additional stateful context.
6. **Continuous Learning:**  
   Feedback from the user (e.g., confirmations, corrections, or further clarifications) is processed by the Continuous Learning Module to adjust recommendations in real time.
7. **Response Delivery:**  
   The final recommendations and insights are sent back to the user via the web browser.

---

# 6. Deployment Strategy

- **Containerization & Orchestration:**  
  FaultMaven is containerized using Docker and orchestrated with Kubernetes to ensure scalability, fault tolerance, and ease of deployment.

- **Monolithic Approach (Initial Deployment):**  
  All core modules (Adaptive Query Handler, Data Normalization Module, Log & Metrics Analysis Module, AI Troubleshooting Module, and Continuous Learning Module) run as a single process within one container to simplify the architecture and reduce inter-process communication overhead.

- **Future Scalability:**  
  The design is modular enough to allow splitting components into separate services if higher load or specialized scalability becomes necessary.

---

This document serves as the foundation for designing and developing FaultMaven. It ensures that every user request is processed efficiently in real time via a unified backend, with intelligent, adaptive troubleshooting and session-based continuous learning, all deployed securely and scalably.