from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from api.dependencies import verify_node_auth
from models.node import Node
from pydantic import BaseModel

router = APIRouter(prefix="/api/pivot", tags=["pivoting"])


class PivotScanRequest(BaseModel):
    internal_target: str
    ports: List[int]


class NetworkDiscoveryRequest(BaseModel):
    scan_type: str = "arp"  # arp, ping, etc


class TunnelRequest(BaseModel):
    target_ip: str
    target_port: int
    tunnel_type: str = "socks5"  # socks5, http, tcp


@router.post("/discover")
async def discover_network(
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """
    네트워크 탐색 (폰이 연결된 WiFi의 다른 기기들 찾기)

    폰이 연결된 WiFi 네트워크에서 다른 기기들을 찾습니다.
    같은 네트워크의 PC, 프린터, 라우터 등을 발견할 수 있습니다.

    **사용 시나리오:**
    1. 집/회사 WiFi에 연결된 내 폰 사용
    2. 이 API로 같은 WiFi의 다른 기기들 탐색
    3. 발견된 기기들에 대한 추가 조사 가능

    **응답:** 발견된 기기 목록 (IP, MAC 주소, 제조사 등)
    """
    # Node will execute network discovery and report back
    return {
        "status": "discovery_started",
        "node_id": current_node.node_id,
        "message": "Network discovery initiated"
    }


@router.post("/scan-internal")
async def pivot_scan(
    scan_req: PivotScanRequest,
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """
    Use authenticated node to scan internal network target
    Node acts as pivot point
    """
    # Create task for node to scan internal network
    return {
        "status": "pivot_scan_started",
        "node_id": current_node.node_id,
        "target": scan_req.internal_target,
        "ports": scan_req.ports
    }


@router.post("/tunnel/create")
async def create_tunnel(
    tunnel_req: TunnelRequest,
    current_node: Node = Depends(verify_node_auth),
    db: AsyncSession = Depends(get_db)
):
    """
    Create tunnel through node to access internal resource
    C2 -> Node -> Internal Target
    """
    # Setup tunnel configuration
    return {
        "status": "tunnel_created",
        "node_id": current_node.node_id,
        "tunnel_id": f"tunnel_{current_node.node_id[:8]}",
        "local_port": 9050,  # Local port to connect to
        "target": f"{tunnel_req.target_ip}:{tunnel_req.target_port}"
    }


@router.get("/routes")
async def get_pivot_routes(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all available pivot routes
    Shows which internal networks are accessible through which nodes
    """
    # TODO: query stored network discovery results
    return {
        "routes": [
            # Example structure:
            # {
            #     "node_id": "xxx",
            #     "node_name": "Galaxy S21",
            #     "network": "192.168.1.0/24",
            #     "gateway": "192.168.1.1",
            #     "accessible_hosts": ["192.168.1.100", "192.168.1.101"]
            # }
        ]
    }
