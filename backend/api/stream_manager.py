import asyncio
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class StreamManager:
    """
    Manages in-memory pub/sub for SSE streaming from background LangGraph tasks.
    Allows the background task to broadcast events, and HTTP endpoints to subscribe.
    """
    def __init__(self):
        # Maps run_id to a list of subscriber queues
        self._channels: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, run_id: str) -> asyncio.Queue:
        """Create a new queue for a run_id and return it."""
        if run_id not in self._channels:
            self._channels[run_id] = []
        q = asyncio.Queue(maxsize=2000)
        self._channels[run_id].append(q)
        return q

    def unsubscribe(self, run_id: str, q: asyncio.Queue):
        """Remove a specific queue from a run_id's channel."""
        if run_id in self._channels:
            if q in self._channels[run_id]:
                self._channels[run_id].remove(q)
            if not self._channels[run_id]:
                del self._channels[run_id]

    async def broadcast(self, run_id: str, event: Any):
        """Broadcast an event to all connected listeners for a run_id."""
        if run_id in self._channels:
            for q in self._channels[run_id]:
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    logger.warning("Queue full for run_id %s, dropping event.", run_id)

stream_manager = StreamManager()
