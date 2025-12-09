from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import verify_api_key
from services.node_service import NodeService
from models.node import Node


async def verify_node_auth(
    x_api_key: str = Header(...),
    x_node_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> Node:
    """Verify node authentication using API key and node ID"""
    node = await NodeService.get_node_by_id(db, x_node_id)

    if not node:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid node credentials"
        )

    if not verify_api_key(x_api_key, node.api_key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return node
