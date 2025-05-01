# app/mcp_processor.py
"""
Module responsible for interacting with the external MCP (Module Context Protocol) server.
"""

import asyncio
from typing import Dict, Any, Optional
import aiohttp # Import the async HTTP client library

from app.logger import logger
from config.settings import settings # To get the MCP server URL

# Define a timeout for requests to the MCP server (in seconds)
MCP_REQUEST_TIMEOUT = 30 # Adjust as needed

async def process_mcp_data(content: str) -> Dict[str, Any]:
    """
    Sends data content to the configured MCP server and returns the processed results.

    Args:
        content: The string data content classified as MCP type.

    Returns:
        A dictionary containing the processed results from the MCP server,
        or a dictionary with an 'error' key if processing fails.

    Raises:
        ValueError: If MCP_SERVER_URL is not configured in settings.
    """
    mcp_url = settings.mcp_server_url
    if not mcp_url:
        logger.error("MCP_SERVER_URL is not configured in settings. Cannot process MCP data.")
        # Raising an error might be better to signal configuration issue clearly
        raise ValueError("MCP Server URL is not configured.")
        # Or return error dict: return {"error": "MCP Server URL not configured."}


    # Convert HttpUrl object to string for aiohttp
    mcp_url_str = str(mcp_url)
    logger.info(f"Sending data to MCP server at {mcp_url_str}...")

    # --- Prepare request ---
    # Assumption: MCP server expects a POST request with JSON payload like {"data": "..."}
    # Adjust the method, payload structure, headers based on the actual MCP server API spec.
    payload = {"data": content}
    headers = {"Content-Type": "application/json"}

    try:
        # Create an async HTTP client session
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=MCP_REQUEST_TIMEOUT)) as session:
            # Make the asynchronous POST request
            async with session.post(mcp_url_str, json=payload, headers=headers) as response:
                # Check for HTTP errors (4xx, 5xx)
                response.raise_for_status() # Raises ClientResponseError for bad statuses

                # Parse the JSON response from the MCP server
                # Assumption: MCP server returns a JSON dictionary with results
                results: Dict[str, Any] = await response.json()
                logger.info(f"Successfully received results from MCP server for data snippet: '{content[:50]}...'")
                logger.debug(f"MCP Server Results: {results}")
                return results

    except aiohttp.ClientConnectorError as e:
        logger.error(f"Connection Error connecting to MCP server at {mcp_url_str}: {e}")
        return {"error": f"Could not connect to MCP server: {e}"}
    except asyncio.TimeoutError:
        logger.error(f"Request timed out connecting to MCP server at {mcp_url_str} after {MCP_REQUEST_TIMEOUT}s.")
        return {"error": f"Request timed out connecting to MCP server."}
    except aiohttp.ClientResponseError as e:
        # Handle HTTP errors reported by the server
        logger.error(f"MCP server returned HTTP error: {e.status} {e.message} for URL {mcp_url_str}")
        try:
             error_detail = await e.text() # Try to get error detail from response body
        except Exception:
             error_detail = "(Could not read error detail)"
        return {"error": f"MCP server returned error {e.status}: {e.message}", "detail": error_detail}
    except aiohttp.ContentTypeError as e:
         logger.error(f"MCP server response was not valid JSON from {mcp_url_str}: {e}")
         return {"error": f"MCP server returned non-JSON response: {e}"}
    except Exception as e:
        # Catch any other unexpected errors
        logger.exception(f"An unexpected error occurred while processing MCP data via {mcp_url_str}: {e}")
        return {"error": f"An unexpected error occurred during MCP processing: {e}"}