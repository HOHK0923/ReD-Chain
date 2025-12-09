from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from api.schemas.node import NodeRegister, NodeResponse, NodeHeartbeat
from api.dependencies import verify_node_auth
from services.node_service import NodeService
from models.node import Node, NodeStatus

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


@router.post("/register", response_model=dict)
async def register_node(
    node_data: NodeRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new node and receive API key"""
    ip_address = request.client.host

    node, api_key = await NodeService.register_node(db, node_data, ip_address)

    return {
        "node_id": node.node_id,
        "api_key": api_key,
        "message": "Node registered successfully"
    }


@router.post("/heartbeat")
async def heartbeat(
    heartbeat_data: NodeHeartbeat,
    request: Request,
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """Update node heartbeat"""
    ip_address = request.client.host

    await NodeService.update_heartbeat(
        db,
        current_node.node_id,
        heartbeat_data,
        ip_address
    )

    return {"status": "ok", "message": "Heartbeat updated"}


@router.get("/", response_model=List[NodeResponse])
async def get_all_nodes(
    status: NodeStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all registered nodes"""
    nodes = await NodeService.get_all_nodes(db, status)
    return nodes


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific node by ID"""
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node
