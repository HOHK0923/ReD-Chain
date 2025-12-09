"""
Advanced Task Scheduling System
Schedule tasks to run at specific times or intervals
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.task import Task, TaskStatus, TaskType
from services.task_service import TaskService
import asyncio


class TaskScheduler:
    """Schedule and manage recurring tasks"""

    def __init__(self):
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.running = False

    async def start(self, db: AsyncSession):
        """Start the scheduler"""
        self.running = True

        while self.running:
            await self.check_scheduled_tasks(db)
            await asyncio.sleep(60)  # Check every minute

    def stop(self):
        """Stop the scheduler"""
        self.running = False

    async def check_scheduled_tasks(self, db: AsyncSession):
        """Check and execute due tasks"""
        now = datetime.utcnow()

        for task_id, scheduled_task in list(self.scheduled_tasks.items()):
            if scheduled_task.next_run <= now:
                # Execute task
                await self.execute_scheduled_task(db, scheduled_task)

                # Update next run time
                if scheduled_task.recurrence:
                    scheduled_task.next_run = now + timedelta(seconds=scheduled_task.interval_seconds)
                else:
                    # One-time task, remove from schedule
                    del self.scheduled_tasks[task_id]

    async def execute_scheduled_task(self, db: AsyncSession, scheduled_task: 'ScheduledTask'):
        """Execute a scheduled task"""
        from api.schemas.task import TaskCreate

        # Create task
        task_data = TaskCreate(
            task_type=scheduled_task.task_type,
            parameters=scheduled_task.parameters,
            priority=scheduled_task.priority,
            assigned_node_id=scheduled_task.assigned_node_id
        )

        await TaskService.create_task(db, task_data)

    def schedule_task(
        self,
        task_type: TaskType,
        parameters: dict,
        schedule_time: datetime = None,
        recurrence: bool = False,
        interval_seconds: int = 3600,
        priority: int = 5,
        assigned_node_id: str = None
    ) -> str:
        """
        Schedule a task

        Args:
            task_type: Type of task
            parameters: Task parameters
            schedule_time: When to run (None = immediate)
            recurrence: Whether task repeats
            interval_seconds: Interval for recurring tasks (default 1 hour)
            priority: Task priority
            assigned_node_id: Specific node to assign

        Returns:
            Scheduled task ID
        """
        import uuid
        task_id = str(uuid.uuid4())

        next_run = schedule_time if schedule_time else datetime.utcnow()

        scheduled_task = ScheduledTask(
            task_id=task_id,
            task_type=task_type,
            parameters=parameters,
            next_run=next_run,
            recurrence=recurrence,
            interval_seconds=interval_seconds,
            priority=priority,
            assigned_node_id=assigned_node_id
        )

        self.scheduled_tasks[task_id] = scheduled_task

        return task_id

    def cancel_scheduled_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            return True
        return False

    def get_scheduled_tasks(self) -> List[dict]:
        """Get all scheduled tasks"""
        return [
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "next_run": task.next_run.isoformat(),
                "recurrence": task.recurrence,
                "interval_seconds": task.interval_seconds if task.recurrence else None
            }
            for task in self.scheduled_tasks.values()
        ]


class ScheduledTask:
    """Represents a scheduled task"""

    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        parameters: dict,
        next_run: datetime,
        recurrence: bool = False,
        interval_seconds: int = 3600,
        priority: int = 5,
        assigned_node_id: str = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.parameters = parameters
        self.next_run = next_run
        self.recurrence = recurrence
        self.interval_seconds = interval_seconds
        self.priority = priority
        self.assigned_node_id = assigned_node_id


# Global scheduler instance
scheduler = TaskScheduler()
