from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from models.task import TaskType, TaskStatus


class TaskCreate(BaseModel):
    task_type: TaskType
    parameters: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10)
    assigned_node_id: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    task_id: str
    task_type: TaskType
    status: TaskStatus
    assigned_node_id: Optional[str]
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    priority: int
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
