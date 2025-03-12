import uuid
import time
from typing import Dict, List, Any, Optional
from config.settings import settings  # Import settings
from app.logger import logger

def create_session(sessions: Dict[str, Dict[str, Any]]) -> str:
    """Creates a new session and returns the session ID.

    Args:
        sessions: The dictionary containing all sessions.

    Returns:
        The newly created session ID.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"history": [], "data": [], "last_activity": time.time()}
    logger.debug(f"Created new session: {session_id}")
    return session_id

def get_session_data(session_id: str, sessions: Dict[str, Dict[str, Any]], session_timeout: int) -> Optional[Dict[str, Any]]:
    """Retrieves session data by ID, handling timeouts. Returns None if invalid.

    Args:
        session_id: The ID of the session.
        sessions:  The dictionary containing all sessions.
        session_timeout: The session timeout in seconds

    Returns:
        The session data (dict) if the session exists and is not expired,
        otherwise None.

    """
    session = sessions.get(session_id)
    if session:
        if time.time() - session["last_activity"] < session_timeout:
            session["last_activity"] = time.time()  # Update last activity
            logger.debug(f"Retrieved session data for: {session_id}")
            return session
        else:
            # Session expired
            del sessions[session_id]
            logger.info(f"Session expired and deleted: {session_id}")
    logger.debug(f"Session not found: {session_id}")
    return None
def delete_session(session_id: str, sessions: Dict[str, Dict[str, Any]]) -> bool:
    """Deletes a session by its ID.

    Args:
        session_id (str): The ID of the session to be deleted.
        sessions (Dict[str, Dict[str, Any]]): The dictionary containing all sessions.

    Returns:
        bool: True if the session was deleted, False if the session was not found.
    """
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Session explicitly deleted: {session_id}")
        return True
    logger.debug(f"Attempted to delete non-existent session: {session_id}")
    return False