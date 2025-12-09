from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.task import Task, TaskStatus, TaskType
from api.schemas.task import TaskCreate, TaskUpdate
from datetime import datetime
import uuid


class TaskService:
    @staticmethod
    async def create_task(db: AsyncSession, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task_id = str(uuid.uuid4())

        new_task = Task(
            task_id=task_id,
            task_type=task_data.task_type,
            parameters=task_data.parameters,
            priority=task_data.priority,
            assigned_node_id=task_data.assigned_node_id,
            status=TaskStatus.ASSIGNED if task_data.assigned_node_id else TaskStatus.PENDING
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        return new_task

    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: str) -> Task:
        """Get task by task_id"""
        result = await db.execute(select(Task).where(Task.task_id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_pending_tasks(db: AsyncSession, node_id: str = None):
        """Get pending tasks, optionally for a specific node"""
        query = select(Task).where(Task.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED]))

        if node_id:
            query = query.where(Task.assigned_node_id == node_id)

        query = query.order_by(Task.priority.desc(), Task.created_at.asc())

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def assign_task(db: AsyncSession, task_id: str, node_id: str) -> Task:
        """Assign a task to a node"""
        await db.execute(
            update(Task)
            .where(Task.task_id == task_id)
            .values(
                assigned_node_id=node_id,
                status=TaskStatus.ASSIGNED,
                assigned_at=datetime.utcnow()
            )
        )
        await db.commit()

        return await TaskService.get_task_by_id(db, task_id)

    @staticmethod
    async def update_task(db: AsyncSession, task_id: str, task_update: TaskUpdate) -> Task:
        """Update task status and result"""
        update_data = {"status": task_update.status}

        if task_update.status == TaskStatus.RUNNING and not update_data.get("started_at"):
            update_data["started_at"] = datetime.utcnow()

        if task_update.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()

        if task_update.result:
            update_data["result"] = task_update.result

        if task_update.error_message:
            update_data["error_message"] = task_update.error_message

        await db.execute(
            update(Task).where(Task.task_id == task_id).values(**update_data)
        )
        await db.commit()

        return await TaskService.get_task_by_id(db, task_id)

    @staticmethod
    async def get_all_tasks(db: AsyncSession, status: TaskStatus = None):
        """Get all tasks, optionally filtered by status"""
        query = select(Task).order_by(Task.created_at.desc())

        if status:
            query = query.where(Task.status == status)

        result = await db.execute(query)
        return result.scalars().all()
