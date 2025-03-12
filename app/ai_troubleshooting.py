"""
ai_troubleshooting.py - AI-Powered Troubleshooting Module

This module integrates LLM-based analysis with structured troubleshooting
workflows for diagnosing issues.
"""

import re
import json
from typing import Dict, List, Any, Optional
from app.logger import logger
from app.llm_provider import LLMProvider  # No need to import LLMParsingError anymore
from config.settings import settings
import html

def process_query(query: str, llm_provider: LLMProvider, context:  Optional[List[Dict[str, Any]]] = None) -> str:
    """Handles query-only requests."""
    prompt = generate_general_query_prompt(query, context)
    result = llm_provider.query(prompt)
    logger.info(f"LLM raw response: {result}") # Keep this for debugging.
    return format_llm_response(result)


def process_query_with_logs(query: str, log_insights_list: List[Dict[str, Any]], llm_provider: LLMProvider, context:  Optional[List[Dict[str, Any]]] = None) -> str:
    """Handles query + logs requests.  Returns formatted HTML."""
    prompt = generate_troubleshooting_prompt(query, log_insights_list, context)
    result = llm_provider.query(prompt)
    return format_llm_response(result)


def generate_troubleshooting_prompt(query: str, analysis_results_list: List[Dict[str, Any]], context: Optional[List[Dict[str, Any]]] = None) -> str:
    """Formats the troubleshooting prompt, handling multiple data submissions."""

    context_string = format_context_for_prompt(context) if context else ""
    data_summary = format_data_summary(analysis_results_list)

    prompt = settings.troubleshooting_prompt.format(
        user_query=query,
        data_summary=data_summary,
        context = context_string
    )
    return prompt

def generate_general_query_prompt(query: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
    """Formats the general query prompt, including conversation history."""
    context_string = format_context_for_prompt(context) if context else ""
    prompt = settings.general_query_prompt.format(query=query, context=context_string)
    return prompt

def format_context_for_prompt(context: List[Dict[str, Any]]) -> str:
    """Formats the conversation history for inclusion in the prompt."""
    formatted_context = ""
    for item in context:
        if item["role"] == "user":
            formatted_context += f"User: {item['content']}\n"
        elif item["role"] == "assistant":
            formatted_context += f"Assistant: {item['content']}\n"
    return formatted_context

def process_data_summary(log_insights: Dict[str, Any], llm_provider: LLMProvider) -> str:
    """Generates an LLM-powered summary of the log analysis results."""
    try:
         # Use the keys from log_insights directly, no need to extract individual fields
        log_data_string = format_log_data_for_summary(log_insights) # Format as string
        prompt = settings.log_summary_prompt.format(log_data=log_data_string) # Pass log data.
        result = llm_provider.query(prompt)
        if result:
            return result
        else:
            logger.error("LLM returned an empty response for data summary.")
            return "Error: LLM returned an empty response." # Consistent Error Message
    except Exception as e:
        logger.error(f"LLM data summary generation failed: {e}", exc_info=True)
        return "Error generating data summary."  # Consistent Error Message

def format_log_data_for_summary(log_insights: Dict[str, Any]) -> str:
    """Formats log insights into a string for the log_summary_prompt"""
    summary = log_insights.get("summary", "No detailed summary available.")
    anomalies = log_insights.get("anomalies", [])
    categorized_logs = log_insights.get("categorized_logs", {})
    metrics = log_insights.get("metrics", {})

    formatted_data = f"Log Summary: {summary}\n"
    if anomalies:
        formatted_data += "Detected Anomalies:\n" + "\n".join([f"  - {a}" for a in anomalies]) + "\n"
    if categorized_logs:
        formatted_data += "Categorized Logs (Counts):\n"
        for category, count in categorized_logs.items():
            formatted_data += f"  - {category}: {count}\n"
    if metrics:
        formatted_data += "Metrics (Averages):\n"
        for metric, value in metrics.items():
            formatted_data += f"  - {metric}: {value}\n"
    return formatted_data

def format_llm_response(response_text: str) -> str:
    """Formats the raw LLM response for display.  Handles JSON and plain text,
    including numbered and bulleted lists, and ensures paragraphs are
    correctly separated.
    """
    try:
        # Attempt to parse as JSON
        parsed_response = json.loads(response_text)
        # If it's JSON, format it nicely
        formatted_output = f"<p><strong>Answer:</strong> {parsed_response.get('answer', 'No answer provided.')}</p>"
        if parsed_response.get("action_items"):
            formatted_output += "<p><strong>Action Items:</strong></p><ul>"  # Use <ul>
            for item in parsed_response["action_items"]:
                formatted_output += f"<li>{html.escape(item)}</li>"  # Escape each item
            formatted_output += "</ul>"  # Use </ul>
        return formatted_output

    except json.JSONDecodeError:
        # If it's not JSON, do more advanced formatting
        response_text = html.escape(response_text)  # Always escape!

        paragraphs = response_text.split("\n\n")
        formatted_output = ""
        in_numbered_list = False  # Flag to track if we're inside a numbered list

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            lines = p.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for bullet points at the START OF THE LINE
                if line.startswith("-") or line.startswith("*"):
                    if in_numbered_list:  # Close <ol> if we were in a numbered list
                        formatted_output += "</ol>"
                        in_numbered_list = False
                    formatted_output += f"<ul><li>{line.lstrip('-* ')}</li></ul>"  # Wrap in <ul><li>

                # Check for numbered list at the START OF THE LINE
                elif re.match(r"^\s*\d+\.\s", line):
                    if not in_numbered_list:  # Start a new <ol> if needed
                        formatted_output += "<ol>"
                        in_numbered_list = True
                    formatted_output += f"<li>{line.lstrip('0123456789. ')}</li>"  # Add <li>

                else:  # Regular text (not a list item)
                    if in_numbered_list:  # Close <ol> if we were in a numbered list
                        formatted_output += "</ol>"
                        in_numbered_list = False
                    formatted_output += f"<p>{line}</p>"  # Wrap in <p>

            if in_numbered_list: # Close numbered list if the paragraph end.
                formatted_output += "</ol>"
                in_numbered_list = False

        return formatted_output