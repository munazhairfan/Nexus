from fastapi import WebSocket
from typing import Dict, List

class VideoSignalingManager:
    def __init__(self):
        # Maps room_id to a list of connected WebSockets
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
        
        # Enforce 1-on-1 private call integrity
        if len(self.active_rooms[room_id]) >= 2:
            await websocket.close(code=4001, reason="Room Full")
            return

        self.active_rooms[room_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            
            # Clean up empty rooms to avoid memory bloat
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]

    async def broadcast_to_room(self, message: dict, room_id: str, exclude_socket: WebSocket = None):
        if room_id in self.active_rooms:
            for connection in self.active_rooms[room_id]:
                if connection != exclude_socket:
                    await connection.send_json(message)

# Global signaling manager instance
manager = VideoSignalingManager()
