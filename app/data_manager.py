import json
import os
from app.logger import logger

# Placeholder storage directory
STORAGE_DIR = "data_storage"

def save_analysis(data, storage_type="file"):
    """
    Stores processed analysis results.

    Args:
        data (dict): Processed analysis results.
        storage_type (str): Storage type ("file", "database"). Defaults to "file".

    Returns:
        dict: Confirmation message.
    """
    if not isinstance(data, dict):
        logger.error("Invalid data format for saving.")
        return {"error": "Invalid data format"}

    try:
        if storage_type == "file":
            return _save_to_file(data)
        elif storage_type == "database":
            return _save_to_database(data)
        else:
            return {"error": "Unsupported storage type"}
    except Exception as e:
        logger.error(f"Error saving analysis: {e}", exc_info=True)
        return {"error": "Failed to save data"}

def _save_to_file(data):
    """Stores analysis results in a local JSON file."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    file_path = os.path.join(STORAGE_DIR, "analysis_results.json")

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    return {"message": f"Analysis saved to {file_path}"}

def _save_to_database(data):
    """
    Placeholder for database integration.
    In the future, this will insert analysis results into a database.

    Args:
        data (dict): Processed analysis results.

    Returns:
        dict: Confirmation message.
    """
    # This is a placeholder function. Replace with actual database logic.
    logger.info("Simulated database storage.")
    return {"message": "Analysis saved to database (not implemented yet)."}

