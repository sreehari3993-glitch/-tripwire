"""
WebSocket Connection Manager for Tripwire Real-Time Live Feed.
Manages active WebSocket connections and thread-safe event broadcasting.
"""
from fastapi import WebSocket
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging

logger = logging.getLogger("tripwire.ws")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    async def connect(self, websocket: WebSocket):
        """Accepts a incoming WebSocket client and records it."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Removes a disconnected client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Asynchronously sends JSON payload to all active clients."""
        if not self.active_connections:
            return

        payload = json.dumps(message)
        dead_connections = []

        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending message to WebSocket client: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    def send_event(self, message: Dict[str, Any]):
        """
        Thread-safe broadcaster. Can be called synchronously from standard FastAPI routes,
        database workers, or asynchronous event loops.
        """
        try:
            target_loop = self.loop
            if target_loop and target_loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast(message), target_loop)
            else:
                # Fallback: try getting running loop
                try:
                    running = asyncio.get_running_loop()
                    if running and running.is_running():
                        asyncio.run_coroutine_threadsafe(self.broadcast(message), running)
                except RuntimeError:
                    pass
        except Exception as e:
            logger.error(f"Failed to dispatch WebSocket event: {e}")


ws_manager = ConnectionManager()
