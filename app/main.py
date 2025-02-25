import uvicorn
import sys
import os
import signal

# Ensure Python recognizes /app
sys.path.insert(0, "/app")

from app.api import app

def shutdown_handler(signum, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, workers=4)
