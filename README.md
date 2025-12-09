# ReD-Chain

**Red Team Distributed Chain Infrastructure**

교육 및 포트폴리오 목적의 분산 레드팀 공격 인프라 프로젝트입니다. 여러 안드로이드/iOS 디바이스를 좀비폰처럼 연동하여 분산 작업을 수행하는 C2(Command & Control) 시스템입니다.

## ⚠️ 주의사항

**이 프로젝트는 교육 및 연구 목적으로만 사용되어야 합니다.**

- 본인 소유의 디바이스에서만 사용하세요
- 무단 접근 및 악의적 사용은 법적 책임을 질 수 있습니다
- 모든 테스트는 승인된 환경에서만 수행하세요
- 현지 법률 및 규정을 준수하세요

## 🏗️ 프로젝트 구조

```
ReD-Chain/
├── c2-server/          # Command & Control 서버 (FastAPI)
├── android-agent/      # 안드로이드 에이전트 앱 (계획 중)
├── ios-agent/          # iOS 에이전트 앱 (계획 중)
└── web-dashboard/      # 관리 대시보드 (계획 중)
```

## 🚀 Features

### C2 Server
- ✅ RESTful API 기반 디바이스 관리
- ✅ WebSocket 실시간 통신
- ✅ 안드로이드/iOS 멀티 플랫폼 지원
- ✅ 분산 작업 큐 시스템
- ✅ API Key 기반 인증
- ✅ PostgreSQL + Redis 백엔드
- ✅ Docker 배포 지원

### Planned Features
- 🔄 안드로이드 에이전트 앱
- 🔄 iOS 에이전트 앱
- 🔄 웹 기반 관리 대시보드
- 🔄 분산 포트 스캐닝
- 🔄 프록시 체인
- 🔄 분산 브루트포스
- 🔄 트래픽 생성 및 분석

## 🎯 사용 사례

- 레드팀 훈련 및 시뮬레이션
- 분산 네트워크 테스팅
- 모바일 디바이스 보안 연구
- CTF 및 해킹 대회 인프라
- 포트폴리오 및 기술 학습

## 📖 시작하기

### C2 Server 실행

```bash
cd c2-server

# Docker로 실행 (권장)
docker-compose up -d

# 또는 로컬 실행
pip install -r requirements.txt
python main.py
```

자세한 내용은 [C2 Server README](c2-server/README.md)를 참고하세요.

## 🔧 기술 스택

### Backend (C2 Server)
- Python 3.11+
- FastAPI
- PostgreSQL
- Redis
- WebSocket
- SQLAlchemy
- Docker

### Android Agent (예정)
- Kotlin
- Ktor Client
- WorkManager

### iOS Agent (예정)
- Swift
- URLSession
- Network Extension

## 🌐 아키텍처

```
┌─────────────────────────────────────┐
│     Zombie Phones (Agents)          │
│  ┌──────┐  ┌──────┐  ┌──────┐      │
│  │Android│  │ iOS  │  │Android│     │
│  └───┬──┘  └───┬──┘  └───┬──┘      │
└──────┼─────────┼─────────┼──────────┘
       │         │         │
       └─────────┼─────────┘
                 │
        ┌────────▼────────┐
        │   C2 Server     │
        │  (FastAPI +     │
        │   WebSocket)    │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│PostgreSQL│ │ Redis │   │ Tasks │
└─────────┘ └───────┘   └───────┘
```

## 📚 API 문서

서버 실행 후 자동 생성되는 API 문서:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 기여

이 프로젝트는 교육 목적입니다. 기여를 환영합니다!

## 📝 라이선스

교육 및 연구 목적으로만 사용하세요. 책임감 있게 사용해주세요.

## 👨‍💻 Author

HOHK0923

---

**Remember: With great power comes great responsibility. Use ethically.**
