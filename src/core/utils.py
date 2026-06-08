"""Utility functions and helper modules."""

import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar("T")


async def run_async_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Run a sync function in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, *kwargs.values())
