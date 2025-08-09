import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

class LogManager:
    """In-memory async pub/sub logger for streaming crawl events to clients."""
    def __init__(self):
        self.subscribers: List[asyncio.Queue] = []
        self.buffer: List[Dict[str, Any]] = []  # recent logs buffer
        self.max_buffer = 500

    def _append_buffer(self, event: Dict[str, Any]):
        self.buffer.append(event)
        if len(self.buffer) > self.max_buffer:
            self.buffer.pop(0)

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subscribers.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

    async def publish(self, event: Dict[str, Any]):
        # add timestamp if missing
        event.setdefault("ts", datetime.utcnow().isoformat() + "Z")
        self._append_buffer(event)
        # fan-out (don't await put for each to avoid head-of-line blocking)
        for q in list(self.subscribers):
            try:
                q.put_nowait(event)
            except Exception:
                # drop slow/broken subscribers
                try:
                    self.subscribers.remove(q)
                except ValueError:
                    pass

    def recent(self, n: int = 100) -> List[Dict[str, Any]]:
        return self.buffer[-n:]

log_manager = LogManager()
