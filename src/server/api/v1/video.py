from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from src.server.core.websocket_manager import manager
from src.server.core.security import verify_access_token

websocket_router = APIRouter()

@websocket_router.websocket("/stream/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: str, 
    token: str = Query(...)
):
    # Authenticate the connection via JWT
    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=4003)
        return

    # Connect to the room
    await manager.connect(websocket, room_id)
    
    try:
        while True:
            # Main signaling event loop
            data = await websocket.receive_json()
            event_type = data.get("type")
            
            # Broadcast the signal to the other participant
            if event_type in ["join", "offer", "answer", "ice-candidate", "media-toggle"]:
                await manager.broadcast_to_room(data, room_id, exclude_socket=websocket)
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, room_id)
