from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, key: str, websocket: WebSocket):
        await websocket.accept()
        self.connections.setdefault(key, []).append(websocket)

    def disconnect(self, key: str, websocket: WebSocket):
        self.connections[key].remove(websocket)
        if not self.connections[key]:
            del self.connections[key]

    async def broadcast(self, key: str, message: dict):
        for ws in self.connections.get(key, []):
            await ws.send_json(message)

manager = ConnectionManager()
