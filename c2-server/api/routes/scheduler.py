from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.task_scheduler import scheduler
from models.task import TaskType
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/scheduler", tags=["task_scheduler"])


class ScheduleTaskRequest(BaseModel):
    task_type: TaskType
    parameters: dict
    schedule_time: Optional[datetime] = None
    recurrence: bool = False
    interval_seconds: int = 3600
    priority: int = 5
    assigned_node_id: Optional[str] = None


@router.post("/schedule")
async def schedule_task(
    request: ScheduleTaskRequest,
    db: AsyncSession = Depends(get_db)
):
    """Schedule a task to run at specific time or interval"""

    task_id = scheduler.schedule_task(
        task_type=request.task_type,
        parameters=request.parameters,
        schedule_time=request.schedule_time,
        recurrence=request.recurrence,
        interval_seconds=request.interval_seconds,
        priority=request.priority,
        assigned_node_id=request.assigned_node_id
    )

    return {
        "scheduled_task_id": task_id,
        "message": "Task scheduled successfully",
        "recurrence": request.recurrence,
        "next_run": request.schedule_time.isoformat() if request.schedule_time else "immediate"
    }


@router.get("/scheduled")
async def get_scheduled_tasks():
    """Get all scheduled tasks"""
    tasks = scheduler.get_scheduled_tasks()

    return {
        "total_scheduled": len(tasks),
        "tasks": tasks
    }


@router.delete("/scheduled/{task_id}")
async def cancel_scheduled_task(task_id: str):
    """Cancel a scheduled task"""
    success = scheduler.cancel_scheduled_task(task_id)

    if success:
        return {"message": "Scheduled task cancelled"}
    else:
        return {"error": "Scheduled task not found"}, 404
