from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.node_service import NodeService
from typing import Dict
import json
import base64

router = APIRouter(prefix="/api/remote", tags=["remote_control"])


class RemoteControlManager:
    """Manage remote control sessions for phones"""

    def __init__(self):
        # Map of node_id -> control WebSocket
        self.control_sessions: Dict[str, WebSocket] = {}
        # Map of node_id -> viewer WebSocket
        self.viewer_sessions: Dict[str, WebSocket] = {}

    async def connect_control(self, node_id: str, websocket: WebSocket):
        """Phone connects for remote control"""
        await websocket.accept()
        self.control_sessions[node_id] = websocket

    async def connect_viewer(self, node_id: str, websocket: WebSocket):
        """Operator connects to view/control phone"""
        await websocket.accept()
        self.viewer_sessions[node_id] = websocket

    def disconnect_control(self, node_id: str):
        if node_id in self.control_sessions:
            del self.control_sessions[node_id]

    def disconnect_viewer(self, node_id: str):
        if node_id in self.viewer_sessions:
            del self.viewer_sessions[node_id]

    async def send_to_phone(self, node_id: str, message: dict):
        """Send command to phone"""
        if node_id in self.control_sessions:
            await self.control_sessions[node_id].send_json(message)

    async def send_to_viewer(self, node_id: str, message: dict):
        """Send data to viewer (screen, events, etc)"""
        if node_id in self.viewer_sessions:
            await self.viewer_sessions[node_id].send_json(message)


manager = RemoteControlManager()


@router.websocket("/control/phone/{node_id}")
async def phone_control_endpoint(
    websocket: WebSocket,
    node_id: str,
    api_key: str
):
    """
    WebSocket endpoint for phone to receive remote control commands
    Phone connects here and waits for commands
    """
    # TODO: Verify api_key

    await manager.connect_control(node_id, websocket)

    try:
        while True:
            # Wait for commands from operator
            data = await websocket.receive_text()
            message = json.loads(data)

            # Phone reports back (screenshot, touch response, etc)
            if message.get("type") == "screenshot":
                # Forward screenshot to viewer
                await manager.send_to_viewer(node_id, message)

            elif message.get("type") == "event":
                # Forward event to viewer
                await manager.send_to_viewer(node_id, message)

    except WebSocketDisconnect:
        manager.disconnect_control(node_id)


@router.websocket("/control/viewer/{node_id}")
async def viewer_endpoint(
    websocket: WebSocket,
    node_id: str
):
    """
    WebSocket endpoint for operator to view/control phone
    Operator connects here to send commands and receive screen updates
    """
    await manager.connect_viewer(node_id, websocket)

    try:
        while True:
            # Receive commands from operator
            data = await websocket.receive_text()
            message = json.loads(data)

            # Forward command to phone
            if message.get("type") == "touch":
                # Touch event: {type: "touch", x: 100, y: 200}
                await manager.send_to_phone(node_id, message)

            elif message.get("type") == "key":
                # Key press: {type: "key", key: "back"}
                await manager.send_to_phone(node_id, message)

            elif message.get("type") == "screenshot":
                # Request screenshot
                await manager.send_to_phone(node_id, {"type": "get_screenshot"})

            elif message.get("type") == "swipe":
                # Swipe gesture
                await manager.send_to_phone(node_id, message)

    except WebSocketDisconnect:
        manager.disconnect_viewer(node_id)


@router.get("/control/sessions")
async def get_active_sessions():
    """Get list of active remote control sessions"""
    return {
        "active_phones": list(manager.control_sessions.keys()),
        "active_viewers": list(manager.viewer_sessions.keys())
    }
