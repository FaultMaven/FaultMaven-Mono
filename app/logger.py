# app/logger.py
import logging
import sys

# 1. Get the specific logger instance
logger = logging.getLogger("FaultMaven")

# 2. Set the desired level for this specific logger
#    Set to DEBUG to see all messages during testing/debugging
#    Set to INFO or WARNING for production
logger.setLevel(logging.DEBUG)

# 3. Prevent messages from propagating to the root logger
#    This avoids potential duplicate messages if root is also configured,
#    and isolates this logger's configuration.
logger.propagate = False

# 4. Configure a handler (e.g., StreamHandler to print to console/stderr)
#    Check if handlers already exist to avoid adding duplicates on re-import
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout) # Output to standard out

    # 5. Set the handler's level (optional, defaults to NOTSET, handles all messages from logger)
    # handler.setLevel(logging.DEBUG) # Usually not needed if logger level is set

    # 6. Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)' # Added filename/line
    )

    # 7. Set the formatter for the handler
    handler.setFormatter(formatter)

    # 8. Add the handler to the logger
    logger.addHandler(handler)

# Optional: Add other handlers like FileHandler here if needed
# file_handler = logging.FileHandler("faultmaven.log")
# file_handler.setLevel(logging.INFO) # Log INFO and above to file
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)