# FaultMaven System Architecture

## 1. Overview
FaultMaven is an AI-powered troubleshooting assistant designed for SREs, DevOps, and engineers. It integrates with logs, metrics, and observability tools to assist in real-time issue diagnosis and resolution.

This document outlines the high-level architecture of FaultMaven, including design goals, system components, and deployment strategy.

## 2. Design Goals
FaultMaven is built with the following core principles:
- **Adaptability**: Supports evolving AI technologies and cloud environments.
- **Scalability**: Designed for enterprise-scale workloads with Kubernetes.
- **Modularity**: Built with a microservices approach for easier maintenance.
- **Performance**: Optimized for real-time troubleshooting.
- **Security**: Ensures data integrity, encryption, and secure API interactions.

## 3. High-Level Architecture
Below is a high-level system architecture diagram:

![System Architecture](diagrams/system-architecture.png)

### 3.1 Major Components

#### **1. User Interface (UI Layer)**
- **Browser Extension (React)**: Captures user interactions and sends them to the backend via API.
- **FastAPI Gateway**: Manages incoming requests and routes them to appropriate services.

#### **2. Core AI Processing**
- **Query Router**: Routes troubleshooting requests to relevant AI agents.
- **Log Analysis Service**: Processes structured and unstructured logs.
- **AI Agent (LangChain-based)**: Provides AI-powered troubleshooting and recommendations.

#### **3. Data Management**
- **Vector Database**: Stores troubleshooting context and knowledge base.
- **PostgreSQL**: Stores logs and structured metadata.

#### **4. Integrations**
- **API Adapters**: Connect FaultMaven to external observability tools (e.g., Splunk, Prometheus).

#### **5. Deployment**
- **Docker**: Containerized services.
- **Kubernetes**: Manages containerized applications for scalability and resilience.

## 4. Data Flow
1. **User triggers troubleshooting** via browser extension.
2. **FastAPI Gateway** routes the request.
3. **Query Router** determines if logs, metrics, or AI assistance is needed.
4. **Log Analysis Service** processes logs and provides insights.
5. **AI Agent** generates troubleshooting suggestions.
6. **User receives recommendations** on potential root causes and next steps.

## 5. Deployment Strategy
- FaultMaven runs as **containerized microservices** managed by Kubernetes.
- The **AI processing pipeline is scalable**, distributing workloads dynamically.
- **Observability integrations** allow seamless connection with enterprise monitoring tools.

---
_Last updated: 2025-02-21_
