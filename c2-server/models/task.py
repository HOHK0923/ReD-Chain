from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from core.database import Base


class TaskType(str, enum.Enum):
    PORT_SCAN = "port_scan"
    PROXY_REQUEST = "proxy_request"
    TRAFFIC_GEN = "traffic_gen"
    EXECUTE_COMMAND = "execute_command"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    CUSTOM = "custom"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    # Assignment
    assigned_node_id = Column(String, ForeignKey("nodes.node_id"), nullable=True)

    # Task data
    parameters = Column(JSON, nullable=False)  # Task-specific parameters
    result = Column(JSON, nullable=True)  # Task result
    error_message = Column(Text, nullable=True)

    # Priority and scheduling
    priority = Column(Integer, default=5)  # 1-10, higher = more important

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Metadata
    created_by = Column(String, default="admin")
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
