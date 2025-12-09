from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from api.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from api.dependencies import verify_node_auth
from services.task_service import TaskService
from models.task import TaskStatus
from models.node import Node

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    task = await TaskService.create_task(db, task_data)
    return task


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(
    status: TaskStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks, optionally filtered by status"""
    tasks = await TaskService.get_all_tasks(db, status)
    return tasks


@router.get("/pending", response_model=List[TaskResponse])
async def get_pending_tasks(
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """Get pending tasks for authenticated node"""
    tasks = await TaskService.get_pending_tasks(db, current_node.node_id)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get specific task by ID"""
    task = await TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """Update task status and result (authenticated nodes only)"""
    task = await TaskService.get_task_by_id(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.assigned_node_id != current_node.node_id:
        raise HTTPException(status_code=403, detail="Task not assigned to this node")

    updated_task = await TaskService.update_task(db, task_id, task_update)
    return updated_task


@router.post("/{task_id}/assign/{node_id}", response_model=TaskResponse)
async def assign_task(
    task_id: str,
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Assign a task to a specific node"""
    task = await TaskService.assign_task(db, task_id, node_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
