# app/dependencies.py
from contextlib import asynccontextmanager
from app.llm_provider import LLMProvider
from typing import AsyncIterator

@asynccontextmanager
async def get_llm_provider_context() -> AsyncIterator[LLMProvider]:
    """Provides an LLMProvider instance within an async context."""
    llm_provider = LLMProvider()  # Create the instance
    try:
        yield llm_provider
    finally:
        pass  # Add any cleanup here if needed (e.g., closing connections)
