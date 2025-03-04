import uvicorn
import sys
import os
import signal

# Ensure Python recognizes the correct module path
sys.path.insert(0, "/fmv")

from app.query_processing import app

def shutdown_handler(signum, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == "__main__":
    uvicorn.run("app.query_processing:app", host="0.0.0.0", port=8000, workers=4)
