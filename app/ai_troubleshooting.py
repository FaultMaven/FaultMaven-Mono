"""
ai_troubleshooting.py - AI-Powered Troubleshooting Module

This module integrates:
- **LLM-based analysis** (OpenAI, Anthropic, Mistral, Hugging Face).
- **Structured troubleshooting workflows** for diagnosing issues.

Responsibilities:
1️⃣ **Synthesizes Query + Observability Insights**
   - Accepts **user queries** and **logs/metrics** for context-aware analysis.
   - Structures logs into a digestible format for the LLM.

2️⃣ **LLM-Based Troubleshooting**
   - Constructs structured prompts to guide AI for reliable, actionable output.
   - Routes queries dynamically to the configured LLM provider.

3️⃣ **Structured Response Processing**
   - Parses the LLM’s response into a structured format.
   - Extracts root cause hypotheses and next steps for actionability.
"""

import re
import json
from typing import Dict, List, Any, Optional
from app.logger import logger
from app.llm_provider import LLMProvider

def query_llm(prompt: str) -> Any:
    """Query the LLM."""
    try:
        return LLMProvider().query(prompt)
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        raise

def process_query(query: str) -> str:
    """Handles query-only requests."""
    try:
        response = query_llm(query)
        # Extract text from LLM response
        if isinstance(response, list) and response and isinstance(response[0], dict) and "generated_text" in response[0]:
            response_text = response[0]["generated_text"]
            # Extract root cause from the response
            cause_match = re.search(r"(?:Root Cause|Likely root cause):\s*(.+?)(?:\. Next Steps:|\n|$)", response_text, re.DOTALL)
            if cause_match:
                # Clean up the root cause text
                likely_cause = cause_match.group(1).strip().replace("**", "").strip()
                return likely_cause
            else:
                return "Unknown"
        else:
            logger.error(f"Unexpected LLM response format: {response}")
            return "Error: Unexpected LLM response format."
    except Exception as e:
        logger.error(f"LLM Query Failed: {e}")
        return f"Error: LLM query failed: {e}"

def process_query_with_logs(query: str, log_insights: Dict[str, Any]) -> Dict[str, Any]:
    """Handles query + logs requests."""
    try:
        # Construct structured prompt
        prompt = generate_troubleshooting_prompt(log_insights)

        # Query the LLM and parse the response
        response = query_llm(prompt)
        parsed_response = parse_llm_response(response)

        if not parsed_response["next_steps"]:
            logger.warning("⚠️ LLM response did not provide actionable next steps.")
            return {"error": "LLM response did not provide actionable next steps"}

        return parsed_response
    except Exception as e:
        logger.error(f"AI troubleshooting failed: {e}")
        return {"error": f"Error: AI troubleshooting failed: {e}"}

def generate_troubleshooting_prompt(analysis_results: Dict[str, Any]) -> str:
    """
    Converts structured log insights into a query-friendly format for the LLM.

    Args:
        analysis_results (dict): Insights from log analysis.

    Returns:
        str: A formatted troubleshooting prompt for the LLM.
    """
    log_summary = analysis_results.get("summary", "No detailed summary available")
    anomalies = analysis_results.get("anomalies", [])

    prompt = f"""
    You are a system troubleshooting assistant. Analyze the following logs
    and identify the most probable root causes and necessary next steps.

    **Log Summary:**
    {log_summary}

    **Detected Anomalies:**
    {', '.join(anomalies) if anomalies else 'No anomalies detected'}

    **Response Format (STRICT):**
    - **Root Cause:** <Brief description>
    - **Next Steps:**
      1. <Step 1>
      2. <Step 2>
      3. <Step 3> (Minimum 3 steps)

    **Example Response (Even without detailed information):**
    - **Root Cause:** General API connectivity issue
    - **Next Steps:**
      1. Check network connectivity.
      2. Review API service status.
      3. Examine recent deployment changes.

    Provide a response even if detailed log information is unavailable.
    """
    return prompt.strip()

def parse_llm_response(response: Any) -> Dict[str, Any]:
    """Parses the LLM response into structured troubleshooting steps."""
    if isinstance(response, list) and response and response[0].get("generated_text"):
        response_text = response[0].get("generated_text", "").strip()
    elif isinstance(response, str):
        response_text = response.strip()
    else:
        return {"likely_cause": "Unknown", "next_steps": ["No specific next steps provided."]}

    # Log the LLM response text for debugging
    logger.debug(f"LLM Response Text: {response_text}")

    # Try to parse as JSON first
    try:
        parsed_json = json.loads(response_text)
        if isinstance(parsed_json, dict) and "likely_cause" in parsed_json and "next_steps" in parsed_json:
            return parsed_json
    except json.JSONDecodeError:
        pass

    # Fallback to regex parsing
    cause_match = re.search(r"(?:Root Cause|Likely root cause):\s*(.+?)(?:\. Next Steps:|\n|$)", response_text, re.DOTALL)
    next_steps_match = re.findall(r"^\d+\.\s(.+)", response_text, re.MULTILINE)

    likely_cause = cause_match.group(1).strip() if cause_match else "Unknown"
    # Clean up the root cause text
    likely_cause = likely_cause.replace("**", "").strip()
    next_steps = next_steps_match or ["No specific next steps provided."]

    return {"likely_cause": likely_cause, "next_steps": next_steps}

# Future Implementation Placeholders
def retrieve_past_cases(issue_description: str) -> Dict[str, str]:
    """
    Placeholder for retrieving past troubleshooting cases.

    Args:
        issue_description (str): The current issue being diagnosed.

    Returns:
        dict: Relevant past cases (to be implemented).
    """
    return {"message": "Retrieving past cases is not implemented yet."}

def suggest_follow_up_questions(analysis_results: Dict[str, Any]) -> List[str]:
    """
    Placeholder for generating intelligent follow-up questions.

    Args:
        analysis_results (dict): Insights from log analysis.

    Returns:
        list: Suggested follow-up questions (to be implemented).
    """
    return ["What were the most recent configuration changes?", "Are there related alerts in the monitoring system?"]