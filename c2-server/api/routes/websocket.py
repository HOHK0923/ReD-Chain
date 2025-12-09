from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.redis_client import get_redis
from services.node_service import NodeService
from models.node import NodeStatus
import json
import asyncio
from typing import Dict

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, node_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[node_id] = websocket

    def disconnect(self, node_id: str):
        if node_id in self.active_connections:
            del self.active_connections[node_id]

    async def send_message(self, node_id: str, message: dict):
        if node_id in self.active_connections:
            websocket = self.active_connections[node_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{node_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    node_id: str,
    api_key: str
):
    """WebSocket endpoint for real-time node communication"""

    # Get database session manually for WebSocket
    async with AsyncSession(bind=websocket.app.state.engine) as db:
        # Verify node
        node = await NodeService.get_node_by_id(db, node_id)

        if not node:
            await websocket.close(code=1008, reason="Invalid node ID")
            return

        # Verify API key
        from core.security import verify_api_key
        if not verify_api_key(api_key, node.api_key_hash):
            await websocket.close(code=1008, reason="Invalid API key")
            return

        # Connect
        await manager.connect(node_id, websocket)
        await NodeService.update_node_status(db, node_id, NodeStatus.ONLINE)

        try:
            # Send welcome message
            await manager.send_message(node_id, {
                "type": "connected",
                "message": f"Connected to C2 server",
                "node_id": node_id
            })

            # Listen for messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "heartbeat":
                    await manager.send_message(node_id, {
                        "type": "heartbeat_ack",
                        "timestamp": message.get("timestamp")
                    })

                elif message.get("type") == "task_update":
                    # Task update from node
                    await manager.send_message(node_id, {
                        "type": "task_update_ack",
                        "task_id": message.get("task_id")
                    })

                elif message.get("type") == "log":
                    # Log message from node
                    print(f"[{node_id}] {message.get('message')}")

        except WebSocketDisconnect:
            manager.disconnect(node_id)
            await NodeService.update_node_status(db, node_id, NodeStatus.OFFLINE)
            print(f"Node {node_id} disconnected")

        except Exception as e:
            print(f"WebSocket error for node {node_id}: {e}")
            manager.disconnect(node_id)
            await NodeService.update_node_status(db, node_id, NodeStatus.ERROR)


@router.get("/api/ws/send/{node_id}")
async def send_to_node(node_id: str, message: str):
    """Send a message to a specific node via WebSocket"""
    await manager.send_message(node_id, {
        "type": "command",
        "message": message
    })
    return {"status": "sent"}
