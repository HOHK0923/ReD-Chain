from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from models.node import Node, NodeStatus
from models.task import Task, TaskStatus, TaskType
from datetime import datetime, timedelta
from typing import Dict, List

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """Get overall statistics"""

    # Count nodes by status
    node_counts = await db.execute(
        select(Node.status, func.count(Node.id))
        .group_by(Node.status)
    )
    nodes_by_status = {status: count for status, count in node_counts}

    # Count tasks by status
    task_counts = await db.execute(
        select(Task.status, func.count(Task.id))
        .group_by(Task.status)
    )
    tasks_by_status = {status: count for status, count in task_counts}

    # Total nodes
    total_nodes = await db.execute(select(func.count(Node.id)))
    total_nodes_count = total_nodes.scalar()

    # Total tasks
    total_tasks = await db.execute(select(func.count(Task.id)))
    total_tasks_count = total_tasks.scalar()

    return {
        "total_nodes": total_nodes_count,
        "total_tasks": total_tasks_count,
        "nodes_by_status": nodes_by_status,
        "tasks_by_status": tasks_by_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/nodes/activity")
async def get_node_activity(hours: int = 24, db: AsyncSession = Depends(get_db)):
    """Get node activity in last N hours"""

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    # Nodes active in timeframe
    result = await db.execute(
        select(Node)
        .where(Node.last_seen >= cutoff_time)
    )
    active_nodes = result.scalars().all()

    return {
        "timeframe_hours": hours,
        "active_nodes": len(active_nodes),
        "nodes": [
            {
                "node_id": node.node_id,
                "node_type": node.node_type,
                "last_seen": node.last_seen.isoformat(),
                "tasks_completed": node.total_tasks_completed
            }
            for node in active_nodes
        ]
    }


@router.get("/tasks/performance")
async def get_task_performance(db: AsyncSession = Depends(get_db)):
    """Get task performance metrics"""

    # Tasks by type
    task_type_counts = await db.execute(
        select(Task.task_type, func.count(Task.id))
        .group_by(Task.task_type)
    )
    tasks_by_type = {task_type: count for task_type, count in task_type_counts}

    # Success rate
    completed = await db.execute(
        select(func.count(Task.id))
        .where(Task.status == TaskStatus.COMPLETED)
    )
    failed = await db.execute(
        select(func.count(Task.id))
        .where(Task.status == TaskStatus.FAILED)
    )

    completed_count = completed.scalar() or 0
    failed_count = failed.scalar() or 0
    total = completed_count + failed_count

    success_rate = (completed_count / total * 100) if total > 0 else 0

    return {
        "tasks_by_type": tasks_by_type,
        "completed": completed_count,
        "failed": failed_count,
        "success_rate": round(success_rate, 2)
    }


@router.get("/network/coverage")
async def get_network_coverage(db: AsyncSession = Depends(get_db)):
    """Get network coverage (which networks we have access to)"""

    # Get all online nodes
    result = await db.execute(
        select(Node)
        .where(Node.status == NodeStatus.ONLINE)
    )
    nodes = result.scalars().all()

    # Group by IP prefix (assume /24 networks)
    networks = {}
    for node in nodes:
        if node.ip_address:
            prefix = '.'.join(node.ip_address.split('.')[:3])
            if prefix not in networks:
                networks[prefix] = []
            networks[prefix].append({
                "node_id": node.node_id,
                "node_type": node.node_type,
                "ip": node.ip_address
            })

    return {
        "total_networks": len(networks),
        "total_online_nodes": len(nodes),
        "networks": networks
    }
