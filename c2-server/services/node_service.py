from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.node import Node, NodeStatus
from api.schemas.node import NodeRegister, NodeHeartbeat
from core.security import generate_api_key, hash_api_key
from datetime import datetime
import uuid


class NodeService:
    @staticmethod
    async def register_node(db: AsyncSession, node_data: NodeRegister, ip_address: str) -> tuple[Node, str]:
        """Register a new node and return node object with API key"""
        node_id = str(uuid.uuid4())
        api_key = generate_api_key()
        api_key_hash = hash_api_key(api_key)

        new_node = Node(
            node_id=node_id,
            node_type=node_data.node_type,
            device_name=node_data.device_name,
            os_version=node_data.os_version,
            api_level=node_data.api_level,
            model=node_data.model,
            capabilities=node_data.capabilities,
            ip_address=ip_address,
            last_ip=ip_address,
            api_key_hash=api_key_hash,
            status=NodeStatus.ONLINE
        )

        db.add(new_node)
        await db.commit()
        await db.refresh(new_node)

        return new_node, api_key

    @staticmethod
    async def get_node_by_id(db: AsyncSession, node_id: str) -> Node:
        """Get node by node_id"""
        result = await db.execute(select(Node).where(Node.node_id == node_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_heartbeat(db: AsyncSession, node_id: str, heartbeat: NodeHeartbeat, ip_address: str):
        """Update node heartbeat and status"""
        update_data = {
            "last_heartbeat": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "status": heartbeat.status,
            "ip_address": ip_address
        }

        if heartbeat.capabilities:
            update_data["capabilities"] = heartbeat.capabilities

        await db.execute(
            update(Node).where(Node.node_id == node_id).values(**update_data)
        )
        await db.commit()

    @staticmethod
    async def get_all_nodes(db: AsyncSession, status: NodeStatus = None):
        """Get all nodes, optionally filtered by status"""
        query = select(Node)
        if status:
            query = query.where(Node.status == status)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_node_status(db: AsyncSession, node_id: str, status: NodeStatus):
        """Update node status"""
        await db.execute(
            update(Node).where(Node.node_id == node_id).values(status=status)
        )
        await db.commit()
