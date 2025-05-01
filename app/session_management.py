# app/session_management.py
import uuid
import time
from typing import Dict, List, Optional
import warnings # Import the warnings module

from config.settings import settings # For SESSION_TIMEOUT
from app.logger import logger

# --- LangChain Imports ---
# Import base class for type hinting if needed elsewhere, though not strictly required here
# from langchain_core.memory import BaseMemory
# Import the specific memory type we are using
from langchain.memory import ConversationBufferMemory

# --- Suppress specific LangChain Deprecation Warning ---
# This targets the warning specifically related to importing ConversationBufferMemory
# from langchain.memory, allowing the code to run without the warning message
# while acknowledging it might need changes for future LangChain versions.
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning, # LangChainDeprecationWarning inherits from DeprecationWarning
    module="langchain.memory", # Or more specific if possible/needed
    message=".*ConversationBufferMemory.*" # Optional: Be more specific if needed
)
# You could also filter more broadly:
# warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
# but requires importing LangChainDeprecationWarning if possible without circular imports

# --- Import Centralized Models ---
from app.models import UploadedData, DataType

# --- Custom Exception (Optional) ---
class SessionManagementError(Exception):
    """Custom exception for session-related errors (e.g., critical storage failures)."""
    pass

# --- Internal In-Memory Stores ---
# (Keep warning comment about scalability)
session_memory_store: Dict[str, ConversationBufferMemory] = {}
session_data_store: Dict[str, List[UploadedData]] = {}
session_last_activity: Dict[str, float] = {}

# --- Helper for Timeout Cleanup ---
def _cleanup_expired_sessions():
    # (Keep implementation as is - looks correct)
    now = time.time()
    timeout_seconds = settings.SESSION_TIMEOUT
    expired_ids = [
        sid for sid, last_active in list(session_last_activity.items())
        if now - last_active > timeout_seconds
    ]
    if expired_ids:
        logger.info(f"Cleaning up {len(expired_ids)} expired sessions...")
        for sid in expired_ids:
            session_memory_store.pop(sid, None)
            session_data_store.pop(sid, None)
            session_last_activity.pop(sid, None)
            logger.debug(f"Removed expired session: {sid}")

# --- Core Session Functions ---

def get_or_create_session(session_id: Optional[str]) -> str:
    # (Keep implementation as is - looks correct)
    _cleanup_expired_sessions()
    now = time.time()
    timeout_seconds = settings.SESSION_TIMEOUT

    if session_id and session_id in session_memory_store:
        if now - session_last_activity.get(session_id, 0) <= timeout_seconds:
            session_last_activity[session_id] = now
            return session_id
        else:
            logger.warning(f"Session {session_id} expired. Cleaning up.")
            session_memory_store.pop(session_id, None)
            session_data_store.pop(session_id, None)
            session_last_activity.pop(session_id, None)

    new_session_id = str(uuid.uuid4())
    logger.info(f"Creating new session: {new_session_id}")
    # Use the standard memory key "chat_history"
    session_memory_store[new_session_id] = ConversationBufferMemory(
        memory_key="chat_history", # Standard key name
        return_messages=True
    )
    session_data_store[new_session_id] = []
    session_last_activity[new_session_id] = now
    return new_session_id


def get_memory_for_session(session_id: str) -> Optional[ConversationBufferMemory]:
    # (Keep implementation as is - looks correct)
    memory = session_memory_store.get(session_id)
    if not memory:
        logger.error(f"Memory store missing for session '{session_id}'.")
    return memory


def get_data_for_session(session_id: str) -> List[UploadedData]:
    # (Keep implementation as is - looks correct)
    data_list = session_data_store.get(session_id)
    if data_list is None:
        logger.error(f"Data store missing for session '{session_id}'. Returning empty list.")
        return []
    return data_list


def add_data_to_session(session_id: str, data: UploadedData):
    # (Keep implementation as is - looks correct)
    if session_id in session_data_store:
        session_data_store[session_id].append(data)
        session_last_activity[session_id] = time.time()
        logger.debug(f"Added data to session {session_id} (Type: {data.classified_type.value}, Status: {data.processing_status})")
    else:
        logger.error(f"Attempted to add data to non-existent session: {session_id}. Data NOT stored.")