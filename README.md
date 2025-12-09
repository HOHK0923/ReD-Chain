# ReD-Chain

> 분산 모바일 디바이스 기반 레드팀 인프라 연구 프로젝트

안드로이드/iOS 디바이스를 활용한 분산 C2(Command & Control) 인프라입니다.
실제 공격자들이 사용하는 봇넷 아키텍처를 연구하고, 방어 전략을 수립하기 위한 교육용 프로젝트입니다.

## 📌 프로젝트 배경

최근 모바일 봇넷을 이용한 공격이 증가하고 있습니다 (Mirai, Mozi 등).
이 프로젝트는 다음을 목표로 합니다:

- 모바일 봇넷의 작동 원리 이해
- 분산 공격 인프라 아키텍처 연구
- 레드팀 시뮬레이션 환경 구축
- 방어 메커니즘 개발을 위한 테스트베드

## ⚠️ 법적 고지사항

**이 프로젝트는 교육 및 연구 목적으로만 개발되었습니다.**

- 본인 소유의 디바이스와 네트워크에서만 사용하십시오
- 무단으로 타인의 시스템에 접근하는 것은 불법입니다
- 모든 테스트는 격리된 환경에서 수행하십시오
- 저는 이 코드의 오용에 대한 책임을 지지 않습니다

## 🎯 핵심 기능

### 구현 완료
- **C2 서버** (Python/FastAPI)
  - RESTful API + WebSocket 실시간 통신
  - 안드로이드/iOS 멀티 플랫폼 지원
  - PostgreSQL + Redis 백엔드
  - 작업 큐 및 분산 처리
  - 암호화 통신 (Fernet)
  - 로깅 및 모니터링

- **안드로이드 에이전트** (Kotlin)
  - 백그라운드 서비스 (재부팅 시 자동 시작)
  - 분산 포트 스캔
  - HTTP 트래픽 생성
  - 네트워크 발견 (피버팅)
  - 은닉 기능 (아이콘 숨김, 에뮬레이터 감지)
  - 화면 캡처 및 원격 제어 (개발 중)

- **iOS 에이전트** (Swift)
  - Background Fetch
  - HTTP 트래픽 생성
  - Jailbreak/디버거 감지
  - 제한적 기능 (iOS 샌드박스)

- **CLI 도구**
  - Commander - 좀비폰 제어 인터페이스
  - Remote Viewer - 화면 미러링 (개발 중)

### 공격 시나리오
- 분산 포트 스캔
- HTTP Flood (DDoS 시뮬레이션)
- 네트워크 피버팅 (내부망 접근)
- 프록시 체인
- 명령 실행
- 원격 제어 및 모니터링

## 🏗️ 아키텍처

```
┌─────────────────────────────────────┐
│       Zombie Phones (Agents)        │
│   [Android]  [iOS]  [Android]       │
└──────────────┬──────────────────────┘
               │ REST/WebSocket
               │ (암호화 통신)
    ┌──────────▼───────────┐
    │   C2 Server (AWS)    │
    │   - FastAPI          │
    │   - PostgreSQL       │
    │   - Redis            │
    └──────────┬───────────┘
               │
    ┌──────────▼──────────┐
    │  CLI Commander      │
    │  (로컬 관리)         │
    └─────────────────────┘
```

## 🚀 빠른 시작

### 1. C2 서버 배포

```bash
# 저장소 클론
git clone https://github.com/HOHK0923/ReD-Chain.git
cd ReD-Chain/c2-server

# 환경 변수 설정
cp .env.example .env
nano .env  # SECRET_KEY, API_KEY_SALT 변경 필수

# Docker로 실행
docker-compose up -d

# 서버 확인
curl http://localhost:8000/health
```

### 2. 안드로이드 에이전트 빌드

```bash
cd android-agent

# C2 서버 URL 수정
# C2Client.kt 파일에서 baseUrl 변경

# Android Studio로 빌드 또는
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 3. CLI Commander 실행

```bash
cd c2-server/cli
pip install -r requirements.txt
python3 commander.py
```

## 📊 사용 예시

### 분산 포트 스캔
```bash
# Commander 실행 후
3. Port Scan Attack
Target: 192.168.1.0/24
Ports: 1-1000
Broadcast: Yes

→ 모든 온라인 좀비폰이 동시에 스캔 수행
→ 결과는 C2 서버에 집계
```

### 네트워크 피버팅
```
핸드폰이 WiFi에 연결되면
→ 해당 WiFi의 내부 네트워크 스캔
→ 발견된 호스트 정보 C2에 전송
→ 핸드폰을 경유하여 내부망 접근 가능
```

## 🔧 기술 스택

| 컴포넌트 | 기술 |
|---------|------|
| C2 Server | Python 3.11, FastAPI, SQLAlchemy, Redis |
| Database | PostgreSQL, Redis |
| Android Agent | Kotlin, OkHttp, WorkManager |
| iOS Agent | Swift, URLSession |
| Deployment | Docker, AWS EC2/RDS/ElastiCache |
| Security | Fernet 암호화, API Key 인증 |

## 📁 프로젝트 구조

```
ReD-Chain/
├── c2-server/              # C2 서버
│   ├── api/                # REST API 엔드포인트
│   ├── core/               # 설정, DB, 보안
│   ├── models/             # 데이터베이스 모델
│   ├── services/           # 비즈니스 로직
│   ├── cli/                # CLI 도구
│   └── modules/            # 공격 모듈
├── android-agent/          # 안드로이드 앱
│   └── app/src/main/java/
│       └── com/redchain/agent/
│           ├── service/    # 백그라운드 서비스
│           ├── network/    # C2 통신
│           └── modules/    # 공격 모듈
└── ios-agent/              # iOS 앱
    └── RedChainAgent/Sources/
```

## 🛡️ 보안 기능

- **통신 암호화**: Fernet (AES-128)
- **인증**: API Key 기반
- **은닉**:
  - 앱 아이콘 숨김 (Android)
  - 에뮬레이터 감지
  - 디버거 감지
- **안티-포렌식**:
  - 랜덤 통신 딜레이
  - 로그 자동 삭제 (개발 중)

## 📚 참고 문서

- [AWS 배포 가이드](c2-server/deploy-aws.md)
- [Android 빌드 가이드](android-agent/README.md)
- [iOS 빌드 가이드](ios-agent/README.md)
- [API 문서](http://localhost:8000/docs) (서버 실행 후)

## 🎓 학습 자료

이 프로젝트를 통해 배울 수 있는 것:
- C2 프레임워크 아키텍처 (Cobalt Strike, Metasploit 유사)
- 분산 시스템 설계
- 모바일 앱 백그라운드 처리
- 네트워크 보안 및 침투 테스트
- RESTful API + WebSocket 설계
- Docker 배포 및 인프라 관리

## 🔍 알려진 제한사항

- iOS는 백그라운드 제약으로 기능 제한적
- 에뮬레이터 감지는 우회 가능
- 암호화는 기본적인 수준 (프로덕션 부적합)
- 일부 기능은 루팅/탈옥 필요

## 🚧 향후 계획

- [ ] SOCKS5 프록시 구현
- [ ] 실시간 화면 스트리밍
- [ ] 웹 기반 대시보드
- [ ] 더 정교한 은닉 기술
- [ ] 도메인 프론팅
- [ ] DNS 터널링

## 💼 포트폴리오 하이라이트

**이 프로젝트에서 다룬 기술:**

✅ **백엔드 개발**: FastAPI로 확장 가능한 C2 서버 구축
✅ **모바일 개발**: Android(Kotlin), iOS(Swift) 네이티브 앱 개발
✅ **네트워크 프로그래밍**: WebSocket, REST API, 비동기 통신
✅ **데이터베이스**: PostgreSQL + Redis, SQLAlchemy ORM
✅ **보안**: 암호화, 인증, 난독화, 안티-분석
✅ **인프라**: Docker, AWS EC2/RDS, CI/CD
✅ **분산 시스템**: 작업 큐, 부하 분산, 상태 관리

## 📧 연락처

프로젝트 관련 문의: [GitHub Issues](https://github.com/HOHK0923/ReD-Chain/issues)

---

**⚖️ 윤리적 사용**: 이 프로젝트는 사이버 보안 연구와 방어 전략 개발을 위한 것입니다. 악의적으로 사용하지 마십시오.

**🎯 채용 담당자분께**: 이 프로젝트는 레드팀 운영, 침투 테스트, 보안 연구 역량을 보여주기 위한 포트폴리오입니다. 실제 운영 환경에서는 사용되지 않았으며, 모든 테스트는 개인 소유 디바이스에서 수행되었습니다.
