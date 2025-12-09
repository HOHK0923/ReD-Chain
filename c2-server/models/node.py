from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, JSON
from datetime import datetime
import enum
from core.database import Base


class NodeType(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"


class NodeStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, unique=True, index=True, nullable=False)
    node_type = Column(Enum(NodeType), nullable=False)
    status = Column(Enum(NodeStatus), default=NodeStatus.OFFLINE)

    # Device info
    device_name = Column(String)
    os_version = Column(String)
    api_level = Column(Integer, nullable=True)  # Android only
    model = Column(String)

    # Network info
    ip_address = Column(String)
    last_ip = Column(String)

    # Capabilities
    capabilities = Column(JSON, default={})  # {"port_scan": True, "proxy": True, etc}

    # Authentication
    api_key_hash = Column(String, nullable=False)

    # Timestamps
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)

    # Metrics
    total_tasks_completed = Column(Integer, default=0)
    total_tasks_failed = Column(Integer, default=0)
