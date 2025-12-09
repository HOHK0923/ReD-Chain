from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from models.node import NodeType, NodeStatus


class NodeRegister(BaseModel):
    node_type: NodeType
    device_name: str
    os_version: str
    api_level: Optional[int] = None
    model: str
    capabilities: Dict = Field(default_factory=dict)


class NodeResponse(BaseModel):
    id: int
    node_id: str
    node_type: NodeType
    status: NodeStatus
    device_name: str
    os_version: str
    model: str
    ip_address: Optional[str]
    last_seen: datetime
    total_tasks_completed: int
    total_tasks_failed: int

    class Config:
        from_attributes = True


class NodeHeartbeat(BaseModel):
    status: NodeStatus
    capabilities: Optional[Dict] = None
