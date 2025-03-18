"""
ai_troubleshooting.py - AI-Powered Troubleshooting Module

Integrates LLM-based analysis with structured troubleshooting workflows.
"""

import re
import json
from typing import Dict, List, Any, Optional, Union
from app.logger import logger
from app.llm_provider import LLMProvider
from config.settings import settings
import html
from app.log_metrics_analysis import LogInsights

def process_query(query: str, llm_provider: LLMProvider, context:  Optional[List[Dict[str, Any]]] = None) -> str:
    """Handles query-only requests, returning formatted HTML."""
    prompt = generate_general_query_prompt(query, context)
    result = llm_provider.query(prompt)
    logger.info(f"LLM raw response (query-only): {result}")  # Log raw response
    return format_llm_response(result)  # Format the response

def process_query_with_logs(query: str, session_data_list: List[Dict[str, Any]], llm_provider: LLMProvider, context:  Optional[List[Dict[str, Any]]] = None) -> str:
    """Handles query + logs requests.  Returns formatted HTML."""
    prompt = generate_troubleshooting_prompt(query, session_data_list, context)
    logger.info(f"Prompt: {prompt}") # Log out prompt
    result = llm_provider.query(prompt)
    logger.info(f"LLM raw response (with logs): {result}") # Log raw response
    return format_llm_response(result) # Format result

def generate_troubleshooting_prompt(query: str, session_data_list: List[Dict[str, Any]], context: Optional[List[Dict[str, Any]]] = None) -> str:
    """Formats the troubleshooting prompt, handling multiple data submissions."""

    context_string = format_context_for_prompt(context) if context else ""
    data_summary = format_data_summary(session_data_list)  # Pass the session data

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


def format_data_summary(session_data_list: List[Dict[str, Any]]) -> str:
    """Formats data from multiple log submissions into a single string for the prompt."""
    all_summaries = ""
    for session_entry in session_data_list:
        data_type = session_entry.get('type', 'Unknown')  # Use type
        content = session_entry.get('content', '')
        llm_summary = session_entry.get('llm_summary', "No detailed summary available.")

        all_summaries += f"- Data Type: {data_type}\n"
        all_summaries += f"  - Summary: {llm_summary}\n"

        # Include log-specific details if available and relevant
        if data_type == "log":  # Check the *original* data type
            log_insights = session_entry.get('summary', {})  # Safely get insights
            if log_insights:  # Check if insights exist
                anomalies = log_insights.get("anomalies", [])
                if anomalies:
                    all_summaries += "  - Detected Anomalies:\n"
                    for anomaly in anomalies:
                        all_summaries += f"    - {anomaly}\n"

                level_counts = log_insights.get("level_counts", {})
                if level_counts:
                    all_summaries += "  - Categorized Logs (Counts):\n"
                    for category, count in level_counts.items():
                        all_summaries += f"    - {category}: {count}\n"

                metrics = log_insights.get("metrics", {})
                if metrics:
                    all_summaries += "  - Metrics (Averages):\n"
                    for metric, value in metrics.items():
                        all_summaries += f"    - {metric}: {value}\n"
        elif data_type == 'text':
            all_summaries += f" - Text data: {content[:100]}...\n" # show a snippet

    return all_summaries.strip()  # Remove trailing whitespace


# --- Helper functions for formatting ---
def sanitize_html(text: str) -> str:
    """
    Sanitizes HTML content by escaping unsafe characters.
    """
    return html.escape(text)

def format_json(parsed_response: Union[Dict, List]) -> str:
    """
    Formats a JSON response into HTML.  Handles nested structures.
    """
    formatted_output = ""

    if isinstance(parsed_response, dict):
        # Only include the content of 'answer', not the label
        answer = parsed_response.get("answer", "No answer provided.")
        formatted_output += f"<p>{sanitize_html(str(answer))}</p>"

        # Only include the content of 'action_items', not the label
        action_items = parsed_response.get("action_items", [])
        if isinstance(action_items, list) and action_items:
            formatted_output += "<ul>"
            for item in action_items:
                formatted_output += f"<li>{sanitize_html(str(item))}</li>"
            formatted_output += "</ul>"

    elif isinstance(parsed_response, list):
        formatted_output += "<ul>"
        for item in parsed_response:
            formatted_output += f"<li>{sanitize_html(str(item))}</li>"
        formatted_output += "</ul>"
    else:
        formatted_output += f"<p>{sanitize_html(str(parsed_response))}</p>"

    return formatted_output

def format_plain_text(response_text: str) -> str:
    """
    Formats plain text into HTML, handling paragraphs, bullets, and numbered lists.
    Correctly handles single line breaks and list items at the start of lines.
    """
    response_text = sanitize_html(response_text)
    formatted_output = ""
    in_numbered_list = False
    in_bulleted_list = False

    # Iterate over lines, not paragraphs
    for line in response_text.splitlines():
        line = line.strip()
        if not line:
            if in_numbered_list:  # Close list at the end
                formatted_output += "</ol>"
                in_numbered_list = False
            if in_bulleted_list:
                formatted_output += "</ul>"
                in_bulleted_list = False
            continue

        # Check for numbered list items at the start of the line
        if re.match(r"^\s*\d+\.\s*", line):
            if in_bulleted_list: # Close bullet list.
                formatted_output += "</ul>"
                in_bulleted_list = False
            if not in_numbered_list:  # If not already in a list, start a new one
                formatted_output += "<ol>"
                in_numbered_list = True
            formatted_output += f"<li>{line.lstrip('0123456789. ')}</li>" # Add the <li> tag
        # Check for bullet points at the start of the line.
        elif line.startswith("-") or line.startswith("*"):
            if in_numbered_list:
                formatted_output += "</ol>"
                in_numbered_list = False
            if not in_bulleted_list:
                formatted_output += "<ul>"  # Start a new unordered list
                in_bulleted_list = True
            formatted_output += f"<li>{line.lstrip('-* ')}</li>"  # Add list item
        else:
            # If it's not a list item, close any open list and add as a paragraph
            if in_numbered_list:
                formatted_output += "</ol>"
                in_numbered_list = False
            if in_bulleted_list:
                formatted_output += "</ul>"
                in_bulleted_list = False
            formatted_output += f"<p>{line}</p>"  # Wrap in <p> tags

    # Close any open list tags at the very end
    if in_numbered_list:
        formatted_output += "</ol>"
    if in_bulleted_list:
        formatted_output += "</ul>"

    return formatted_output

def format_llm_response(response_text: str) -> str:
    """
    Formats a raw LLM response into HTML.  Handles JSON (extracting from
    Markdown if necessary) and plain text.  Detects if the input is ALREADY
    HTML and avoids double-encoding.
    """
    if not response_text or not isinstance(response_text, str):
        return "<p>No response provided.</p>"

    try:
        # Check for Markdown code block and extract JSON if present
        match = re.search(r"`json\s*([\s\S]*?)\s*`", response_text)
        if match:
            response_text = match.group(1).strip()  # Extract *just* the JSON

        parsed_response = json.loads(response_text)
        return format_json(parsed_response)  # Use the dedicated JSON formatter

    except json.JSONDecodeError:
        # If it's not JSON, use the plain text formatting
        return format_plain_text(response_text)