# iOS Agent

좀비폰 인프라용 iOS 에이전트 앱

## 기능

- ✅ C2 서버 자동 등록
- ✅ Background Fetch
- ✅ HTTP 트래픽 생성
- ⚠️ 포트 스캔 (제한적 - iOS 샌드박스)
- 🔄 프록시/VPN (Network Extension 필요)

## iOS 제약사항

iOS는 안드로이드보다 백그라운드 실행에 제약이 많습니다:

- 백그라운드 앱은 최대 15분마다 깨어남
- 포트 스캔 등 raw socket 사용 제한
- VPN/Network Extension은 별도 인증 필요
- Jailbreak 없이는 기능 제한적

## 빌드 방법

### Xcode 사용

1. Xcode로 `ios-agent` 폴더 열기
2. C2 서버 URL 수정:
   - `C2Manager.swift`에서 `baseURL` 변경
3. Signing & Capabilities 설정
   - Background Modes: Fetch, Processing
4. 실제 iOS 기기에 설치 (시뮬레이터는 백그라운드 제한)

### 필요한 Capabilities

- Background Modes
  - Background fetch
  - Background processing
- Network (기본 포함)

## 배포 옵션

### 1. TestFlight (권장)

- App Store Connect에 업로드
- 테스터 초대
- 90일간 사용 가능

### 2. Ad-Hoc 배포

- UDID 등록 필요
- 최대 100대 기기
- 프로비저닝 프로파일 필요

### 3. Enterprise Distribution

- Apple Developer Enterprise 계정 필요 ($299/년)
- 무제한 기기
- 사내 배포 전용

### 4. Jailbreak

- Cydia로 설치
- 모든 제약 해제
- 불안정할 수 있음

## 설정

### C2 서버 URL 변경

`Sources/C2Manager.swift`:

```swift
private let baseURL = "http://YOUR_C2_SERVER_IP:8000"
```

## 사용법

1. Xcode로 앱 빌드 및 설치
2. 앱 실행
3. 백그라운드로 전환
4. iOS가 주기적으로 앱을 깨워 작업 수행

## 주의사항

- iOS 백그라운드는 안드로이드만큼 신뢰성 높지 않음
- 배터리 세이빙 모드에서는 백그라운드 제한
- 앱 강제 종료 시 재시작 안 됨 (재부팅 후도)
- 프로덕션에서는 HTTPS 필수

## 개발 TODO

- [ ] Network Extension으로 VPN/프록시
- [ ] URL Session Background Configuration
- [ ] Push Notification으로 원격 깨우기
- [ ] 로컬 네트워크 스캔 (Bonjour)
- [ ] iCloud 동기화로 설정 백업
